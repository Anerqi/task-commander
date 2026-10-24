"""Focused tests for scripts/validate-knowledge.py (the optional knowledge layer)."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-knowledge.py"

LOG_DESCENDING = """# Project Knowledge Log

## 2026-02-10 — Newest entry
- Recorded a decision.

## 2026-01-05 - Older entry
- Recorded an older result.
"""


class KnowledgeValidatorTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="_tmp_knowledge_tests_")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.environment = dict(os.environ, PYTHONIOENCODING="utf-8",
                                PYTHONDONTWRITEBYTECODE="1")

    def make_project(self, name):
        root = self.directory / name
        root.mkdir()
        return root

    def write(self, path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")

    def add_log(self, root, content):
        self.write(root / "knowledge" / "LOG.md", content)

    def add_topic(self, root, name, content):
        self.write(root / "knowledge" / "topics" / name, content)

    def topic_content(self, omit=(), **overrides):
        fields = {
            "type": "project_topic",
            "status": "active",
            "summary": "A concise topic summary",
            "tags": "[alpha, beta]",
            "contains": "[lesson, procedure]",
            "created": "2026-01-01",
            "updated": "2026-02-01",
            "authoring_mode": "ai_generated",
        }
        fields.update(overrides)
        lines = [f"{key}: {value}" for key, value in fields.items()
                 if key not in omit]
        return "---\n" + "\n".join(lines) + "\n---\n\n# Topic title\n\n" \
               "Real body content with a stable conclusion.\n"

    def run_cli(self, *arguments, cwd=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            cwd=str(cwd or self.directory), env=self.environment,
            capture_output=True, text=True, encoding="utf-8", timeout=30,
            check=False,
        )

    def run_for(self, root, *arguments):
        return self.run_cli("--project-root", root, *arguments)

    def payload(self, process):
        self.assertEqual(process.stderr, "")
        self.assertTrue(process.stdout.endswith("\n"))
        return json.loads(process.stdout)

    def assert_valid(self, process, topic_count=0):
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
        data = self.payload(process)
        self.assertTrue(data["valid"], data)
        self.assertEqual(data["errors"], [])
        self.assertEqual(data["topic_count"], topic_count)
        return data

    def assert_invalid(self, process, *expected_fragments):
        self.assertEqual(process.returncode, 1, process.stdout + process.stderr)
        data = self.payload(process)
        self.assertFalse(data["valid"], data)
        self.assertTrue(data["errors"], data)
        for fragment in expected_fragments:
            self.assertTrue(any(fragment in error for error in data["errors"]),
                            data)
        return data

    def test_valid_layer_with_log_and_topic(self):
        root = self.make_project("valid-layer")
        self.add_log(root, LOG_DESCENDING)
        self.add_topic(root, "state-machine.md", self.topic_content())
        process = self.run_for(root)
        data = self.assert_valid(process, topic_count=1)
        self.assertEqual(data["warnings"], [])
        self.assertTrue(data["log_present"])
        self.assertEqual(data["project_root"], os.path.realpath(str(root)))
        self.assertEqual(data["knowledge_dir"], "knowledge")
        self.assertEqual(set(data), {
            "valid", "project_root", "knowledge_dir", "log_present",
            "topic_count", "errors", "warnings",
        })

    def test_absent_layer_is_optional_without_require(self):
        root = self.make_project("absent-layer")
        data = self.assert_valid(self.run_for(root))
        self.assertFalse(data["log_present"])
        self.assertTrue(any("not initialized" in warning
                            for warning in data["warnings"]), data)

    def test_absent_layer_is_invalid_with_require(self):
        root = self.make_project("required-layer")
        data = self.assert_invalid(self.run_for(root, "--require"),
                                   "required but not found")
        self.assertFalse(data["log_present"])
        self.assertEqual(data["warnings"], [])

    def test_missing_unclosed_duplicate_key_and_duplicate_block_frontmatter(self):
        cases = {
            "missing": ("# No frontmatter\n\nBody only.\n",
                        "missing frontmatter"),
            "unclosed": ("---\ntype: project_topic\nstatus: active\n",
                         "unclosed frontmatter"),
            "duplicate-key": (
                self.topic_content().replace(
                    "status: active\n", "status: active\nstatus: archived\n", 1),
                "duplicate frontmatter key: status"),
            "duplicate-block": (
                self.topic_content().replace(
                    "\n---\n\n# Topic title",
                    "\n---\n---\ntype: project_topic\nstatus: active\n---\n\n# Topic title", 1),
                "duplicate frontmatter block"),
            "malformed-line": (
                self.topic_content().replace(
                    "status: active\n", "status active\n", 1),
                "malformed frontmatter line"),
            "missing-field": (
                self.topic_content(omit=("authoring_mode",)),
                "missing required field: authoring_mode"),
        }
        for label, (content, fragment) in cases.items():
            with self.subTest(label=label):
                root = self.make_project("frontmatter-" + label)
                self.add_topic(root, "topic.md", content)
                self.assert_invalid(self.run_for(root), fragment)

    def test_invalid_enum_values(self):
        cases = {
            "type": ({"type": "project_note"}, "invalid type"),
            "status": ({"status": "done"}, "invalid status"),
            "contains": ({"contains": "[lesson, anecdote]"},
                         "invalid contains value"),
            "authoring_mode": ({"authoring_mode": "machine"},
                               "invalid authoring_mode"),
            "graduation_status": ({"graduation_status": "ready"},
                                  "invalid graduation_status"),
        }
        for label, (overrides, fragment) in cases.items():
            with self.subTest(field=label):
                root = self.make_project("enum-" + label)
                self.add_topic(root, "topic.md", self.topic_content(**overrides))
                self.assert_invalid(self.run_for(root), fragment)

    def test_log_dates_must_be_newest_first(self):
        ascending = """# Log

