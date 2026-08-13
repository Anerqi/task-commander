#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan-skills.py - scan skills, dedupe by name, and filter candidates

Standard-library-only script (Python 3.10+): read one or more scan root
directories, parse the simple YAML frontmatter fields needed for skill
discovery, dedupe by skill name, score the entries against the query terms,
and print the surviving candidates as JSON.

- Flags: --query-terms (one or more query terms); --max-results (1-500,
  default 30); --roots (one or more scan root directories); --output-path.
- Default scan roots (runtime discovery): when --roots is omitted, the
  roots are discovered at runtime; no absolute path is hard-coded.
  Project-level skill directories (.opencode/skills, .agents/skills,
  .claude/skills) are collected walking upward from the current working
  directory, stopping at the filesystem root or at the git worktree top
  when git reports one. User-level directories under the home directory
  follow (~/.config/opencode/skills, ~/.agents/skills, ~/.claude/skills),
  then the Codex directories under CODEX_HOME (defaults to ~/.codex):
  skills plus the three plugins/cache directories. Only existing
  directories are scanned, and each real path is scanned once.
- Frontmatter parsing: read line by line; the first line must be '---';
  at most 200 lines are parsed; keys are lower-cased; quotes are stripped;
  '>' '|' '>-' '|-' count as empty values; indented continuation lines are
  joined with a space; files without a name key are skipped.
- Dedupe: by name after stripping leading/trailing whitespace and
  lower-casing; the first-scanned root wins (root_priority); later
  duplicates are recorded in duplicate_paths.
- Scoring: exact name match 12, substring match 8, description substring
  +3, accumulated per query term; entries with no query terms or a score
  above 0 become candidates.
- Sort and truncation: score descending, name ascending (case-insensitive),
  keep the first max-results entries.
- Output: UTF-8 without BOM. Files written via --output-path use LF line
  endings; stdout text uses the platform's default newline translation.
  JSON is pretty-printed with indent=2 for readability; the output is not
  byte-aligned with any other tool.
