#!/usr/bin/env python3
"""Resolve legacy agent-judge model placeholders before skill-up loads case YAML."""

import argparse
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PLACEHOLDER = "${EVAL_JUDGE_MODEL}"
MODEL_LINE = re.compile(
    r"^([ \t]*model:[ \t]*)\$\{EVAL_JUDGE_MODEL\}([ \t]*(?:\#[^\n]*)?)$",
    re.MULTILINE,
)
MODEL_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._:+/-]*\Z")


def prepare(cases_dir: Path, judge_model: str) -> int:
    if not MODEL_NAME.fullmatch(judge_model):
        raise ValueError("EVAL_JUDGE_MODEL must use provider/model format.")

    paths = sorted(cases_dir.glob("*.yaml"))
    if not paths:
        raise ValueError(f"No YAML cases found in {cases_dir}")

    replacements = []
    for path in paths:
        original = path.read_text(encoding="utf-8")
        if "type: agent_judge" not in original:
            continue
        rendered, count = MODEL_LINE.subn(
            lambda match: match.group(1) + judge_model + match.group(2),
            original,
        )
        if count != 1 or PLACEHOLDER in rendered:
            raise ValueError(
                f"{path}: expected one unresolved agent-judge model placeholder."
            )
        replacements.append((path, rendered))

    if not replacements:
        raise ValueError("No agent-judge cases were found.")

    for path, rendered in replacements:
        path.write_text(rendered, encoding="utf-8", newline="\n")

    return len(replacements)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases-dir", type=Path, default=ROOT / "evals" / "cases")
    parser.add_argument("--judge-model", default=os.environ.get("EVAL_JUDGE_MODEL", ""))
    args = parser.parse_args()
    try:
        count = prepare(args.cases_dir, args.judge_model)
    except ValueError as error:
        parser.error(str(error))
    print(f"Resolved the judge model in {count} evaluation cases.")


if __name__ == "__main__":
    main()
