"""Status sections stop at headings and ignore fenced examples."""

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "status_markdown", ROOT / "scripts" / "markdown_table.py")
MARKDOWN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MARKDOWN)


class MarkdownSectionTests(unittest.TestCase):
    def test_nested_section_stops_before_sibling_table(self):
        content = ("## Coordination\nPolicy\n### Needs you now\n| 01 | Why? | Reply |\n"
                   "### Active windows\n| unrelated | table |\n")
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Needs you now"),
                         ["| 01 | Why? | Reply |\n"])

    def test_legacy_section_and_eof(self):
        content = "## Needs you now\n| 01 | Why? | Reply |"
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Needs you now"),
                         ["| 01 | Why? | Reply |"])

    def test_empty_and_duplicate_sections_are_preserved_for_validation(self):
        content = "## Needs you now\n## Other\nText\n### Needs you now\n"
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Needs you now"),
                         ["", ""])

    def test_fenced_examples_are_not_headings_or_data(self):
        for fence in ("```", "~~~~"):
            with self.subTest(fence=fence):
                content = (f"## Needs you now\n{fence}markdown\n"
                           "## Task list\n| fake | row |\n"
                           f"{fence}\n| real | row |\n## End\n")
                self.assertEqual(
                    MARKDOWN.find_markdown_sections(content, "Needs you now"),
                    ["| real | row |\n"])

    def test_shorter_or_different_fence_cannot_close_code(self):
        content = ("## Needs you now\n````\n```\n~~~\n"
                   "## Fake\n````\nreal\n")
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Needs you now"),
                         ["real\n"])

    def test_heading_spacing_closing_hashes_and_case(self):
        content = "   ### Needs you now ###\nreal\n##Other\ntext\n## End\n"
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Needs you now"),
                         ["real\n##Other\ntext\n"])
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "needs you now"), [])

    def test_level_filter_keeps_direct_boundaries_and_ignores_history(self):
        content = ("## Task list\ncurrent\n### Example\nexample\n"
                   "## Status history\n### Task list\npast\n")
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Task list", level=2),
                         ["current\n"])
        self.assertEqual(MARKDOWN.find_markdown_sections(content, "Task list", level=3),
                         ["past\n"])

    def test_attention_and_history_keep_distinct_parents(self):
        content = ("## Needs you now\nquestion\n### Blocked\ncurrent\n"
                   "## Status history\n### Blocked\npast\n")
        records = MARKDOWN.extract_sections(content, "Blocked", (2, 3))
        self.assertEqual([section['parent'] for section in records],
                         ["Needs you now", "Status history"])
        self.assertEqual([section['body'] for section in records], ["current\n", "past\n"])

    def test_fenced_parent_does_not_reparent_real_sections(self):
        content = ("## Needs you now\n```md\n## Status history\n```\n"
                   "### Blocked\ncurrent\n")
        record, = MARKDOWN.extract_sections(content, "Blocked", (3,))
        self.assertEqual(record['parent'], "Needs you now")