## 2026-01-01 - Older first
- Entry.

## 2026-02-01 - Newer second
- Entry.
"""
        root = self.make_project("ascending-log")
        self.add_log(root, ascending)
        self.assert_invalid(self.run_for(root), "newest-first")

        descending = """# Log

## 2026-04-04 · Dot separator
- Entry.

## 2026-03-03 — Em dash separator
- Entry.

## 2026-02-02 - Hyphen separator
- Entry.

## 2026-01-01: Colon separator
- Entry.
"""
        root = self.make_project("descending-log")
        self.add_log(root, descending)
        data = self.assert_valid(self.run_for(root))
        self.assertEqual(data["warnings"], [])

    def test_empty_topic_body_is_a_warning_only(self):
        variants = {
            "no-body": self.topic_content().split("\n# Topic title", 1)[0],
            "title-and-comment": self.topic_content().replace(
                "\nReal body content with a stable conclusion.\n",
                "\n<!-- only a comment -->\n", 1),
        }
        for label, content in variants.items():
            with self.subTest(label=label):
                root = self.make_project("empty-body-" + label)
                self.add_topic(root, "topic.md", content)
                data = self.assert_valid(self.run_for(root), topic_count=1)
                self.assertTrue(any("empty topic shell" in warning
                                    for warning in data["warnings"]), data)

    def test_list_and_quoted_value_parsing(self):
        root = self.make_project("lists")
        self.add_topic(root, "quoted.md", self.topic_content(
            type='"project_topic"',
            status='"active"',
            summary='"Quoted: summary with a colon"',
            tags='[alpha, "beta, gamma"]',
            contains='[lesson, procedure]',
            authoring_mode='"ai_generated"',
        ))
        self.add_topic(root, "empty-tags.md", self.topic_content(
            tags="[]", contains="[]"))
        data = self.assert_valid(self.run_for(root), topic_count=2)
        self.assertTrue(any("contains is empty" in warning
                            for warning in data["warnings"]), data)

    def test_updated_before_created_is_invalid(self):
        root = self.make_project("date-order")
        self.add_topic(root, "topic.md", self.topic_content(
            created="2026-02-01", updated="2026-01-01"))
        self.assert_invalid(self.run_for(root), "earlier than created")

    def test_help_exits_zero(self):
        process = self.run_cli("--help")
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(process.stderr, "")
        self.assertIn("usage", process.stdout.lower())
        self.assertIn("--project-root", process.stdout)
        self.assertIn("--knowledge-dir", process.stdout)
        self.assertIn("--require", process.stdout)

    def test_defaults_run_from_project_root(self):
        root = self.make_project("defaults")
        self.add_log(root, LOG_DESCENDING)
        self.add_topic(root, "topic.md", self.topic_content())
        process = self.run_cli(cwd=root)
        data = self.assert_valid(process, topic_count=1)
        self.assertEqual(data["project_root"], os.path.realpath(str(root)))
        self.assertEqual(data["knowledge_dir"], "knowledge")

    def test_custom_knowledge_directory_name(self):
        root = self.make_project("custom-dir")
        self.write(root / "kb" / "LOG.md", LOG_DESCENDING)
        self.write(root / "kb" / "topics" / "topic.md", self.topic_content())
        data = self.assert_valid(
            self.run_for(root, "--knowledge-dir", "kb"), topic_count=1)
        self.assertTrue(data["log_present"])
        self.assertEqual(data["knowledge_dir"], "kb")

    def test_knowledge_dir_without_log_or_topics_is_a_warning(self):
        root = self.make_project("empty-layer")
        (root / "knowledge").mkdir()
        data = self.assert_valid(self.run_for(root))
        self.assertFalse(data["log_present"])
        self.assertTrue(any("LOG.md is missing" in warning
                            for warning in data["warnings"]), data)

    def test_log_without_dated_entries_and_entry_warnings(self):
        log = """# Log

