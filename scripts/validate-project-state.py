#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-project-state.py - validate the structure and state transitions of a project-status.md file

Standard-library-only script (Python 3.10+); the flags and the validation
behavior are described below.

- Flags: --path (required; alone performs structural validation);
  --from-state and --to-state require each other and a nonblank --task-id;
  --task-id alone is invalid; --spec-path (defaults to
  templates/task-state-spec.txt located relative to the script, without
  hard-coding absolute paths); --expected-revision N compares the optional
  "- Status revision: N" line in the Project section, which gives the sole
  writer a compare-and-set check instead of an honour-system read.
- Optional coordination metadata: a "## Needs you now" section, when present,
  must hold at most needs_you_max_rows rows (default 5) of three columns
  (task, one concrete question, resume condition). Each row must name an
  existing task in a non-terminal state and carry a nonblank question; a
  missing section or an empty one is valid, so older files stay valid.
- Status revision: when --expected-revision is given, the file must carry a
  non-negative integer revision line and match it; a missing line is an error
  rather than a silent pass.
- Spec parsing: read task-state-spec.txt line by line, skip blank lines
  and # comments; '=' separates key and value; phase / state / heading /
  transition.<from> and the remaining settings each go to their own
  bucket; a missing required settings key aborts with an error.
- Structure validation: required headings, the project phase field with a
  legal value, the task table header, the task list table (11 columns,
  duplicate task-id detection, legal states), and the blocked table (first
  column task id, second column pre-block state). Every currently Blocked
  task requires exactly one blocked record; other tasks must have none.
  Pre-block states must be declared, non-Blocked states with a legal edge
  to Blocked. Malformed, duplicate, orphan, and stale records are errors.
- Transition validation: nonblank --from-state/--to-state and --task-id
  identify a parsed task whose current state must match --from-state.
  Source and target states must be legal and the transition must be allowed
  by the table; <blocked-before> permits restoration to the recorded state.
  Explicit edges (including Blocked -> Cancelled) do not require restoration,
  but still require structurally consistent metadata. Reviewer/QA flags,
  evidence, and phase semantics are not enforced.
- Case comparison: state and transition lookup is case-insensitive; the
  spelling from the specification is retained in validation messages.
- Output: UTF-8 without BOM, LF line endings. JSON contains valid / path /
  task_count / status_revision / needs_you_count / errors; when errors exist the JSON is still printed and the
  exit code is 1; fatal errors such as a missing state file or a missing
  spec key go to stderr with exit code 1.
