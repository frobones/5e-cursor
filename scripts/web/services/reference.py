"""
Reference data service for spells, creatures, items, etc.
"""

import json
import re
from pathlib import Path
from typing import Optional, Any

from web.models.reference import ReferenceIndex, ReferenceListItem, ReferenceDetail
from web.services.campaign import get_repo_root


class ReferenceService:
    """Service for reference data operations."""

    def __init__(self) -> None:
        """Initialize the reference service."""
        self.books_dir = get_repo_root() / "books"
        self.reference_dir = self.books_dir / "reference"
        self._index: Optional[dict] = None

    def _load_index(self) -> dict:
        """Load the reference index."""
        if self._index is not None:
            return self._index

        index_path = self.books_dir / "reference-index.json"
        if not index_path.exists():
            return {"total_entries": 0, "entries": [], "by_type": {}}

        with open(index_path, encoding="utf-8") as f:
            self._index = json.load(f)
            return self._index

    def get_index(self) -> ReferenceIndex:
        """Get reference data index statistics."""
        index = self._load_index()

        by_type = {}
        if "by_type" in index:
            by_type = {k: len(v) for k, v in index["by_type"].items()}

        return ReferenceIndex(
            total_entries=index.get("total_entries", 0),
            by_type=by_type,
        )

    def search(
        self,
        query: str,
        ref_type: Optional[str] = None,
        limit: int = 50,
    ) -> list[ReferenceListItem]:
        """Search reference data by name."""
        index = self._load_index()
        entries = index.get("entries", [])

        query_lower = query.lower()
        results = []

        for entry in entries:
            name = entry.get("name", "")
            entry_type = entry.get("type", "")

            # Filter by type if specified
            if ref_type and entry_type != ref_type:
                continue

            # Match by name
            if query_lower in name.lower():
                results.append(self._entry_to_list_item(entry))

            if len(results) >= limit:
                break

        return results

    def list_by_type(
        self,
        ref_type: str,
        level: Optional[int] = None,
        cr: Optional[str] = None,
        rarity: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> dict:
        """List reference data by type with optional filters and pagination."""
        index = self._load_index()
        entries = index.get("entries", [])

        # Filter entries first
        filtered = []
        for entry in entries:
            if entry.get("type") != ref_type:
                continue

            # Apply filters
            if level is not None and entry.get("level") != level:
                continue
            if cr is not None and entry.get("cr") != cr:
                continue
            if rarity is not None and entry.get("rarity", "").lower() != rarity.lower():
                continue

            filtered.append(entry)

        total = len(filtered)

        # Apply pagination
        paginated = filtered[offset : offset + limit]
        items = [self._entry_to_list_item(entry) for entry in paginated]

        return {
            "items": items,
            "total": total,
            "offset": offset,
            "limit": limit,
            "has_more": offset + limit < total,
        }

    def _get_slug_from_path(self, entry_path: str, ref_type: str) -> str:
        """Extract slug from entry path, handling nested directories.
        
        For path "reference/equipment/gear/backpack.md" with type "equipment",
        returns "gear/backpack".
        """
        if not entry_path:
            return ""
        
        path = Path(entry_path)
        # Remove .md extension
        path_without_ext = str(path.with_suffix(""))
        
        # Find the type directory and get everything after it
        parts = path_without_ext.split("/")
        try:
            type_idx = parts.index(ref_type)
            # Everything after the type directory is the slug
            slug_parts = parts[type_idx + 1:]
            return "/".join(slug_parts)
        except ValueError:
            # Type not in path, just use the stem
            return path.stem

    def get_detail(self, ref_type: str, slug: str) -> Optional[ReferenceDetail]:
        """Get full reference content by type and slug."""
        index = self._load_index()
        entries = index.get("entries", [])

        # Find matching entry
        entry = None
        for e in entries:
            if e.get("type") == ref_type:
                entry_path = e.get("path", "")
                entry_slug = self._get_slug_from_path(entry_path, ref_type)

                if entry_slug == slug:
                    entry = e
                    break

        if not entry:
            return None

        # Load content from file
        content_path = self.books_dir / entry.get("path", "")
        if not content_path.exists():
            return None

        content = content_path.read_text(encoding="utf-8")

        return ReferenceDetail(
            name=entry.get("name", ""),
            slug=slug,
            type=ref_type,
            source=entry.get("source"),
            content=content,
            metadata=self._extract_metadata(entry),
        )

    def _entry_to_list_item(self, entry: dict) -> ReferenceListItem:
        """Convert index entry to list item."""
        path = entry.get("path", "")
        ref_type = entry.get("type", "")
        
        # Handle species-traits: link to parent species with anchor
        if ref_type == "species-traits":
            parent_path = entry.get("path", "")
            anchor = entry.get("anchor", "")
            # For traits, the slug is the parent species slug
            slug = self._get_slug_from_path(parent_path, "species")
            if anchor:
                slug = f"{slug}#{anchor}"
            # Display as "[trait] (Species)" for clarity
            name = entry.get("name", "")
            parent = entry.get("parent_species", "")
            display_name = f"{name} ({parent} trait)" if parent else name
            
            return ReferenceListItem(
                name=display_name,
                slug=slug,
                type="species",  # Link as species for routing
                source=entry.get("source"),
                metadata=self._extract_metadata(entry),
            )
        
        slug = self._get_slug_from_path(path, ref_type)

        return ReferenceListItem(
            name=entry.get("name", ""),
            slug=slug,
            type=ref_type,
            source=entry.get("source"),
            metadata=self._extract_metadata(entry),
        )

    def _extract_metadata(self, entry: dict) -> dict[str, Any]:
        """Extract type-specific metadata from entry."""
        metadata = {}

        # Common fields
        for key in ["level", "school", "cr", "type", "rarity", "casting_time", "range", "duration"]:
            if key in entry:
                metadata[key] = entry[key]

        return metadata
