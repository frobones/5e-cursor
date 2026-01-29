"""
Reference data linking utilities.

Resolves names to reference file paths using the reference index.
"""

import json
import re
from pathlib import Path
from typing import Optional


class ReferenceLinker:
    """Links entity names to reference file paths."""

    def __init__(self, books_dir: Optional[Path] = None):
        """Initialize the linker.

        Args:
            books_dir: Path to the books directory. Defaults to books/ in repo root.
        """
        if books_dir is None:
            # Find repo root by looking for books directory
            current = Path(__file__).resolve()
            while current.parent != current:
                if (current / "books").exists():
                    books_dir = current / "books"
                    break
                current = current.parent

        if books_dir is None or not books_dir.exists():
            raise FileNotFoundError("Could not find books directory. Run 'make' to extract reference data.")

        self.books_dir = Path(books_dir)
        self.index_path = self.books_dir / "reference-index.json"

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"Reference index not found at {self.index_path}. Run 'make' to extract reference data."
            )

        self._index: dict[str, list[dict]] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load and index the reference data."""
        with open(self.index_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Build lookup by normalized name
        for entry in data.get("entries", []):
            name = entry.get("name", "")
            normalized = self._normalize(name)

            if normalized not in self._index:
                self._index[normalized] = []

            self._index[normalized].append(entry)

    def _normalize(self, name: str) -> str:
        """Normalize a name for lookup.

        Args:
            name: The name to normalize

        Returns:
            Normalized name (lowercase, no special chars)
        """
        normalized = name.lower()
        normalized = re.sub(r"[^a-z0-9\s]", "", normalized)
        normalized = re.sub(r"\s+", " ", normalized)
        return normalized.strip()

    def find(self, name: str, entry_type: Optional[str] = None) -> Optional[dict]:
        """Find a reference entry by name.

        Args:
            name: Name to search for
            entry_type: Optional type filter (spells, creatures, items, etc.)

        Returns:
            Reference entry dict or None if not found
        """
        normalized = self._normalize(name)
        entries = self._index.get(normalized, [])

        if not entries:
            return None

        if entry_type:
            filtered = [e for e in entries if e.get("type") == entry_type]
            return filtered[0] if filtered else entries[0]

        return entries[0]

    def find_path(self, name: str, entry_type: Optional[str] = None) -> Optional[str]:
        """Find the reference file path for a name.

        Args:
            name: Name to search for
            entry_type: Optional type filter

        Returns:
            Path string relative to books/ or None if not found
        """
        entry = self.find(name, entry_type)
        return entry.get("path") if entry else None

    def link(self, name: str, from_path: str, entry_type: Optional[str] = None) -> Optional[str]:
        """Generate a markdown link to a reference.

        Args:
            name: Name to link
            from_path: Path of the file containing the link (for relative path calculation)
            entry_type: Optional type filter

        Returns:
            Markdown link string or None if reference not found
        """
        ref_path = self.find_path(name, entry_type)
        if ref_path is None:
            return None

        # Calculate relative path from campaign file to books reference
        from_parts = Path(from_path).parent.parts
        full_ref_path = self.books_dir / ref_path
        to_parts = full_ref_path.parts

        # Find where paths diverge from repo root
        # Assume from_path is relative to repo root (e.g., campaign/party/characters/foo.md)
        # and ref_path is relative to books/ (e.g., reference/spells/1st-level/magic-missile.md)

        # For campaign files, we need to go up to repo root then into books/
        up_count = len(from_parts)
        relative = "../" * up_count + f"books/{ref_path}"

        return f"[{name}]({relative})"

    def link_or_text(self, name: str, from_path: str, entry_type: Optional[str] = None) -> str:
        """Generate a link if reference exists, otherwise return name with marker.

        Args:
            name: Name to link
            from_path: Path of the file containing the link
            entry_type: Optional type filter

        Returns:
            Markdown link or name with [No Reference] marker
        """
        result = self.link(name, from_path, entry_type)
        return result if result else f"{name} [No Reference]"

    def find_all(self, entry_type: str) -> list[dict]:
        """Get all entries of a specific type.

        Args:
            entry_type: Type to filter by (spells, creatures, items, etc.)

        Returns:
            List of matching entries
        """
        results = []
        for entries in self._index.values():
            for entry in entries:
                if entry.get("type") == entry_type:
                    results.append(entry)
        return results

    def search(self, query: str, entry_type: Optional[str] = None, limit: int = 10) -> list[dict]:
        """Search for entries matching a query.

        Args:
            query: Search query
            entry_type: Optional type filter
            limit: Maximum results to return

        Returns:
            List of matching entries
        """
        normalized_query = self._normalize(query)
        results = []

        for normalized_name, entries in self._index.items():
            if normalized_query in normalized_name:
                for entry in entries:
                    if entry_type is None or entry.get("type") == entry_type:
                        results.append(entry)
                        if len(results) >= limit:
                            return results

        return results


# Module-level instance for convenience
_linker: Optional[ReferenceLinker] = None


def get_linker() -> ReferenceLinker:
    """Get or create the global ReferenceLinker instance."""
    global _linker
    if _linker is None:
        _linker = ReferenceLinker()
    return _linker


def find_reference(name: str, entry_type: Optional[str] = None) -> Optional[dict]:
    """Find a reference entry by name. Convenience wrapper."""
    return get_linker().find(name, entry_type)


def link_reference(name: str, from_path: str, entry_type: Optional[str] = None) -> str:
    """Generate a markdown link to a reference. Convenience wrapper."""
    return get_linker().link_or_text(name, from_path, entry_type)
