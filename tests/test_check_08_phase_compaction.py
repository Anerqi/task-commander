"""Regression tests for case 08 phase-compaction disk checks."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "evals" / "scripts" / "check_08_phase_compaction.py"
SPEC = importlib.util.spec_from_file_location("check_08_phase_compaction", CHECKER_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PhaseCompactionCheckTests(unittest.TestCase):
    def history_rows(self):
        return [list(row) for row in CHECKER.EXPECTED_HISTORY]

    def test_one_project_phase_change_can_be_appended(self):
        rows = self.history_rows()
        rows.append([
            "2026-11-15", "Project", "Acceptance", "Planning",
            "Phase 1 accepted; Phase 2 handoff prepared", "Commander",
        ])
        self.assertTrue(CHECKER.history_is_valid(rows))

    def test_changed_original_history_row_fails(self):
        rows = self.history_rows()
        rows[4][4] = "Changed validation basis"
        self.assertFalse(CHECKER.history_is_valid(rows))

    def test_appended_history_requires_a_project_phase_change(self):
        rows = self.history_rows()
        rows.append([
            "2026-11-15", "TASK-013", "TODO", "In Progress",
            "New work", "Commander",
        ])
        self.assertFalse(CHECKER.history_is_valid(rows))

    def test_appended_history_cannot_predate_the_date_floor(self):
        rows = self.history_rows()
        rows.append([
            "2026-11-09", "Project", "Acceptance", "Planning",
            "Phase boundary", "Commander",
        ])
        self.assertFalse(CHECKER.history_is_valid(rows))

    def test_descriptive_phase_two_current_focus_passes(self):
        roadmap = "**Current focus**: Plan the Phase 2 cutover rehearsal and rollback review.\n"
        self.assertTrue(CHECKER.current_focus_is_phase_2(roadmap))

    def test_current_focus_must_not_repeat_phase_one_validation(self):
        roadmap = "**Current focus**: Phase 2 after Phase 1 validation.\n"
        self.assertFalse(CHECKER.current_focus_is_phase_2(roadmap))

    def test_latest_log_entry_accepts_descriptive_phase_one_closeout(self):
        log = (
            "# Project Knowledge Log\n\n"
            "## 2026-11-10 — Phase 1 validation baseline\n"
            "- Baseline retained.\n\n"
            "## 2026-11-15 — Closeout and handoff\n"
            "- Phase 1 is closed and the Phase 2 handoff is ready.\n"
        )
        self.assertTrue(CHECKER.latest_log_entry_is_valid(log))

    def test_latest_log_entry_rejects_wrong_date_and_long_entry(self):
        wrong_date = (
            "# Project Knowledge Log\n\n"
            "## 2026-11-14 — Phase 1 closeout\n"
            "- Phase 1 is closed.\n"
        )
        self.assertFalse(CHECKER.latest_log_entry_is_valid(wrong_date))
        long_entry = (
            "## 2026-11-15 — Phase 1 closeout\n"
            + "".join(f"- Detail {index}.\n" for index in range(20))
        )
        self.assertFalse(CHECKER.latest_log_entry_is_valid(long_entry))


if __name__ == "__main__":
    unittest.main()