"""

import argparse
import datetime
import json
import os
import re
import sys


def default_roots():
    """Discover default scan roots at runtime; no path is hard-coded.

    Project level: walk upward from the current working directory,
    collecting the .opencode/skills, .agents/skills, and .claude/skills
    directories that exist at each level; stop at the filesystem root, or
    at the git worktree top when git is available and reports one.
    User level: ~/.config/opencode/skills, ~/.agents/skills, and
    ~/.claude/skills under the home directory. Codex: the skills directory
    under CODEX_HOME (defaults to ~/.codex) and the three plugins/cache
    directories, when they exist.
    Only existing directories are returned; after resolving to real paths
    each directory is kept once.
    """
    import subprocess

    home = os.path.expanduser('~')

    roots = []

    # Project level: nearest directories first
    worktree_top = None
    try:
        probe = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace',
            check=False,
            timeout=10)
        if probe.returncode == 0 and probe.stdout.strip():
            worktree_top = os.path.realpath(probe.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    current = os.path.abspath(os.getcwd())
    while True:
        for name in ('.opencode', '.agents', '.claude'):
            candidate = os.path.join(current, name, 'skills')
            if os.path.isdir(candidate):
                roots.append(candidate)
        if worktree_top is not None and os.path.realpath(current) == worktree_top:
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # User level
    for name in ('.config/opencode', '.agents', '.claude'):
        candidate = os.path.join(home, name, 'skills')
        if os.path.isdir(candidate):
            roots.append(candidate)

    # Codex
    codex_home = os.environ.get('CODEX_HOME') or os.path.join(home, '.codex')
    for relative in ('skills',
                     os.path.join('plugins', 'cache', 'openai-curated'),
                     os.path.join('plugins', 'cache', 'openai-bundled'),
                     os.path.join('plugins', 'cache', 'openai-curated-remote')):
        candidate = os.path.join(codex_home, relative)
        if os.path.isdir(candidate):
            roots.append(candidate)

    # Dedupe after resolving real paths
    unique_roots = []
    seen = set()
    for root in roots:
        real = os.path.realpath(root)
        if real not in seen:
            seen.add(real)
            unique_roots.append(real)
    return unique_roots


def parse_frontmatter(path):
    """
    Return (name, description, disable_model_invocation); None when no legal
    name key exists. Reads as UTF-8 with BOM stripped; invalid bytes are
    replaced. File read errors are raised.
    """
    metadata = {}          # keys are lower-cased
    current_key = None     # most recent key, for joining continuation lines
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as reader:
        first_line = reader.readline().rstrip('\r\n')
        if first_line != '---':
            return None

        # Read only frontmatter and cap work at 200 physical lines, including
        # the opening delimiter. The Skill body is never loaded.
        for line_count, source_line in enumerate(reader, start=2):
            if line_count > 200:
                break
            raw_line = source_line.rstrip('\r\n')
            if raw_line == '---':
                break

            key_match = re.match(r'^([A-Za-z0-9_-]+):\s*(.*)$', raw_line)
            if key_match:
                key = key_match.group(1).lower()
                value = key_match.group(2).strip().strip('"').strip("'")
                if value in ('>', '|', '>-', '|-'):   # block scalar indicators count as empty
                    value = ''
                metadata[key] = value
                current_key = key
                continue

            continuation = re.match(r'^\s+(.+)$', raw_line)
            if continuation and current_key is not None:
                value = continuation.group(1).strip().strip('"').strip("'")
                if value:
                    existing = metadata[current_key]
                    if existing.strip():
                        metadata[current_key] = existing + ' ' + value
                    else:
                        metadata[current_key] = value
            else:
                current_key = None

    if 'name' not in metadata:
        return None
    return (
        str(metadata['name']),
        str(metadata.get('description', '')),
        str(metadata.get('disable-model-invocation', '')),
    )


def find_skill_files(root):
    """
    Recursively scan a directory for SKILL.md files; filename comparison is
    case-insensitive so files are not missed on case-sensitive platforms.
    Directories that cannot be accessed are skipped silently.
    """
    matches = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=lambda _err: None):
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename.lower() == 'skill.md':
                matches.append(os.path.join(dirpath, filename))
    return matches


def max_results_type(text):
    """Valid range 1-500; out-of-range values raise an argument error."""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError('not a valid integer') from None
    if value < 1 or value > 500:
        raise argparse.ArgumentTypeError('must be in the range 1-500')
    return value


def main():
    # When stdout is piped or redirected, the platform default code page
    # (e.g. GBK) garbles non-ASCII output; reconfigure both streams to
    # UTF-8 up front (aligned with the UTF-8 output principle in runtime.md;
    # this also keeps argparse --help text UTF-8).
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description='Scan directories for skills: parse frontmatter, dedupe by name, '
                    'and filter candidates')
    parser.add_argument('--query-terms', nargs='*', default=[], metavar='TERM',
                        help='one or more query terms; with no terms, return all candidates')
    parser.add_argument('--max-results', type=max_results_type, default=30, metavar='N',
                        help='upper bound on returned candidates, 1-500 (default 30)')
    parser.add_argument('--roots', nargs='*', default=[], metavar='DIR',
                        help='one or more scan root directories; defaults to '
                             'runtime-discovered roots')
    parser.add_argument('--output-path', default=None, metavar='FILE',
                        help='JSON output file path; prints to stdout when omitted')
    args = parser.parse_args()

    if args.roots:
        candidate_roots = args.roots
    else:
        candidate_roots = default_roots()

    # Keep only existing directories and resolve them to real paths; skip empty strings
    roots = [
        os.path.realpath(root)
        for root in candidate_roots
        if root.strip() and os.path.isdir(root)
    ]

    by_name = {}   # insertion order is scan order; the first-scanned root wins (root_priority)
    root_index = 0
    for root in roots:
        for skill_file in find_skill_files(root):
            frontmatter = parse_frontmatter(skill_file)
            if frontmatter is None:
                continue
            name, description, disable_model_invocation = frontmatter
            key = name.strip().lower()
            if not key:
                continue
            if key not in by_name:
                by_name[key] = {
                    'name': name.strip(),
                    'description': description.strip(),
                    'path': skill_file,
                    'root_priority': root_index,
                    'disable_model_invocation': disable_model_invocation.strip(),
                    'duplicate_paths': [],
                }
            else:
                by_name[key]['duplicate_paths'].append(skill_file)
        root_index += 1

    # Query terms: strip whitespace, lower-case, dedupe preserving first-occurrence order
    normalized_terms = []
    for term in args.query_terms:
        normalized = term.strip().lower()
        if normalized and normalized not in normalized_terms:
            normalized_terms.append(normalized)

    results = []
    for entry in by_name.values():
        name_lower = entry['name'].lower()
        description_lower = entry['description'].lower()
        score = 0
        matched_terms = []
        for term in normalized_terms:
            term_score = 0
            if name_lower == term:
                term_score = 12
            elif term in name_lower:
                term_score = 8
            if term in description_lower:
                term_score += 3
            if term_score > 0:
                score += term_score
                matched_terms.append(term)
        if not normalized_terms or score > 0:
            results.append({
                'name': entry['name'],
                'description': entry['description'],
                'path': entry['path'],
                'score': score,
                'matched_terms': matched_terms,
                'disable_model_invocation': entry['disable_model_invocation'],
                'duplicate_paths': entry['duplicate_paths'],
            })

    # Sort by score descending, then name ascending (case-insensitive); keep the
    # first max-results entries
    results.sort(key=lambda item: (-item['score'], item['name'].lower()))
    results = results[:args.max_results]

    payload = {
        'generated_at': datetime.datetime.now().astimezone().isoformat(),
        # ISO-8601 timestamp with timezone (microsecond precision may vary)
        'roots': roots,
        'query_terms': normalized_terms,
        'unique_skills_scanned': len(by_name),
        'candidates_returned': len(results),
        'candidates': results,
    }
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + '\n'

    if args.output_path:
        full_output_path = os.path.abspath(args.output_path)
        parent = os.path.dirname(full_output_path)
        if parent and not os.path.isdir(parent):
            os.makedirs(parent, exist_ok=True)   # create missing parent directories
        # UTF-8 without BOM, LF line endings
        with open(full_output_path, 'w', encoding='utf-8', newline='\n') as out:
            out.write(json_text)
    else:
        sys.stdout.write(json_text)


if __name__ == '__main__':
    main()
