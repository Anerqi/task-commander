"""Section and cell parsing shared by the status validator and display renderer.

This handles the project's pipe tables, not arbitrary Markdown documents.
"""

import re
from collections.abc import Iterator


def iter_markdown_sections(content: str, level: int | None = None) -> Iterator[tuple[str, str]]:
    """Yield ATX heading titles and their direct bodies, excluding fenced code.

    Any subsequent heading ends the direct body, including a nested heading.
    The optional level filter selects authoritative tables without changing
    body boundaries. Nested historical tables remain separate sections.
    """
    title = None
    heading_level = None
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
            if title is not None and (level is None or level == heading_level):
                yield title, "".join(body)
            heading_level = len(heading.group(1))
            title = re.sub(r"[ \t]+#+[ \t]*$", "", heading.group(2) or "").strip()
            body = []
        elif title is not None:
            body.append(line)
    if title is not None and (level is None or level == heading_level):
        yield title, "".join(body)


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
