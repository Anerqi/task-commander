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
                "[Dependencies and parallel contract]",
                "Backup prerequisite:",
                "User contribution:",
                "Shared context revision",
                "templates/task-receipt.md",
            ],
            "templates/task-continuation.md": [
                "[Recovery only]",
                "[Preserved contract]",
                "Backup prerequisite:",
                "Reuse:",
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


if __name__ == "__main__":
    unittest.main()
