#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate-project-state.py - validate the structure and state transitions of a project-status.md file

Standard-library-only script (Python 3.10+); the flags and the validation
behavior are described below.

- Flags: --path (required); --from-state and --to-state are used as a
  pair; --task-id (blocked recovery validation); --spec-path (defaults to
  templates/task-state-spec.txt located relative to the script, without
  hard-coding absolute paths).
- Spec parsing: read task-state-spec.txt line by line, skip blank lines
  and # comments; '=' separates key and value; phase / state / heading /
  transition.<from> and the remaining settings each go to their own
  bucket; a missing required settings key aborts with an error.
- Structure validation: required headings, the project phase field with a
  legal value, the task table header, the task list table (11 columns,
  duplicate task-id detection, legal states), and the blocked table (first
  column task id, second column pre-block state).
- Transition validation: --from-state/--to-state must be provided
  together; source and target states must be legal and the transition must
  be allowed by the table; the <blocked-before> pseudo-target means "the
  task's pre-block state" and is verified with --task-id.
- Case comparison: state and transition lookup is case-insensitive; the
  spelling from the specification is retained in validation messages.
- Output: UTF-8 without BOM, LF line endings. JSON contains valid / path /
  task_count / errors; when errors exist the JSON is still printed and the
  exit code is 1; fatal errors such as a missing state file or a missing
  spec key go to stderr with exit code 1.
"""

import argparse
import json
import os
import re
import sys


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
        description='Validate the structure and state-transition legality of a '
                    'project-status.md file')
    parser.add_argument('--path', required=True, metavar='FILE',
                        help='path to the project-status.md file to validate (required)')
    parser.add_argument('--from-state', default=None, metavar='STATE',
                        help='source state of the transition (must be paired with --to-state)')
    parser.add_argument('--to-state', default=None, metavar='STATE',
                        help='target state of the transition (must be paired with --from-state)')
    parser.add_argument('--task-id', default=None, metavar='ID',
                        help='task id used to validate blocked recovery')
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
    task_ids = set()   # case-insensitive
    if task_section:
        for line_number, line in enumerate(
                re.split(r'\r\n|\r|\n', task_section.group(1)), start=1):
            if not line.startswith('|'):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) != task_column_count:
                errors.append('Malformed task table row ' + str(line_number)
                              + ': expected ' + str(task_column_count)
                              + ' columns, found ' + str(len(cells)))
                continue
            if contains_ci((settings['task_id_header'], '---', ''), cells[0]):
                continue
            parsed_task_id = cells[0]
            state = cells[2]
            task_key = parsed_task_id.strip().casefold()
            if task_key in task_ids:
                errors.append('Duplicate task id: ' + parsed_task_id)
            else:
                task_ids.add(task_key)
            if not contains_ci(task_states, state):
                errors.append('Task ' + parsed_task_id + ' has invalid state: ' + state)
    else:
        errors.append('Task table section is missing')

    # blockedSection: non-greedy capture of the blocked table; keep only the
    # first occurrence per task
    blocked_before_by_task = {}
    blocked_pattern = ('(?s)' + re.escape(settings['blocked_section_start'])
                       + r'\s*(.*?)\s*' + re.escape(settings['blocked_section_end']))
    blocked_match = re.search(blocked_pattern, content)
    if blocked_match:
        for line_number, line in enumerate(
                re.split(r'\r\n|\r|\n', blocked_match.group(1)), start=1):
            if not line.startswith('|'):
                continue
            cells = [cell.strip() for cell in line.strip('|').split('|')]
            if len(cells) != blocked_column_count:
                errors.append('Malformed blocked table row ' + str(line_number)
                              + ': expected ' + str(blocked_column_count)
                              + ' columns, found ' + str(len(cells)))
                continue
            if contains_ci((settings['blocked_id_header'], '---', ''), cells[0]):
                continue
            task_key = cells[0].strip().casefold()
            if task_key not in blocked_before_by_task:
                blocked_before_by_task[task_key] = cells[1]
    else:
        errors.append('Blocked section is missing')

    # State transition validation (including <blocked-before> blocked recovery)
    blocked_before_token = '<blocked-before>'
    from_state = args.from_state
    to_state = args.to_state
    task_id = args.task_id
    if from_state or to_state:
        if not from_state or not to_state:
            errors.append('FromState and ToState must be provided together')
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
                if not task_id:
                    errors.append('Blocked recovery requires --task-id to verify the pre-block state')
                else:
                    task_key = task_id.strip().casefold()
                    if task_key not in blocked_before_by_task:
                        errors.append('Task ' + task_id + ' is not listed in the blocked section')
                    elif normalize_state(to_state) != normalize_state(blocked_before_by_task[task_key]):
                        errors.append('Invalid state transition: ' + from_state + ' -> ' + to_state
                                      + ' (pre-block state of task ' + task_id + ' is '
                                      + blocked_before_by_task[task_key] + ')')
        elif not contains_ci(transitions_ci[normalize_state(from_state)], to_state):
            errors.append('Invalid state transition: ' + from_state + ' -> ' + to_state)

    result = {
        'valid': len(errors) == 0,
        'path': real_path,
        'task_count': len(task_ids),
        'errors': errors,
    }
    # Always print the JSON; exit code 1 when errors exist
    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
