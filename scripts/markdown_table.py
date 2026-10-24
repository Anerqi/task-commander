"""Cell parsing shared by the status validator and display renderer.

This handles the project's pipe tables, not arbitrary Markdown documents.
"""

import re


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
