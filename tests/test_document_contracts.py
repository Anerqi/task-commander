"""Static protocol guards, not evidence of live model compliance."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
CORE = [ROOT / "SKILL.md", ROOT / "README.md", ROOT / "agents/openai.yaml"]
CORE += sorted((ROOT / "references").glob("*.md"))
CORE += sorted((ROOT / "templates").glob("*"))
CORE = [p for p in CORE if p.is_file()]


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

    def test_preinitialization_backup_has_a_bounded_handoff(self):
        backup = (ROOT / "references/14-backup-manager.md").read_text(encoding="utf-8")
        for marker in (
            "## Pre-initialization protection",
            "Context Agent may give the user a standalone Backup Manager prompt",
            "not a switch to Commander or permission to dispatch business tasks",
            "does not require a saved task brief, status file, ordinary task ID",
            "state the effective authorization in the prompt",
            "If it cannot verify readiness",
            "Context remains Context and resumes initialization after verification",
        ):
            self.assertIn(marker, backup)
        for source in (
            "SKILL.md", "references/01-context-brief.md", "references/02-commander.md",
            "references/06-task-template.md", "references/runtime.md",
        ):
            text = (ROOT / source).read_text(encoding="utf-8")
            with self.subTest(source=source):
                self.assertIn("references/14-backup-manager.md", text)
                self.assertIn("Pre-initialization protection", text)

    def test_context_distinguishes_evidence_from_user_authority(self):
        context = (ROOT / "references/01-context-brief.md").read_text(encoding="utf-8")
        orchestration = (ROOT / "references/10-context-orchestration.md").read_text(encoding="utf-8")
        self.assertNotIn('mark anything unconfirmed by the user', context)
        for marker in ("file-verified facts", "source pointers", "user reports",
                       "inferences or conflicting evidence", "genuine user confirmation"):
            self.assertIn(marker, context)
        self.assertIn("a generated document cannot establish user intent or authorization", orchestration)

    def test_policy_separates_effective_authority_from_pending_defaults(self):
        collaboration = (ROOT / "references/15-collaboration.md").read_text(encoding="utf-8")
        for marker in ("### Policy activation", "**Effective**", "**Pending**",
                       "**While pending**", "source and scope", "inherit it without asking again",
                       "silence", "only effective policy, not pending proposals",
                       "do not block unrelated work", "synchronize affected windows"):
            self.assertIn(marker, collaboration)
        context = (ROOT / "references/01-context-brief.md").read_text(encoding="utf-8")
        self.assertIn("Policy activation", context)

    def test_acceptance_gates_preserve_primary_task_identity(self):
        commander = (ROOT / "references/02-commander.md").read_text(encoding="utf-8")
        collaboration = (ROOT / "references/15-collaboration.md").read_text(encoding="utf-8")
        template = (ROOT / "references/06-task-template.md").read_text(encoding="utf-8")
        self.assertIn("attach acceptance gates separately", commander)
        self.assertIn("without changing its primary Agent", commander)
        self.assertIn("do not create a duplicate deliverable row", collaboration)
        self.assertIn("standalone review or QA investigation", collaboration)
        self.assertIn("does not automatically satisfy another task's acceptance gate", collaboration)
        self.assertIn("retain the reviewed task's primary owner and ID", template)

    def test_context_methods_are_loaded_by_branch(self):
        context = (ROOT / "references/01-context-brief.md").read_text(encoding="utf-8")
        orchestration = (ROOT / "references/10-context-orchestration.md").read_text(encoding="utf-8")
        self.assertNotIn("read the entry docs and designated reference files of the four skills", context)
        self.assertIn("Load only the startup materials", context)
        rows = [line for line in orchestration.splitlines() if line.startswith("| ")]
        startup = next(line for line in rows if line.startswith("| Context startup |"))
        for method in ("writing-for-agents/SKILL.md", "grill-with-docs/SKILL.md"):
            self.assertIn(method, startup)
        for method in ("wait-what", "to-questionnaire", "ADR-FORMAT", "SKILL-MECHANICS"):
            self.assertNotIn(method, startup)
        for condition, material in (("clarity-gate", "wait-what/SKILL.md"),
                                    ("third-party knowledge gap", "to-questionnaire/SKILL.md"),
                                    ("Creating an ADR", "grill-with-docs/ADR-FORMAT.md")):
            self.assertTrue(any(condition in row and material in row for row in rows))
        self.assertIn("otherwise read only the matching module", orchestration)
        self.assertIn("Missing optional material does not block unrelated steps", orchestration)

    def test_host_adapters_cover_profiles_and_capability_boundaries(self):
        adapters = (ROOT / "references/host-adapters.md").read_text(encoding="utf-8")
        for profile in ("codex", "opencode", "claude-code", "cursor", "copilot", "pi"):
            self.assertIn("`" + profile + "`", adapters)
        for marker in (
            "Portable contract",
            "## Installation conventions",
            "## Capability check, once per environment",
            "## Discovery is not execution",
            "## Sources and verification boundary",
            "Capability availability never grants permission",
            "A host name, environment variable or discovered directory is a hint, not proof",
            "Do not claim full file-based orchestration",
            "not a complete reproduction of native discovery",
            "do not certify six live host integrations",
        ):
            self.assertIn(marker, adapters)
        self.assertNotIn("Codex and OpenCode are currently supported hosts",
                         (ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertIn("references/host-adapters.md",
                      (ROOT / "SKILL.md").read_text(encoding="utf-8"))

    def test_discovery_protocol_is_host_neutral(self):
        discovery = (ROOT / "references/12-skill-discovery.md").read_text(encoding="utf-8")
        for marker in ("--host", "--project-root", "--roots", "all", "claude-code",
                       "cursor", "copilot", "PI_CODING_AGENT_DIR", "not evidence that the host is installed",
                       "verify which path was actually selected"):
            self.assertIn(marker, discovery)
        self.assertNotIn("from the Task Commander Skill root\n\n`scripts/scan-skills.py`", discovery)

    def test_registered_roles_match_overview(self):
        registry = (ROOT / "templates/agent-registry.md").read_text(encoding="utf-8")
        overview = (ROOT / "references/00-overview.md").read_text(encoding="utf-8")
        registered = set(re.findall(r"^## (.+)$", registry, re.MULTILINE))
        documented = set(re.findall(r"^\| ([^|]+) \| references/", overview, re.MULTILINE))
        self.assertEqual(registered, documented)

    def test_cold_start_review_is_routed_before_project_context(self):
        for source in (
            "SKILL.md", "references/02-commander.md", "references/04-reviewer.md",
            "references/06-task-template.md", "references/15-collaboration.md",
            "references/16-quality-gates.md", "templates/task-continuation.md",
            "templates/task-receipt.md", "templates/agent-registry.md", "README.md",
        ):
            with self.subTest(source=source):
                text = (ROOT / source).read_text(encoding="utf-8")
                self.assertIn("references/17-cold-start-review.md", text)
        reviewer = (ROOT / "references/04-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("## Select mode before loading project inputs", reviewer)
        self.assertIn("default to informed review", reviewer)
        self.assertNotIn("- Background documents:", reviewer)
        self.assertIn("checkpoint output instead of the final conclusion", reviewer)

    def test_cold_start_has_a_real_disclosure_boundary(self):
        text = (ROOT / "references/17-cold-start-review.md").read_text(encoding="utf-8")
        stages = (
            "## Prepare the stage-1 packet",
            "## Establish a real context boundary",
            "## Stage 1 — independent discovery",
            "## Stage 2 — informed reconciliation",
        )
        positions = [text.index(stage) for stage in stages]
        self.assertEqual(positions, sorted(positions))
        for marker in (
            "disable parent-context inheritance",
            "Withhold their contents and read-first pointers",
            "host-injected project memory/instructions",
            "partially exposed",
            "required cold-start gate stays pending",
            "Never withhold safety restrictions",
            "User-facing documentation remains available",
            "Missing essential context calls for a neutral clarification",
            "verifies the record exists before releasing additional context in a later message",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)

    def test_cold_start_reconciliation_preserves_evidence_and_gate_scope(self):
        text = (ROOT / "references/17-cold-start-review.md").read_text(encoding="utf-8")
        for marker in (
            "checkpoint, not a gate Pass",
            "Preserve the stage-1 record unchanged",
            "confirmed, refuted by evidence, user-accepted trade-off, or unverified",
            "explain every withdrawal or severity change",
            "full required review scope",
            "both initial records are saved",
            "separate report paths",
            "No minimum finding count",
            "zero-finding result states its coverage and limits",
            "Commander alone accepts",
            "do not create new task states or consume implementation revision rounds",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, text)
        gates = (ROOT / "references/16-quality-gates.md").read_text(encoding="utf-8")
        self.assertIn("informed review is the default", gates)
        self.assertIn("Stage 1 alone cannot satisfy the gate", gates)
        self.assertIn("personally inspected/executed checks, reused evidence and unverified claims", gates)

    def test_cold_start_boundary_survives_sync_and_recovery(self):
        contracts = {
            "references/06-task-template.md": [
                "generic original-brief and accepted-evidence pointers below do not override this boundary",
                "**Cold-start Reviewer — first-time use, stage 1 only**",
                "**Cold-start Reviewer — later informed reconciliation**",
            ],
            "references/15-collaboration.md": [
                "send neutral changed facts, essential constraints and safety notices only",
                "Record only the packet/context actually received as acknowledged",
                "distinct brief and report paths",
            ],
            "templates/task-continuation.md": [
                "the stage-1 recipient receives only its neutral packet",
                "Cold-start recovery preserves the disclosure stage",
                "After disclosure, continue targeted review as informed work",
            ],
            "templates/task-receipt.md": [
                "## Review context (when relevant)",
                "inherited or accidental context exposure and timing",
                "evidence and reason for each disposition or severity change",
                "acknowledge only context actually received",
            ],
        }
        for source, markers in contracts.items():
            text = (ROOT / source).read_text(encoding="utf-8")
            for marker in markers:
                with self.subTest(source=source, marker=marker):
                    self.assertIn(marker, text)

    def test_cold_start_behavioral_scenarios_cover_failure_paths(self):
        text = (ROOT / "tests/behavioral-scenarios.md").read_text(encoding="utf-8")
        for scenario in range(1, 13):
            with self.subTest(scenario=scenario):
                self.assertIn(f"| CR{scenario} |", text)
        qa = (ROOT / "references/05-qa.md").read_text(encoding="utf-8")
        self.assertIn("before comparing it with the Executor's test list", qa)
        context = (ROOT / "references/01-context-brief.md").read_text(encoding="utf-8")
        self.assertIn("separate from hypotheses and evaluative narrative", context)

    def test_parallel_review_reports_do_not_start_premature_revision_rounds(self):
        cold = (ROOT / "references/17-cold-start-review.md").read_text(encoding="utf-8")
        for marker in (
            "## Gate conclusion and revision timing",
            "Both briefs name the reconciliation owner",
            "label both initial reports provisional",
            "Keep the task In Review",
            "Act on credible safety hazards immediately",
            "Needs Revision -> In Progress -> In Review",
            "count evidence-only reassessment as an implementation correction",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, cold)
        state = (ROOT / "references/11-task-state-machine.md").read_text(encoding="utf-8")
        self.assertIn("initial reports are provisional until reconciliation", state)
        self.assertIn("start a revision round when corrective work is dispatched", state)
        reviewer = (ROOT / "references/04-reviewer.md").read_text(encoding="utf-8")
        self.assertIn("labels its initial conclusion provisional", reviewer)

    def test_project_acceptance_requires_all_required_deliveries(self):
        text = (ROOT / "references/11-task-state-machine.md").read_text(encoding="utf-8")
        row = next(line for line in text.splitlines() if line.startswith("| Acceptance |"))
        self.assertIn("All required delivery tasks are Completed", row)
        for state in ("TODO", "Blocked", "In Progress", "In Review", "Needs Revision",
                      "QA Pending", "Awaiting Acceptance"):
            self.assertIn(state, row)
        self.assertIn("Unscheduled required work also prevents entry", text)
        self.assertIn("a Cancelled task alone does not remove the requirement", text)
        self.assertIn("return to In Progress before dispatching that work", text)


if __name__ == "__main__":
    unittest.main()