## 2026-03-03
- A dated entry without a title.

## 2026-02-02 — Long entry
""" + "\n".join(f"- body line {index}" for index in range(1, 22)) + "\n"
        root = self.make_project("log-warnings")
        self.add_log(root, log)
        data = self.assert_valid(self.run_for(root))
        self.assertTrue(any("has no title" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("non-empty body lines" in warning
                            for warning in data["warnings"]), data)

        root = self.make_project("undated-log")
        self.add_log(root, "# Log\n\nNo dated headings here.\n")
        data = self.assert_valid(self.run_for(root))
        self.assertTrue(any("no dated entries" in warning
                            for warning in data["warnings"]), data)

    def test_topic_filename_summary_length_and_empty_contains_warnings(self):
        root = self.make_project("topic-warnings")
        self.add_topic(root, "Not-Kebab.md", self.topic_content(
            summary="x" * 201, contains="[]"))
        data = self.assert_valid(self.run_for(root), topic_count=1)
        self.assertTrue(any("kebab-case" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("summary exceeds" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("contains is empty" in warning
                            for warning in data["warnings"]), data)

    def test_roadmap_and_cited_are_light_warnings(self):
        root = self.make_project("optional-files")
        self.write(root / "knowledge" / "ROADMAP.md",
                   "# Roadmap\n\n## Milestones\n\n- [ ] Something\n")
        self.write(root / "knowledge" / "Cited.md",
                   "# Cited\n\n<!-- no adopted sources yet -->\n")
        data = self.assert_valid(self.run_for(root))
        self.assertTrue(any("ROADMAP.md" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("Cited.md" in warning
                            for warning in data["warnings"]), data)

        root = self.make_project("optional-valid")
        self.write(root / "knowledge" / "ROADMAP.md",
                   "# Roadmap\n\n**Current focus**: ship the validator\n")
        self.write(root / "knowledge" / "Cited.md",
                   "# Cited\n\n| Date | Source | Conclusion |\n|---|---|---|\n")
        data = self.assert_valid(self.run_for(root))
        self.assertFalse(any("ROADMAP.md" in warning
                             for warning in data["warnings"]), data)
        self.assertFalse(any("Cited.md" in warning
                             for warning in data["warnings"]), data)

    def test_only_flat_lowercase_markdown_files_are_topics(self):
        root = self.make_project("topic-count")
        self.add_topic(root, "real.md", self.topic_content())
        self.write(root / "knowledge" / "topics" / "notes.txt", "not a topic")
        self.write(root / "knowledge" / "topics" / "nested" / "deep.md",
                   self.topic_content())
        data = self.assert_valid(self.run_for(root), topic_count=1)
        self.assertTrue(data["log_present"] is False)

    def test_missing_project_root_is_reported_as_json(self):
        missing = self.directory / "does-not-exist"
        data = self.assert_invalid(self.run_for(missing), "Project root")
        self.assertEqual(data["topic_count"], 0)

    def test_encoding_errors_and_warnings(self):
        root = self.make_project("encoding-bad")
        topic = root / "knowledge" / "topics" / "bad.md"
        topic.parent.mkdir(parents=True)
        valid = self.topic_content().encode("utf-8")
        topic.write_bytes(valid + b"\xff\n")
        data = self.assert_invalid(self.run_for(root), "invalid UTF-8")
        self.assertEqual(data["topic_count"], 1)

        root = self.make_project("encoding-log")
        log = root / "knowledge" / "LOG.md"
        log.parent.mkdir(parents=True)
        log.write_bytes(b"# Log\n\n## 2026-01-01 - bad \xff\n")
        self.assert_invalid(self.run_for(root), "invalid UTF-8")

        root = self.make_project("encoding-warn")
        topic = root / "knowledge" / "topics" / "bom.md"
        topic.parent.mkdir(parents=True)
        crlf = self.topic_content().replace("\n", "\r\n").encode("utf-8")
        topic.write_bytes(b"\xef\xbb\xbf" + crlf)
        data = self.assert_valid(self.run_for(root), topic_count=1)
        self.assertTrue(any("BOM present" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("CRLF" in warning
                            for warning in data["warnings"]), data)

        root = self.make_project("encoding-log-warn")
        log = root / "knowledge" / "LOG.md"
        log.parent.mkdir(parents=True)
        log.write_bytes(b"\xef\xbb\xbf## 2026-01-01 - ok\r\n- Entry.\r\n")
        data = self.assert_valid(self.run_for(root))
        self.assertTrue(any("BOM present" in warning
                            for warning in data["warnings"]), data)
        self.assertTrue(any("CRLF" in warning
                            for warning in data["warnings"]), data)

    def test_knowledge_directory_cannot_escape_the_project_root(self):
        root = self.make_project("path-root")
        outside = self.directory / "outside"
        self.write(outside / "LOG.md", LOG_DESCENDING)
        for name in ("../outside", str(outside)):
            with self.subTest(name=name):
                data = self.assert_invalid(
                    self.run_for(root, "--knowledge-dir", name),
                    "must stay under")
                self.assertEqual(data["topic_count"], 0)

    def test_log_fences_do_not_create_or_truncate_entries(self):
        log = """# Log

