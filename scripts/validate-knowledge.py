#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-knowledge.py - validate the optional project knowledge layer

Standard-library-only script (Python 3.10+); it never imports PyYAML.

Layout checked under the project root:

    knowledge/
      LOG.md                  # optional; expected when topics exist
      ROADMAP.md              # optional
      topics/<topic>.md       # optional; YAML frontmatter required
      Cited.md                # optional

- Flags: --project-root (default '.'); --knowledge-dir (default 'knowledge');
  --require (turn a missing knowledge directory into an error instead of a
  warning). The layer is optional for existing and small projects.
- LOG.md: level-2 entries "## YYYY-MM-DD <separator> <title>" with the
  separator one of '·', '—', '-', ':'. Dates must be ISO and non-increasing
  (newest first); ascending dates are an error. Missing titles, entry bodies
  over 20 non-empty lines, and a LOG without dated entries are warnings.
- topics/*.md: a frontmatter block delimited by '---' on the first line and a
  later '---' line. The line parser supports "key: value", "key: [a, b]",
  "key: []", quoted values, blank lines, and full-line or whitespace-prefixed
  inline comments. Duplicate keys and lines without ':' are errors. Required
  fields: type, status, summary, tags, contains, created, updated,
  authoring_mode. Enumerations, date order, kebab-case filenames, empty
  contains lists, long summaries, and empty topic shells are also checked;
  the latter four are warnings. Markdown link targets are not validated.
- ROADMAP.md: a non-empty file should contain a "**Current focus**" line.
- Cited.md: a non-empty file should contain a Markdown table header or at
  least one non-comment content line.
- Encoding: invalid UTF-8 is an error; a BOM or CRLF line endings produce
  warnings because project text files are UTF-8 without BOM and LF.
- Output: one UTF-8 JSON object with valid / project_root / knowledge_dir /
  log_present / topic_count / errors / warnings, pretty-printed with
  ensure_ascii=False. project_root is resolved; knowledge_dir echoes the
  configured directory name; topic_count includes topic files that failed
  validation. Exit 0 when valid, 1 otherwise; --help exits 0. Argparse usage
  errors (for example an unknown flag) conventionally exit 2 with usage text
  and are outside this JSON contract.

Conservative interpretations where the schema leaves room:
- LOG.md stays optional even when topics exist: a missing LOG.md is a
  warning, never a hard error. --require only affects the knowledge directory.
- A duplicate frontmatter block is reported only when a second '---' block
  starts immediately after the first closing delimiter (blank lines allowed)
  and its contents look like frontmatter; Markdown horizontal rules in the
  body are not treated as a second block.
- Only files whose names end in lowercase '.md' directly under topics/ count
  as topic files. Nested files and other extensions are ignored.
- Frontmatter keys are compared exactly (case-sensitive); enum values and
  required field names are the lowercase literals in the protocol.
- Inline comments start with '#' preceded by whitespace outside quotes; a
  '#' without preceding whitespace (for example inside a quoted value or in
  "[#tag]") is literal.
- LOG entry bodies end at the next level-2 heading; "non-empty" means a line
  with non-whitespace content, including HTML comments.
- Topic body content excludes blank lines, Markdown heading lines, and HTML
  comments (including multi-line comments) for the empty-shell warning.
"""

import argparse
import datetime
import json
import os
import re
import sys


ISO_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
LOG_HEADING_RE = re.compile(
    r'^\s{0,3}##[ \t]+(\d{4}-\d{2}-\d{2})(?=$|[ \t·—:\-])(.*)$')
LOG_DATE_LIKE_RE = re.compile(
    r'^\s{0,3}##[ \t]+(\d{4}[-/.]\d{1,3}[-/.]\d{1,3})(?=$|[ \t·—:\-])')
LOG_H2_RE = re.compile(r'^\s{0,3}##[ \t]')
FENCE_RE = re.compile(r'^(`{3,}|~{3,})')
HEADING_RE = re.compile(r'^#{1,6}\s')
KEBAB_FILENAME_RE = re.compile(r'^[a-z0-9][a-z0-9-]*\.md$')
KNOWN_FRONTMATTER_KEYS = frozenset({
    'type', 'status', 'summary', 'tags', 'contains', 'created', 'updated',
    'related', 'authoring_mode', 'graduation_status', 'contributors',
})
MAX_FILE_BYTES = 2 * 1024 * 1024

TOPIC_TYPES = ('project_topic',)
TOPIC_STATUSES = ('active', 'superseded', 'archived', 'needs_review')
CONTAINS_KINDS = ('decision', 'experience', 'lesson', 'procedure',
                  'reference', 'open_question')
AUTHORING_MODES = ('ai_generated', 'human_written', 'ai_assisted')
GRADUATION_STATUSES = ('candidate', 'deferred', 'not_applicable')
REQUIRED_TOPIC_FIELDS = (
    'type', 'status', 'summary', 'tags', 'contains', 'created', 'updated',
    'authoring_mode',
)
ENTRY_LINE_LIMIT = 20
SUMMARY_LENGTH_LIMIT = 200


def inspect_encoding(path, label, errors, warnings):
    """Flag invalid UTF-8/BOM/CRLF/oversize; return False when the file is unusable."""
    try:
        size = os.path.getsize(path)
        if size > MAX_FILE_BYTES:
            errors.append(label + ': file is too large for a knowledge note ('
                          + str(size) + ' bytes; limit ' + str(MAX_FILE_BYTES) + ')')
            return False
        with open(path, 'rb') as reader:
            raw = reader.read()
    except OSError as exc:
        errors.append(label + ': cannot read file: ' + str(exc))
        return False
    if raw.startswith(b'\xef\xbb\xbf'):
        warnings.append(label + ': UTF-8 BOM present (project files use UTF-8 without BOM)')
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError:
        errors.append(label + ': invalid UTF-8')
        return False
    if b'\r\n' in raw:
        warnings.append(label + ': CRLF line endings present (project files use LF)')
    return True


def read_text(path):
    """Read a text file as UTF-8 (BOM stripped, bad bytes replaced)."""
    with open(path, 'r', encoding='utf-8-sig', errors='replace') as reader:
        return reader.read()


def parse_iso_date(value):
    """Return a date for an ISO YYYY-MM-DD string, or None."""
    if not ISO_DATE_RE.match(value):
        return None
    try:
        return datetime.date.fromisoformat(value)
    except ValueError:
        return None


def strip_inline_comment(value):
    """Remove a whitespace-prefixed '#' comment that is outside quotes."""
    quote = None
    for index, character in enumerate(value):
        if quote is not None:
            if character == quote:
                quote = None
        elif character in ('"', "'"):
            quote = character
        elif character == '#' and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
    return value.strip()


def unquote(value):
    """Drop one pair of matching surrounding quotes; no escape decoding."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_flow_list(value):
    """Parse '[a, b]' / '[]'; return None when the value is not a flow list."""
    value = value.strip()
    if not (value.startswith('[') and value.endswith(']')):
        return None
    inner = value[1:-1].strip()
    if not inner:
        return []
    items = []
    current = []
    quote = None
    for character in inner:
        if quote is not None:
            current.append(character)
            if character == quote:
                quote = None
        elif character in ('"', "'"):
            quote = character
            current.append(character)
        elif character == ',':
            items.append(''.join(current).strip())
            current = []
        else:
            current.append(character)
    items.append(''.join(current).strip())
    return [unquote(item) for item in items]


def looks_like_frontmatter(lines):
    """True when the candidate looks like a real topic frontmatter block.

    Requiring at least two required keys avoids treating an ordinary Markdown
    horizontal rule plus prose such as "type: this is prose" as a second block.
    """
    saw_key = False
    required_keys = 0
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' not in stripped:
            return False
        key = stripped.split(':', 1)[0].strip()
        if not key or key not in KNOWN_FRONTMATTER_KEYS:
            return False
        if key in REQUIRED_TOPIC_FIELDS:
            required_keys += 1
        saw_key = True
    return saw_key and required_keys >= 2


def extract_frontmatter(lines, label, errors):
    """Split a topic file into frontmatter lines and body lines.

    Returns (frontmatter_lines, body_lines); frontmatter_lines is None when
    the block is missing or unclosed.
    """
    if not lines or lines[0].strip() != '---':
        errors.append(label + ': missing frontmatter block '
                      '(the first line must be ---)')
        return None, lines

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == '---':
            closing_index = index
            break
    if closing_index is None:
        errors.append(label + ': unclosed frontmatter block '
                      '(no closing --- line)')
        return None, []

    # A second block immediately after the first one is duplicate
    # frontmatter; a later horizontal rule is not.
    next_index = closing_index + 1
    while next_index < len(lines) and not lines[next_index].strip():
        next_index += 1
    if next_index < len(lines) and lines[next_index].strip() == '---':
        second_closing = None
        for index in range(next_index + 1, len(lines)):
            if lines[index].strip() == '---':
                second_closing = index
                break
        if (second_closing is not None
                and looks_like_frontmatter(lines[next_index + 1:second_closing])):
            errors.append(label + ': duplicate frontmatter block')

    return lines[1:closing_index], lines[closing_index + 1:]


def parse_frontmatter(lines, label, errors):
    """Parse the small supported YAML subset into a key -> raw value dict."""
    fields = {}
    for index, raw_line in enumerate(lines, start=2):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' not in stripped:
            errors.append(label + ': malformed frontmatter line ' + str(index)
                          + ': expected "key: value"')
            continue
        key, raw_value = stripped.split(':', 1)
        key = key.strip()
        if not key:
            errors.append(label + ': malformed frontmatter line ' + str(index)
                          + ': empty key')
            continue
        if key in fields:
            errors.append(label + ': duplicate frontmatter key: ' + key)
            continue
        fields[key] = strip_inline_comment(raw_value)
    return fields


def body_has_content(body_lines):
    """True when the body has content beyond headings and HTML comments."""
    in_comment = False
    for raw_line in body_lines:
        stripped = raw_line.strip()
        if in_comment:
            if '-->' in stripped:
                in_comment = False
                stripped = stripped.split('-->', 1)[1].strip()
                if stripped and not HEADING_RE.match(stripped):
                    return True
            continue
        while stripped.startswith('<!--'):
            if '-->' not in stripped:
                in_comment = True
                stripped = ''
                break
            stripped = stripped.split('-->', 1)[1].strip()
        if not stripped or HEADING_RE.match(stripped):
            continue
        return True
    return False


def fence_mask(lines):
    """Return True for lines inside fenced code blocks (including fences)."""
    mask = []
    in_fence = False
    fence_char = None
    fence_len = 0
    for line in lines:
        match = FENCE_RE.match(line.strip())
        if match:
            marker = match.group(1)
            char = marker[0]
            length = len(marker)
            if not in_fence:
                in_fence = True
                fence_char = char
                fence_len = length
            elif char == fence_char and length >= fence_len:
                in_fence = False
                fence_char = None
                fence_len = 0
            mask.append(True)
            continue
        mask.append(in_fence)
    return mask


def validate_log(content, errors, warnings):
    """Validate LOG.md ordering, entry titles, and entry body length."""
    lines = content.splitlines()
    fenced = fence_mask(lines)
    entries = []
    for index, line in enumerate(lines):
        if fenced[index]:
            continue
        heading = LOG_HEADING_RE.match(line)
        if not heading:
            date_like = LOG_DATE_LIKE_RE.match(line)
            if date_like:
                errors.append('LOG.md: invalid entry date (expected ISO '
                              'YYYY-MM-DD): ' + date_like.group(1))
            continue
        raw_date = heading.group(1)
        entry_date = parse_iso_date(raw_date)
        if entry_date is None:
            errors.append('LOG.md: invalid entry date (expected ISO YYYY-MM-DD): '
                          + raw_date)
            continue
        rest = heading.group(2)
        title = ''
        if rest.strip():
            stripped_rest = rest.strip()
            if stripped_rest[0] in '·—:-':
                title = stripped_rest[1:].strip()
            else:
                warnings.append('LOG.md: malformed entry heading (expected '
                                '"## YYYY-MM-DD · title"): ' + line.strip())
                title = stripped_rest
        if not title:
            warnings.append('LOG.md: entry ' + raw_date + ' has no title')
        entries.append((index, entry_date, raw_date))

    previous_date = None
    for index, entry_date, raw_date in entries:
        if previous_date is not None and entry_date > previous_date:
            errors.append('LOG.md: dates must be newest-first; ' + raw_date
                          + ' appears after ' + previous_date.isoformat())
        previous_date = entry_date

        body_end = len(lines)
        for later_index in range(index + 1, len(lines)):
            if not fenced[later_index] and LOG_H2_RE.match(lines[later_index]):
                body_end = later_index
                break
        non_empty_lines = sum(1 for line in lines[index + 1:body_end]
                              if line.strip())
        if non_empty_lines > ENTRY_LINE_LIMIT:
            warnings.append('LOG.md: entry ' + raw_date + ' has '
                            + str(non_empty_lines) + ' non-empty body lines '
                            '(limit ' + str(ENTRY_LINE_LIMIT) + ')')

    if not entries:
        warnings.append('LOG.md: no dated entries found (expected '
                        '"## YYYY-MM-DD · title" headings)')


def validate_topic(path, name, display_name, errors, warnings):
    """Validate one topics/*.md file and return its parsed fields."""
    label = 'topics/' + display_name
    if not inspect_encoding(path, label, errors, warnings):
        return None
    lines = read_text(path).splitlines()
    frontmatter_lines, body_lines = extract_frontmatter(lines, label, errors)
    if frontmatter_lines is None:
        return None

    fields = parse_frontmatter(frontmatter_lines, label, errors)
    for field in REQUIRED_TOPIC_FIELDS:
        if field not in fields:
            errors.append(label + ': missing required field: ' + field)

    if 'type' in fields:
        topic_type = unquote(fields['type'])
        if topic_type not in TOPIC_TYPES:
            errors.append(label + ': invalid type: ' + topic_type
                          + ' (expected project_topic)')

    if 'status' in fields:
        status = unquote(fields['status'])
        if status not in TOPIC_STATUSES:
            errors.append(label + ': invalid status: ' + status
                          + ' (expected one of '
                          + ', '.join(TOPIC_STATUSES) + ')')

    if 'summary' in fields:
        summary = unquote(fields['summary']).strip()
        if not summary:
            errors.append(label + ': summary must be non-empty')
        elif len(summary) > SUMMARY_LENGTH_LIMIT:
            warnings.append(label + ': summary exceeds '
                            + str(SUMMARY_LENGTH_LIMIT) + ' characters ('
                            + str(len(summary)) + ')')

    if 'tags' in fields:
        tags = parse_flow_list(fields['tags'])
        if tags is None:
            errors.append(label + ': tags must be a flow list such as '
                          '[a, b] or []')
        elif any(not tag for tag in tags):
            errors.append(label + ': tags must not contain empty items')

    if 'contains' in fields:
        contains = parse_flow_list(fields['contains'])
        if contains is None:
            errors.append(label + ': contains must be a flow list such as '
                          '[lesson, procedure] or []')
        else:
            if not contains:
                warnings.append(label + ': contains is empty')
            for kind in contains:
                if not kind:
                    errors.append(label + ': contains must not contain empty items')
                elif kind not in CONTAINS_KINDS:
                    errors.append(label + ': invalid contains value: ' + kind
                                  + ' (expected one of '
                                  + ', '.join(CONTAINS_KINDS) + ')')

    created_date = None
    updated_date = None
    if 'created' in fields:
        created_date = parse_iso_date(unquote(fields['created']))
        if created_date is None:
            errors.append(label + ': invalid created date: '
                          + unquote(fields['created']))
    if 'updated' in fields:
        updated_date = parse_iso_date(unquote(fields['updated']))
        if updated_date is None:
            errors.append(label + ': invalid updated date: '
                          + unquote(fields['updated']))
    if (created_date is not None and updated_date is not None
            and updated_date < created_date):
        errors.append(label + ': updated date ' + updated_date.isoformat()
                      + ' is earlier than created date '
                      + created_date.isoformat())

    if 'authoring_mode' in fields:
        authoring_mode = unquote(fields['authoring_mode'])
        if authoring_mode not in AUTHORING_MODES:
            errors.append(label + ': invalid authoring_mode: ' + authoring_mode
                          + ' (expected one of '
                          + ', '.join(AUTHORING_MODES) + ')')

    if 'graduation_status' in fields:
        graduation_status = unquote(fields['graduation_status'])
        if graduation_status not in GRADUATION_STATUSES:
            errors.append(label + ': invalid graduation_status: '
                          + graduation_status + ' (expected one of '
                          + ', '.join(GRADUATION_STATUSES) + ')')

    if not KEBAB_FILENAME_RE.match(name):
        warnings.append(label + ': filename is not kebab-case '
                        '(expected lowercase letters, digits, and hyphens)')

    if not body_has_content(body_lines):
        warnings.append(label + ': empty topic shell (no body content beyond '
                        'a title or comments)')

    return fields


def validate_roadmap(path, errors, warnings):
    """A non-empty roadmap should state the current focus."""
    if not inspect_encoding(path, 'ROADMAP.md', errors, warnings):
        return
    content = read_text(path)
    if not content.strip():
        return
    if not any(line.lstrip().startswith('**Current focus**')
               for line in content.splitlines()):
        warnings.append('ROADMAP.md: non-empty roadmap has no '
                        '"**Current focus**" line')


def commented_content_lines(content):
    """Yield stripped non-comment lines, dropping HTML comment blocks."""
    in_comment = False
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if in_comment:
            if '-->' in stripped:
                in_comment = False
                stripped = stripped.split('-->', 1)[1].strip()
            else:
                continue
        while stripped.startswith('<!--'):
            if '-->' not in stripped:
                in_comment = True
                stripped = ''
                break
            stripped = stripped.split('-->', 1)[1].strip()
        if stripped:
            yield stripped


def validate_cited(path, errors, warnings):
    """A non-empty citation file needs a table header or real content."""
    if not inspect_encoding(path, 'Cited.md', errors, warnings):
        return
    content = read_text(path)
    if not content.strip():
        return
    lines = list(commented_content_lines(content))
    has_table = any(line.startswith('|') for line in lines)
    has_content = any(not HEADING_RE.match(line) for line in lines)
    if not (has_table or has_content):
        warnings.append('Cited.md: non-empty citation file has no Markdown '
                        'table header or content line')


def safe_display_name(name):
    """Return a printable label for a possibly non-UTF-8 filename."""
    try:
        return os.fsencode(name).decode('utf-8', 'replace')
    except Exception:
        return repr(name)


def is_within(root, path):
    """True when path resolves under root (used to reject directory junctions)."""
    try:
        common = os.path.commonpath([os.path.realpath(root), os.path.realpath(path)])
    except ValueError:
        return False
    return os.path.normcase(common) == os.path.normcase(os.path.realpath(root))


def main():
    # When stdout is piped or redirected, the platform default code page
    # (e.g. GBK) garbles non-ASCII output; reconfigure both streams to
    # UTF-8 up front (this also keeps argparse --help text UTF-8).
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')

    parser = argparse.ArgumentParser(
        description='Validate the optional project knowledge layer: LOG.md '
                    'ordering, topic frontmatter, ROADMAP.md focus, and '
                    'Cited.md content. Output is JSON.')
    parser.add_argument('--project-root', default='.', metavar='DIR',
                        help="project root to inspect (default: '.')")
    parser.add_argument('--knowledge-dir', default='knowledge', metavar='NAME',
                        help="knowledge directory name under the project root "
                             "(default: 'knowledge')")
    parser.add_argument('--require', action='store_true',
                        help='treat a missing knowledge directory as an error '
                             'instead of a warning')
    args = parser.parse_args()

    project_root = os.path.realpath(args.project_root)
    knowledge_name = args.knowledge_dir
    errors = []
    warnings = []
    log_present = False
    topic_count = 0
    path_parts = [part for part in knowledge_name.replace('\\', '/').split('/')
                  if part not in ('', '.')]

    if not knowledge_name.strip():
        errors.append('Knowledge directory name must be nonblank')
    elif os.path.isabs(knowledge_name) or any(part == '..' for part in path_parts):
        errors.append('Knowledge directory must stay under the project root: '
                      + knowledge_name)
    elif not os.path.isdir(project_root):
        errors.append('Project root is not a directory: ' + project_root)
    else:
        knowledge_path = os.path.realpath(os.path.join(project_root, knowledge_name))
        if not is_within(project_root, knowledge_path):
            errors.append('Knowledge path must stay under the project root: '
                          + knowledge_path)
        elif not os.path.isdir(knowledge_path):
            if os.path.exists(knowledge_path):
                errors.append('Knowledge path is not a directory: '
                              + knowledge_path)
            elif args.require:
                errors.append('Knowledge layer is required but not found: '
                              + knowledge_path)
            else:
                warnings.append('Knowledge layer is not initialized '
                                '(optional): ' + knowledge_path)
        else:
            log_path = os.path.join(knowledge_path, 'LOG.md')
            log_present = os.path.isfile(log_path)
            if log_present and not is_within(knowledge_path, log_path):
                errors.append('LOG.md: must stay under the knowledge directory')
                log_present = False
            elif log_present:
                try:
                    if inspect_encoding(log_path, 'LOG.md', errors, warnings):
                        validate_log(read_text(log_path), errors, warnings)
                except OSError as exc:
                    errors.append('LOG.md: cannot read file: ' + str(exc))

            topics_path = os.path.join(knowledge_path, 'topics')
            topic_names = []
            if os.path.isdir(topics_path) and not is_within(knowledge_path, topics_path):
                errors.append('topics/: must stay under the knowledge directory')
            elif os.path.isdir(topics_path):
                try:
                    with os.scandir(topics_path) as entries:
                        topic_names = sorted(
                            entry.name for entry in entries
                            if entry.is_file(follow_symlinks=False)
                            and entry.name.endswith('.md'))
                except OSError as exc:
                    errors.append('topics/: cannot scan directory: ' + str(exc))
            topic_count = len(topic_names)
            for name in topic_names:
                display_name = safe_display_name(name)
                try:
                    validate_topic(os.path.join(topics_path, name), name,
                                   display_name, errors, warnings)
                except OSError as exc:
                    errors.append('topics/' + display_name
                                  + ': cannot read file: ' + str(exc))

            if not log_present:
                if topic_count:
                    warnings.append('LOG.md is expected when topics exist; '
                                    'topics are present but no timeline was '
                                    'found')
                else:
                    warnings.append('LOG.md is missing; the optional '
                                    'knowledge timeline is not initialized')

            roadmap_path = os.path.join(knowledge_path, 'ROADMAP.md')
            if os.path.isfile(roadmap_path):
                if not is_within(knowledge_path, roadmap_path):
                    errors.append('ROADMAP.md: must stay under the knowledge directory')
                else:
                    try:
                        validate_roadmap(roadmap_path, errors, warnings)
                    except OSError as exc:
                        errors.append('ROADMAP.md: cannot read file: ' + str(exc))

            cited_path = os.path.join(knowledge_path, 'Cited.md')
            if os.path.isfile(cited_path):
                if not is_within(knowledge_path, cited_path):
                    errors.append('Cited.md: must stay under the knowledge directory')
                else:
                    try:
                        validate_cited(cited_path, errors, warnings)
                    except OSError as exc:
                        errors.append('Cited.md: cannot read file: ' + str(exc))

    result = {
        'valid': not errors,
        'project_root': project_root,
        'knowledge_dir': knowledge_name,
        'log_present': log_present,
        'topic_count': topic_count,
        'errors': errors,
        'warnings': warnings,
    }
    # Always print the JSON; exit code 1 only when errors exist.
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        # Preserve the one-JSON-object contract even on an unexpected error.
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
        except Exception:
            pass
        result = {
            'valid': False,
            'project_root': None,
            'knowledge_dir': None,
            'log_present': False,
            'topic_count': 0,
            'errors': ['unexpected validation error: '
                       + type(exc).__name__ + ': ' + str(exc)],
            'warnings': [],
        }
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        sys.exit(1)