"""

import argparse
import json
import os
import re
import sys

try:
    from markdown_table import is_separator_row, split_markdown_row
except ImportError as exc:
    raise SystemExit(
        'markdown_table.py must be alongside this script; copy the whole '
        'scripts/ directory. (' + str(exc) + ')'
    ) from None


def contains_ci(sequence, value):
    """List membership with case-insensitive comparison."""
    normalized = normalize_state(value)
    return any(normalize_state(item) == normalized for item in sequence)


def normalize_state(value):
    """Return the comparison form used for state names and transitions."""
    return value.strip().casefold()


def load_spec(spec_path):
    """Parse the spec: return phases, states, headings, transitions, settings."""
    # UTF-8 with BOM stripped; invalid bytes are replaced
    with open(spec_path, 'r', encoding='utf-8-sig', errors='replace') as reader:
        spec_content = reader.read()

    project_phases = []
    task_states = []
    required_headings = []
    transitions = {}
    settings = {}

    for raw_line in re.split(r'\r\n|\r|\n', spec_content):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        separator = line.find('=')
        if separator < 1:
            continue
        key = line[:separator].strip()
        value = line[separator + 1:].strip()
        if key == 'phase':
            project_phases.append(value)
        elif key == 'state':
            task_states.append(value)
        elif key == 'heading':
            required_headings.append(value)
        elif key.startswith('transition.'):
            from_state = key[len('transition.'):]
            if value:
                transitions[from_state] = value.split('|')
            else:
                transitions[from_state] = []
        else:
            settings[key] = value

    return project_phases, task_states, required_headings, transitions, settings


def main():
    # When stdout is piped or redirected, the platform default code page
    # (e.g. GBK) garbles non-ASCII output; reconfigure both streams to
    # UTF-8 up front (aligned with the UTF-8 output principle in runtime.md;
    # this also keeps argparse --help text UTF-8).
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(
        description='Validate project-status.md structure with --path alone, or '
                    'also validate a task transition with --from-state, --to-state, '
                    'and --task-id.')
    parser.add_argument('--path', required=True, metavar='FILE',
                        help='path to the project-status.md file to validate (required)')
    parser.add_argument('--from-state', default=None, metavar='STATE',
                        help='current task state (requires --to-state and --task-id; nonblank)')
    parser.add_argument('--to-state', default=None, metavar='STATE',
                        help='target state (requires --from-state and --task-id; nonblank)')
    parser.add_argument('--task-id', default=None, metavar='ID',
                        help='existing task id required for every transition; invalid alone')
    parser.add_argument('--expected-revision', default=None, type=int, metavar='N',
                        help='compare the optional "- Status revision: N" line in the '
                             'Project section; a mismatch or a missing line is an error')
    parser.add_argument('--spec-path', default=None, metavar='FILE',
                        help='path to the state specification file; defaults to '
                             'templates/task-state-spec.txt under the Task Commander '
                             'root (located relative to the script)')
    args = parser.parse_args()

    if args.spec_path:
        spec_path = os.path.realpath(args.spec_path)
    else:
        # --spec-path default = templates/task-state-spec.txt in the parent of
        # the script directory
        spec_path = os.path.realpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', 'templates', 'task-state-spec.txt'))

    real_path = os.path.realpath(args.path)

    if not os.path.isfile(real_path):
        sys.exit('State file not found: ' + args.path)
    if not os.path.isfile(spec_path):
        sys.exit('State specification not found: ' + spec_path)

    project_phases, task_states, required_headings, transitions, settings = load_spec(spec_path)
    transitions_ci = {
        normalize_state(source): targets
        for source, targets in transitions.items()
    }

    required_settings = [
        'phase_prefix', 'task_header', 'task_section_start', 'task_section_end',
        'task_id_header', 'blocked_section_start', 'blocked_section_end', 'blocked_id_header',
        'task_column_count', 'blocked_column_count',
    ]
    for key in required_settings:
        if key not in settings:
            sys.exit('Missing state specification key: ' + key)

    # UTF-8 with BOM stripped; invalid bytes are replaced
    with open(real_path, 'r', encoding='utf-8-sig', errors='replace') as reader:
        content = reader.read()

    errors = []

    for heading in required_headings:
        if heading not in content:
            errors.append('Missing heading: ' + heading)

    # phasePattern: the first line whose start is exactly phase_prefix
    phase_match = re.search(
        r'(?m)^' + re.escape(settings['phase_prefix']) + r'(.+)$', content)
    if not phase_match:
        errors.append('Missing project phase field')
    else:
        phase = phase_match.group(1).strip()
        if not contains_ci(project_phases, phase):
            errors.append('Invalid project phase: ' + phase)

    if settings['task_header'] not in content:
        errors.append('Task table header does not match the template')

    try:
        task_column_count = int(settings['task_column_count'])
        blocked_column_count = int(settings['blocked_column_count'])
        if task_column_count < 1 or blocked_column_count < 1:
            raise ValueError
    except ValueError:
        sys.exit('State specification column counts must be positive integers')

    # taskSection: non-greedy capture of the task list table content
    section_pattern = ('(?s)' + re.escape(settings['task_section_start'])
                       + r'\s*(.*?)\s*' + re.escape(settings['task_section_end']))
    task_section = re.search(section_pattern, content)
    task_states_by_id = {}   # case-insensitive task id -> parsed current state
    if task_section:
        for line_number, line in enumerate(
                re.split(r'\r\n|\r|\n', task_section.group(1)), start=1):
            line = line.strip()
            if not line.startswith('|'):
                continue
            cells = split_markdown_row(line)
            if len(cells) != task_column_count:
                errors.append('Malformed task table row ' + str(line_number)
                              + ': expected ' + str(task_column_count)
                              + ' columns, found ' + str(len(cells)))
                continue
            if is_separator_row(cells) or contains_ci((settings['task_id_header'], ''), cells[0]):
                continue
            parsed_task_id = cells[0]
            state = cells[2]
            task_key = parsed_task_id.strip().casefold()
            if task_key in task_states_by_id:
                errors.append('Duplicate task id: ' + parsed_task_id)
            else:
                task_states_by_id[task_key] = state
            if not contains_ci(task_states, state):
                errors.append('Task ' + parsed_task_id + ' has invalid state: ' + state)
    else:
        errors.append('Task table section is missing')

    # Validate all blocked metadata, even for structural-only invocations.
    blocked_before_by_task = {}
    blocked_pattern = ('(?s)' + re.escape(settings['blocked_section_start'])
                       + r'\s*(.*?)\s*' + re.escape(settings['blocked_section_end']))
    blocked_match = re.search(blocked_pattern, content)
    if blocked_match:
        for line_number, line in enumerate(
                re.split(r'\r\n|\r|\n', blocked_match.group(1)), start=1):
            line = line.strip()
            if not line.startswith('|'):
                continue
            cells = split_markdown_row(line)
            if len(cells) != blocked_column_count:
                errors.append('Malformed blocked table row ' + str(line_number)
                              + ': expected ' + str(blocked_column_count)
                              + ' columns, found ' + str(len(cells)))
                continue
            if is_separator_row(cells) or contains_ci((settings['blocked_id_header'],), cells[0]):
                continue
            task_key = cells[0].strip().casefold()
            if not task_key:
                errors.append('Malformed blocked table row ' + str(line_number)
                              + ': task id must be nonblank')
            if task_key in blocked_before_by_task:
                errors.append('Duplicate blocked record for task: ' + cells[0])
            else:
                blocked_before_by_task[task_key] = cells[1]
            if task_key not in task_states_by_id:
                errors.append('Orphan blocked record for task: ' + cells[0])
            elif normalize_state(task_states_by_id[task_key]) != 'blocked':
                errors.append('Blocked record for non-Blocked task: ' + cells[0])
            before = cells[1]
            if (not contains_ci(task_states, before)
                    or normalize_state(before) == 'blocked'
                    or not contains_ci(transitions_ci.get(normalize_state(before), []),
                                       'Blocked')):
                errors.append('Invalid pre-block state for task ' + cells[0] + ': ' + before)
    else:
        errors.append('Blocked section is missing')

    for task_key, state in task_states_by_id.items():
        if normalize_state(state) == 'blocked' and task_key not in blocked_before_by_task:
            errors.append('Missing blocked record for task: ' + task_key)

    # Optional compare-and-set metadata: the sole writer bumps the revision once
    # per update, so a stale read is detectable instead of silently overwritten.
    revision_value = None
    revision_prefix = settings.get('revision_prefix', '- Status revision:')
    revision_match = re.search(r'(?m)^' + re.escape(revision_prefix) + r'\s*(\S+)\s*$', content)
    if revision_match:
        raw_revision = revision_match.group(1)
        if re.fullmatch(r'\d+', raw_revision):
            revision_value = int(raw_revision)
        else:
            errors.append('Invalid status revision: ' + raw_revision)
    if args.expected_revision is not None:
        if args.expected_revision < 0:
            errors.append('Expected revision must not be negative: ' + str(args.expected_revision))
        elif not revision_match:
            errors.append('Missing status revision line required by --expected-revision')
        elif revision_value is not None and revision_value != args.expected_revision:
            errors.append('Status revision mismatch: file has ' + str(revision_value)
                          + ', expected ' + str(args.expected_revision))

    # Optional attention view: only work that waits for a person belongs here,
    # and the row count is capped so a healthy project takes no space.
    needs_you_count = 0
    needs_you_start = settings.get('needs_you_section_start')
    needs_you_end = settings.get('needs_you_section_end')
    if needs_you_start and needs_you_end and needs_you_start in content:
        try:
            needs_you_columns = int(settings.get('needs_you_column_count', '3'))
            needs_you_max_rows = int(settings.get('needs_you_max_rows', '5'))
            if needs_you_columns < 1 or needs_you_max_rows < 1:
                raise ValueError
        except ValueError:
            sys.exit('Needs-you-now column count and row cap must be positive integers')
        needs_you_header = settings.get('needs_you_task_header', 'Task')
        needs_you_section = re.search(
            '(?s)' + re.escape(needs_you_start) + r'\s*(.*?)\s*' + re.escape(needs_you_end),
            content)
        if not needs_you_section:
            errors.append('Needs you now section is not closed by the following section heading')
        else:
            for line_number, line in enumerate(
                    re.split(r'\r\n|\r|\n', needs_you_section.group(1)), start=1):
                line = line.strip()
                if not line.startswith('|'):
                    continue
                cells = split_markdown_row(line)
                if len(cells) != needs_you_columns:
                    errors.append('Malformed needs-you-now row ' + str(line_number)
                                  + ': expected ' + str(needs_you_columns)
                                  + ' columns, found ' + str(len(cells)))
                    continue
                if is_separator_row(cells) or contains_ci((needs_you_header, ''), cells[0]):
                    continue
                needs_you_count += 1
                needs_you_task = cells[0].strip()
                needs_you_key = needs_you_task.casefold()
                if not needs_you_key:
                    errors.append('Malformed needs-you-now row ' + str(line_number)
                                  + ': task id must be nonblank')
                    continue
                if needs_you_key not in task_states_by_id:
                    errors.append('Needs you now references unknown task: ' + needs_you_task)
                elif normalize_state(task_states_by_id[needs_you_key]) in ('completed', 'cancelled'):
                    errors.append('Needs you now lists a finished task: ' + needs_you_task)
                if not cells[1].strip() or cells[1].strip() == '-':
                    errors.append('Needs you now row for task ' + needs_you_task
                                  + ' has no concrete question')
            if needs_you_count > needs_you_max_rows:
                errors.append('Needs you now lists ' + str(needs_you_count)
                              + ' rows; the attention budget is ' + str(needs_you_max_rows))

    # Flag presence, not truthiness: empty values must never bypass validation.
    # State transition validation (including <blocked-before> blocked recovery)
    blocked_before_token = '<blocked-before>'
    from_state = args.from_state
    to_state = args.to_state
    task_id = args.task_id
    if from_state is not None or to_state is not None:
        if task_id is None or not task_id.strip():
            errors.append('Transitions require a nonblank --task-id')
        elif task_id.strip().casefold() not in task_states_by_id:
            errors.append('Unknown task id: ' + task_id)
        elif (from_state is not None and normalize_state(from_state)
              != normalize_state(task_states_by_id[task_id.strip().casefold()])):
            errors.append('Source state mismatch for task ' + task_id + ': current state is '
                          + task_states_by_id[task_id.strip().casefold()]
                          + ', not ' + from_state)
        if from_state is None or to_state is None:
            errors.append('FromState and ToState must be provided together')
        elif not from_state.strip() or not to_state.strip():
            errors.append('FromState and ToState must be nonblank')
        elif not contains_ci(task_states, from_state):
            errors.append('Invalid source state: ' + from_state)
        elif not contains_ci(task_states, to_state):
            errors.append('Invalid target state: ' + to_state)
        elif normalize_state(from_state) not in transitions_ci:
            errors.append('Invalid state transition: ' + from_state + ' -> ' + to_state)
        elif contains_ci(transitions_ci[normalize_state(from_state)], blocked_before_token):
            explicit_targets = [target for target in transitions_ci[normalize_state(from_state)]
                                if normalize_state(target) != normalize_state(blocked_before_token)]
            if not contains_ci(explicit_targets, to_state):
                task_key = task_id.strip().casefold() if task_id is not None else ''
                if task_key in task_states_by_id and task_key not in blocked_before_by_task:
                    errors.append('Missing blocked record for task: ' + task_id)
                elif task_key in blocked_before_by_task and (
                        normalize_state(to_state) != normalize_state(blocked_before_by_task[task_key])):
                    errors.append('Invalid state transition: ' + from_state + ' -> ' + to_state
                                  + ' (pre-block state of task ' + task_id + ' is '
                                  + blocked_before_by_task[task_key] + ')')
        elif not contains_ci(transitions_ci[normalize_state(from_state)], to_state):
            errors.append('Invalid state transition: ' + from_state + ' -> ' + to_state)

    elif task_id is not None:
        errors.append('--task-id requires --from-state and --to-state')

    result = {
        'valid': len(errors) == 0,
        'path': real_path,
        'task_count': len(task_states_by_id),
        'status_revision': revision_value,
        'needs_you_count': needs_you_count,
        'errors': errors,
    }
    # Always print the JSON; exit code 1 when errors exist
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