## 2026-02-10 - Real entry
- Entry body.

```text
## 2026-01-01 - Fenced example, not an entry
```
"""
        root = self.make_project("log-fence")
        self.add_log(root, log)
        data = self.assert_valid(self.run_for(root))
        self.assertEqual(data["errors"], [])

    def test_body_horizontal_rule_and_prose_is_not_duplicate_frontmatter(self):
        root = self.make_project("body-rule")
        content = self.topic_content().replace(
            "\nReal body content with a stable conclusion.\n",
            "\n---\nNote: this is prose, not a second frontmatter block.\n---\n\n"
            "Real body content.\n", 1)
        self.add_topic(root, "topic.md", content)
        self.assert_valid(self.run_for(root), topic_count=1)

    def test_malformed_date_heading_is_an_error_not_ignored(self):
        root = self.make_project("bad-date")
        self.add_log(root, "# Log\n\n## 2026-01-011 - Bad date\n- Entry.\n")
        self.assert_invalid(self.run_for(root), "invalid entry date")

    def test_hashtag_body_is_content_not_an_empty_shell(self):
        root = self.make_project("hashtag-body")
        content = self.topic_content().replace(
            "Real body content with a stable conclusion.\n",
            "#task-commander is a tag, not a heading.\n", 1)
        self.add_topic(root, "topic.md", content)
        data = self.assert_valid(self.run_for(root), topic_count=1)
        self.assertFalse(any("empty topic shell" in warning
                             for warning in data["warnings"]), data)

    def test_empty_tag_items_are_invalid(self):
        root = self.make_project("empty-tags")
        self.add_topic(root, "topic.md", self.topic_content(tags="[alpha, , beta]"))
        self.assert_invalid(self.run_for(root), "tags must not contain empty items")

    def test_quoted_dates_and_require_with_existing_layer(self):
        root = self.make_project("quoted-dates")
        self.add_log(root, LOG_DESCENDING)
        self.add_topic(root, "topic.md", self.topic_content(
            created='"2026-01-01"', updated='"2026-02-01"'))
        self.assert_valid(self.run_for(root, "--require"), topic_count=1)

    def test_uppercase_markdown_is_not_counted_as_a_topic(self):
        root = self.make_project("uppercase")
        self.write(root / "knowledge" / "topics" / "TOPIC.MD",
                   self.topic_content())
        data = self.assert_valid(self.run_for(root))
        self.assertEqual(data["topic_count"], 0)

    def test_known_key_prose_is_not_duplicate_frontmatter(self):
        root = self.make_project("known-key-prose")
        content = self.topic_content().replace(
            "\nReal body content with a stable conclusion.\n",
            "\n---\ntype: this is prose, not a second frontmatter block\n---\n\n"
            "Real body content.\n", 1)
        self.add_topic(root, "topic.md", content)
        self.assert_valid(self.run_for(root), topic_count=1)

    def test_longer_fence_opener_is_not_closed_by_shorter_marker(self):
        log = """# Log

