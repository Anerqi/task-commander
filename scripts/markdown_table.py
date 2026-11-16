"""Section and cell parsing shared by the status validator and display renderer.

This handles the project's pipe tables, not arbitrary Markdown documents.
"""

import re
from collections.abc import Iterator


def parse_markdown_sections(content: str) -> list[dict]:
    """Read heading metadata and direct bodies, excluding fenced examples.

    Any subsequent heading ends the direct body, including a nested heading.
    Parent names refer to the containing level-two section. This distinguishes
    attention subsections from nested historical tables with the same name.
    """
    title = None
    heading_level = None
    parent = None
    current_parent = None
    sections = []
    body = []
    fence_character = None
    fence_length = 0
    for line in content.splitlines(keepends=True):
        stripped = line.rstrip("\r\n")
        if fence_character is not None:
            if re.fullmatch(r" {0,3}" + re.escape(fence_character)
                            + "{" + str(fence_length) + r",}[ \t]*", stripped):
                fence_character = None
            continue
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", stripped)
        if fence and not (fence.group(1)[0] == "`" and "`" in fence.group(2)):
            fence_character = fence.group(1)[0]
            fence_length = len(fence.group(1))
            continue
        heading = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|[ \t]*)$", stripped)
        if heading:
            if title is not None:
                sections.append({'level': heading_level, 'title': title,
                                 'parent': parent, 'body': ''.join(body)})
            heading_level = len(heading.group(1))
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(2) or "").strip()
            parent = current_parent if heading_level > 2 else None
            if heading_level < 2:
                current_parent = None
            elif heading_level == 2:
                current_parent = title
            body = []
        elif title is not None:
            body.append(line)
    if title is not None:
        sections.append({'level': heading_level, 'title': title,
                         'parent': parent, 'body': ''.join(body)})
    return sections


def iter_markdown_sections(content: str, level: int | None = None) -> Iterator[tuple[str, str]]:
    """Yield matching heading titles and their direct bodies."""
    for section in parse_markdown_sections(content):
        if level is None or level == section['level']:
            yield section['title'], section['body']


def extract_sections(content: str, title: str, allowed_levels: tuple[int, ...]) -> list[dict]:
    """Select section records without losing nesting or direct-body boundaries."""
    return [section for section in parse_markdown_sections(content)
            if section['title'] == title and section['level'] in allowed_levels]


def find_markdown_sections(content: str, title: str, level: int | None = None) -> list[str]:
    """Return all matching direct bodies, retaining duplicates for validation."""
    return [body for heading, body in iter_markdown_sections(content, level) if heading == title]


def is_separator_row(cells: list[str]) -> bool:
    """Recognize a row made entirely of Markdown alignment cells."""
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def split_markdown_row(line: str) -> list[str]:
    """Split unescaped pipes; preserve empty cells and optional outer borders.

    An odd backslash run escapes a pipe. Only that pipe's escape is decoded;
    other backslashes are retained, rather than interpreting full Markdown.
    """
    line = line.strip()
    cells, current, backslashes = [], [], 0
    for character in line:
        if character == "|" and backslashes % 2 == 0:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        backslashes = backslashes + 1 if character == "\\" else 0
    cells.append("".join(current).strip())
    if line.startswith("|"):
        cells = cells[1:]
    # An escaped final pipe is cell content, not a closing border.
    if line.endswith("|") and not current:
        cells = cells[:-1]
    return [cell.replace("\\|", "|") for cell in cells]
