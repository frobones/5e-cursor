"""
Service for serving project documentation from the docs/ directory.
"""

import re
from pathlib import Path

from web.models.docs import DocDetail, DocListItem


def get_docs_dir() -> Path:
    """Get the docs directory at repository root."""
    return Path(__file__).parent.parent.parent.parent / "docs"


def _slug_from_path(path: Path) -> str:
    """Return slug (filename without .md) for a doc path."""
    return path.stem


def _title_from_content(content: str, fallback_slug: str) -> str:
    """Extract title from first markdown H1, or derive from slug."""
    match = re.match(r"^#\s+(.+)$", content.strip(), re.MULTILINE)
    if match:
        return match.group(1).strip()
    # Fallback: "00-guide" -> "Guide", "01-introduction" -> "Introduction"
    parts = fallback_slug.split("-", 1)
    if len(parts) == 2 and parts[0].isdigit():
        return parts[1].replace("-", " ").title()
    return fallback_slug.replace("-", " ").title()


class DocsService:
    """Service for reading documentation files."""

    def __init__(self) -> None:
        """Initialize with docs directory."""
        self.docs_dir = get_docs_dir()

    def list_docs(self) -> list[DocListItem]:
        """List all markdown files in docs/, sorted by filename (00- first)."""
        if not self.docs_dir.exists():
            return []
        items = []
        for path in sorted(self.docs_dir.glob("*.md")):
            slug = _slug_from_path(path)
            content = path.read_text(encoding="utf-8")
            title = _title_from_content(content, slug)
            items.append(DocListItem(slug=slug, title=title))
        return items

    def get_doc(self, slug: str) -> DocDetail | None:
        """Get a single doc by slug (filename without .md). Returns None if not found."""
        # Restrict to safe slug (no path traversal): letters, digits, hyphens only
        if not re.match(r"^[a-zA-Z0-9_-]+$", slug) or ".." in slug:
            return None
        path = self.docs_dir / f"{slug}.md"
        if not path.is_file():
            return None
        content = path.read_text(encoding="utf-8")
        title = _title_from_content(content, slug)
        return DocDetail(slug=slug, title=title, content=content)