## 2026-02-10 - Real entry
- Entry body.

````text
```text
## 2026-01-011 - Fenced example, not an entry
```
````
"""
        root = self.make_project("long-fence")
        self.add_log(root, log)
        data = self.assert_valid(self.run_for(root))
        self.assertEqual(data["errors"], [])

    def test_oversized_topic_is_reported_cleanly(self):
        root = self.make_project("oversized")
        content = self.topic_content() + ("body line\n" * 250000)
        self.add_topic(root, "big.md", content)
        data = self.assert_invalid(self.run_for(root), "too large")
        self.assertEqual(data["topic_count"], 1)

    def test_topic_directory_symlink_cannot_escape(self):
        root = self.make_project("topic-symlink")
        self.add_log(root, LOG_DESCENDING)
        outside = self.directory / "outside-topics"
        outside.mkdir()
        self.write(outside / "external.md", self.topic_content())
        try:
            os.symlink(outside, root / "knowledge" / "topics",
                       target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.assert_invalid(self.run_for(root),
                            "topics/: must stay under the knowledge directory")

    @unittest.skipUnless(sys.platform == "win32", "Windows share-mode lock")
    def test_locked_file_still_returns_json(self):
        import ctypes
        from ctypes import wintypes
        root = self.make_project("locked")
        self.add_log(root, LOG_DESCENDING)
        log = root / "knowledge" / "LOG.md"
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
            wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.CloseHandle.restype = wintypes.BOOL
        handle = kernel32.CreateFileW(str(log), 0x80000000, 0, None, 3, 0, None)
        invalid = ctypes.c_void_p(-1).value
        if handle in (None, 0, -1, invalid):
            self.skipTest("could not acquire an exclusive lock")
        try:
            data = self.assert_invalid(self.run_for(root), "cannot read file")
            self.assertTrue(data["valid"] is False)
        finally:
            kernel32.CloseHandle(handle)

    @unittest.skipUnless(os.name == "posix", "surrogate filename support")
    def test_non_utf8_filename_does_not_crash_json(self):
        root = self.make_project("surrogate-name")
        self.add_log(root, LOG_DESCENDING)
        name = os.fsdecode(b"bad-\xff.md")
        path = root / "knowledge" / "topics" / name
        path.parent.mkdir(parents=True)
        path.write_text(self.topic_content(), encoding="utf-8", newline="\n")
        process = self.run_for(root)
        self.assertEqual(process.stderr, "")
        data = json.loads(process.stdout)
        self.assertTrue(data["valid"], data)
        self.assertEqual(data["topic_count"], 1)
        self.assertTrue(any("kebab-case" in warning
                            for warning in data["warnings"]), data)


if __name__ == "__main__":
    unittest.main()
