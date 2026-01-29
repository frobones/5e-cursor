"""
Markdown output generation utilities.

Provides consistent formatting for campaign and reference markdown files.
"""

import re
from datetime import date
from typing import Any


def slugify(name: str) -> str:
    """Convert a name to a URL-safe slug.

    Args:
        name: The name to convert (e.g., "Meilin Starwell")

    Returns:
        URL-safe slug (e.g., "meilin-starwell")
    """
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def heading(text: str, level: int = 1) -> str:
    """Generate a markdown heading.

    Args:
        text: Heading text
        level: Heading level (1-6)

    Returns:
        Markdown heading string
    """
    return f"{'#' * level} {text}\n"


def bold(text: str) -> str:
    """Wrap text in bold markers."""
    return f"**{text}**"


def italic(text: str) -> str:
    """Wrap text in italic markers."""
    return f"*{text}*"


def link(text: str, url: str) -> str:
    """Generate a markdown link.

    Args:
        text: Link text
        url: Link URL or path

    Returns:
        Markdown link string
    """
    return f"[{text}]({url})"


def bullet_list(items: list[str], indent: int = 0) -> str:
    """Generate a markdown bullet list.

    Args:
        items: List of items
        indent: Number of spaces to indent

    Returns:
        Markdown bullet list string
    """
    prefix = " " * indent
    return "\n".join(f"{prefix}- {item}" for item in items)


def numbered_list(items: list[str]) -> str:
    """Generate a markdown numbered list.

    Args:
        items: List of items

    Returns:
        Markdown numbered list string
    """
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))


def table(headers: list[str], rows: list[list[str]]) -> str:
    """Generate a markdown table.

    Args:
        headers: List of column headers
        rows: List of rows, each row is a list of cell values

    Returns:
        Markdown table string
    """
    if not headers:
        return ""

    # Header row
    header_row = "| " + " | ".join(headers) + " |"

    # Separator row
    separator = "| " + " | ".join("-" * max(3, len(h)) for h in headers) + " |"

    # Data rows
    data_rows = []
    for row in rows:
        # Pad row to match header length
        padded = list(row) + [""] * (len(headers) - len(row))
        data_rows.append("| " + " | ".join(str(cell) for cell in padded[:len(headers)]) + " |")

    return "\n".join([header_row, separator] + data_rows)


def code_block(code: str, language: str = "") -> str:
    """Generate a markdown code block.

    Args:
        code: Code content
        language: Language for syntax highlighting

    Returns:
        Markdown code block string
    """
    return f"```{language}\n{code}\n```"


def inline_code(text: str) -> str:
    """Wrap text in inline code markers."""
    return f"`{text}`"


def blockquote(text: str) -> str:
    """Generate a markdown blockquote.

    Args:
        text: Quote content (can be multiline)

    Returns:
        Markdown blockquote string
    """
    lines = text.split("\n")
    return "\n".join(f"> {line}" for line in lines)


def horizontal_rule() -> str:
    """Generate a markdown horizontal rule."""
    return "---\n"


def metadata_block(fields: dict[str, str]) -> str:
    """Generate a metadata block with key-value pairs.

    Args:
        fields: Dictionary of field names to values

    Returns:
        Formatted metadata block
    """
    lines = []
    for key, value in fields.items():
        lines.append(f"{bold(key)}: {value}  ")
    return "\n".join(lines)


def frontmatter(fields: dict[str, Any]) -> str:
    """Generate YAML frontmatter.

    Args:
        fields: Dictionary of frontmatter fields

    Returns:
        YAML frontmatter string
    """
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'true' if value else 'false'}")
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines)


def relative_link(from_path: str, to_path: str) -> str:
    """Calculate a relative path from one file to another.

    Args:
        from_path: Path of the file containing the link
        to_path: Path of the file being linked to

    Returns:
        Relative path string
    """
    from pathlib import Path

    from_parts = Path(from_path).parent.parts
    to_parts = Path(to_path).parts

    # Find common prefix
    common_length = 0
    for f, t in zip(from_parts, to_parts):
        if f == t:
            common_length += 1
        else:
            break

    # Build relative path
    up_count = len(from_parts) - common_length
    remaining = to_parts[common_length:]

    parts = [".."] * up_count + list(remaining)
    return "/".join(parts) if parts else "."


def iso_date() -> str:
    """Return today's date in ISO format."""
    return date.today().isoformat()


def session_filename(session_number: int) -> str:
    """Generate a session filename with zero-padded number.

    Args:
        session_number: Session number

    Returns:
        Filename like "session-001.md"
    """
    return f"session-{session_number:03d}.md"
