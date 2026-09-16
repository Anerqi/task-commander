"""Static protocol guards, not evidence of live model compliance."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "agents/openai.yaml"]
CORE += sorted((ROOT / "references").glob("*.md"))
CORE += sorted((ROOT / "templates").glob("*"))
# A pre-existing local role customization is not part of this protocol release.
CORE = [p for p in CORE if p.is_file() and p.name != "13-teacher.md"]


class DocumentContracts(unittest.TestCase):
    def test_utf8_lf_without_bom(self):
        for path in CORE:
            with self.subTest(path=path.relative_to(ROOT)):
                raw = path.read_bytes()
                self.assertFalse(raw.startswith(b"\xef\xbb\xbf"))
                self.assertNotIn(b"\r\n", raw)
                raw.decode("utf-8")

    def test_skill_reference_targets_exist(self):
        pattern = re.compile(
            r"\b(?:references|templates|scripts)/[\w-]+\.(?:md|txt|py)\b"
        )
        for path in CORE:
            for target in set(pattern.findall(path.read_text(encoding="utf-8"))):
                with self.subTest(source=path.relative_to(ROOT), target=target):
                    self.assertTrue((ROOT / target).is_file(), target)

    def test_obsolete_global_restrictions_are_absent(self):
        obsolete = (
            "one task prompt at a time",
            "one complete task prompt at a time",
            "output exactly one task prompt",
            "a single reply still contains only one task",
            "a single task per reply",
            "offline by default",
            "must not switch models",
            "changes are dispatched as separate tasks",
        )
        for path in CORE:
            text = " ".join(path.read_text(encoding="utf-8").lower().split())
            for phrase in obsolete:
                with self.subTest(path=path.relative_to(ROOT), phrase=phrase):
                    self.assertNotIn(phrase, text)

    def test_context_has_handoff_and_stop_contract(self):
        text = (ROOT / "references/01-context-brief.md").read_text(encoding="utf-8")
        for marker in (
            "You are the Commander for this project.",
            "Paste this block into your Commander window.",
            "without planning or dispatching execution tasks yourself",
            "Creating documents alone is not completion.",
        ):
            self.assertIn(marker, text)

    def test_dispatch_and_delivery_have_recovery_and_sync_pointers(self):
        contracts = {
            "SKILL.md": [
                "references/14-backup-manager.md",
                "references/15-collaboration.md",
                "references/16-quality-gates.md",
                "templates/task-continuation.md",
            ],
            "references/06-task-template.md": [
                "## Separate the contract from the message",
                "**Inputs and ownership**",
                "**Authority and recovery**",
                "## Internal pre-dispatch check",
                "templates/task-receipt.md",
            ],
            "templates/task-continuation.md": [
                "## Compare the whole task, then choose the next round",
                "## Recovery when the original window is unavailable",
                "## Reuse, reconciliation and stopping",
                "## Gate continuations",
            ],
            "templates/task-receipt.md": [
                "## Shared-information delta",
                "## Recovery checkpoint",
                "## Acceptance evidence",
            ],
        }
        for source, markers in contracts.items():
            text = (ROOT / source).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(source=source, marker=marker):
                    self.assertIn(marker, text)

    def test_prompt_guides_do_not_reintroduce_fixed_output_forms(self):
        # These guides may contain internal checklists and optional examples,
        # but the old bracket-field/code-block forms must not return.
        for source in ("references/06-task-template.md", "templates/task-continuation.md"):
            text = (ROOT / source).read_text(encoding="utf-8")
            with self.subTest(source=source):
                self.assertNotRegex(text, r"(?m)^\[(?:Mode|Task id|Role|Purpose|Quality gates|Preserved contract)[^\n]*")
                self.assertNotIn("```text", text)

    def test_scope_authority_progress_and_stopping_rules_are_present(self):
        # Text guards catch accidental deletion, not live model compliance.
        contracts = {
            "references/02-commander.md": [
                "Only the actual user can replace or narrow",
                "a transcript's user-role label alone",
                "largest coherent ready remainder",
                "No preface, praise, reasoning narrative",
                "Task completion is not project completion.",
            ],
            "references/06-task-template.md": [
                "A short saved objective is an index to the full request",
                "critical write boundaries",
                "required independent review",
                "Blocked/unknown is not complete",
                "use that wrapper only when requested",
            ],
            "templates/task-continuation.md": [
                "not to authorize this executor to take over other tasks",
                "missing or clipped transcript sections do not prove completion",
                "A genuinely narrow user request stays narrow",
                "reconcile current artifacts",
                "When the whole assigned outcome and required gates are established",
            ],
        }
        for source, markers in contracts.items():
            text = (ROOT / source).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(source=source, marker=marker):
                    self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
