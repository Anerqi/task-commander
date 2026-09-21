#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan-skills.py - scan skills, dedupe by name, and filter candidates

Standard-library-only script (Python 3.10+): read one or more scan root
directories, parse the simple YAML frontmatter fields needed for skill
discovery, dedupe by skill name, score the entries against the query terms,
and print the surviving candidates as JSON.

- Flags: --query-terms; --max-results (1-500, default 30); --roots;
  --output-path; --host (all by default); --project-root (cwd by default).
- Discovery: HOST_PROFILES declares candidate paths, not host availability.
  Project paths are collected nearest-first up to the Git worktree top or
  filesystem root, then user paths, then selected compatibility paths.
  Nonempty --roots replaces discovery entirely; an empty --roots retains
  the legacy automatic-discovery behavior. Pi's .pi/skills is local to the
  discovery start; its shared .agents/skills follows ancestor discovery.
  PI_CODING_AGENT_DIR overrides the Pi user configuration base.
  Only existing directories are scanned; realpath/normcase deduplication
  also prevents cycles when following skill-directory symlinks.
  This does not reproduce host permissions or conflict-resolution rules,
  read host configuration, or execute plugins.
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


# Ordered candidates only: directory existence does not imply host availability.
# Keep native paths before compatibility paths within each scope.
HOST_PROFILES = {
    'codex': {
        'project': ('.agents/skills',),
        'user': ('.agents/skills',),
    },
    'opencode': {
        'project': ('.opencode/skills', '.agents/skills', '.claude/skills'),
        'user': ('.config/opencode/skills', '.agents/skills', '.claude/skills'),
    },
    'claude-code': {
        'project': ('.claude/skills',),
        'user': ('.claude/skills',),
    },
    'cursor': {
        'project': ('.cursor/skills', '.agents/skills', '.claude/skills', '.codex/skills'),
        'user': ('.cursor/skills', '.agents/skills', '.claude/skills', '.codex/skills'),
    },
    'copilot': {
        'project': ('.github/skills', '.claude/skills', '.agents/skills'),
        'user': ('.copilot/skills', '.agents/skills'),
    },
    'pi': {
        'project': ('.pi/skills', '.agents/skills'),
        'user': ('.pi/agent/skills', '.agents/skills'),
    },
}
# Preserve the previous shared-path ordering in all mode.
ALL_HOST_ORDER = ('opencode', 'codex', 'claude-code', 'cursor', 'copilot', 'pi')
CODEX_COMPAT_PATHS = (
    'skills',
    'plugins/cache/openai-curated',
    'plugins/cache/openai-bundled',
    'plugins/cache/openai-curated-remote',
)


def path_key(path):
    return os.path.normcase(os.path.realpath(path))


def existing_unique_roots(candidates):
    """Keep existing directories once, in first-occurrence order."""
    roots = []
    seen = set()
    for candidate in candidates:
        if not candidate.strip() or not os.path.isdir(candidate):
            continue
        real = os.path.realpath(candidate)
        key = path_key(real)
        if key not in seen:
            seen.add(key)
            roots.append(real)
    return roots


def project_root_type(text):
    if not text.strip() or not os.path.isdir(text):
        raise argparse.ArgumentTypeError('must be an existing directory')
    return os.path.realpath(text)


def default_roots(host='all', project_root=None):
    """Discover ordered project, user, and compatibility roots for a profile.

    --project-root, not the script installation directory, anchors Git and
    ancestor discovery. Configuration files and extra plugin roots are not read;
    callers can supply --roots for any additional directories.
    """
    import subprocess

    current = project_root_type(os.getcwd() if project_root is None else project_root)
    start = current
    hosts = ALL_HOST_ORDER if host == 'all' else (host,)
    paths = {
        scope: tuple(dict.fromkeys(
            path for selected in hosts for path in HOST_PROFILES[selected][scope]))
        for scope in ('project', 'user')
    }
    roots = []
    worktree_top = None
    try:
        probe = subprocess.run(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=current,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            encoding='utf-8',
            errors='replace',
            check=False,
            timeout=10)
        if probe.returncode == 0 and probe.stdout.strip():
            worktree_top = path_key(probe.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        pass
    while True:
        roots.extend(os.path.join(current, path) for path in paths['project']
                     if path != '.pi/skills' or current == start)
        if worktree_top is not None and path_key(current) == worktree_top:
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    home = os.path.expanduser('~')
    for path in paths['user']:
        if path == '.pi/agent/skills':
            pi_home = os.environ.get('PI_CODING_AGENT_DIR') or os.path.join(home, '.pi', 'agent')
            roots.append(os.path.join(pi_home, 'skills'))
        else:
            roots.append(os.path.join(home, path))
    if 'codex' in hosts:
        codex_home = os.environ.get('CODEX_HOME') or os.path.join(home, '.codex')
        roots.extend(os.path.join(codex_home, path) for path in CODEX_COMPAT_PATHS)
    return existing_unique_roots(roots)


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


def find_skill_files(root, seen_dirs=None, seen_files=None):
    """Follow directory symlinks safely, skipping inaccessible directories.

    Shared visited sets avoid rescanning aliases and overlapping scan roots.
    Filenames are matched case-insensitively; traversal is sorted.
    """
    if seen_dirs is None:
        seen_dirs = set()
    if seen_files is None:
        seen_files = set()
    matches = []
    for dirpath, dirnames, filenames in os.walk(
            root, followlinks=True, onerror=lambda _err: None):
        key = path_key(dirpath)
        if key in seen_dirs:
            dirnames[:] = []
            continue
        seen_dirs.add(key)
        dirnames.sort()
        filenames.sort()
        for filename in filenames:
            if filename.lower() == 'skill.md':
                path = os.path.realpath(os.path.join(dirpath, filename))
                key = path_key(path)
                if key not in seen_files:
                    seen_files.add(key)
                    matches.append(path)
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
                        help='nonempty explicit roots replace discovery (including home); '
                             'omitted or empty uses automatic discovery')
    parser.add_argument('--host', choices=('all', *HOST_PROFILES), default='all',
                        help='candidate path profile, not host availability (default all)')
    parser.add_argument('--project-root', type=project_root_type, default=os.getcwd(),
                        metavar='DIR', help='existing discovery starting directory (default cwd)')
    parser.add_argument('--output-path', default=None, metavar='FILE',
                        help='JSON output file path; prints to stdout when omitted')
    args = parser.parse_args()

    if args.roots:
        roots = existing_unique_roots(args.roots)
    else:
        roots = default_roots(args.host, args.project_root)

    by_name = {}   # insertion order is scan order; the first-scanned root wins (root_priority)
    seen_dirs = set()
    seen_files = set()
    root_index = 0
    for root in roots:
        for skill_file in find_skill_files(root, seen_dirs, seen_files):
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
