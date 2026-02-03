"""
Search service for full-text search across campaign and reference data.
"""

from collections import defaultdict
from typing import Optional

from web.models.search import SearchResponse, SearchResult
from web.services.entities import EntityService
from web.services.reference import ReferenceService


class SearchService:
    """Service for full-text search operations."""

    def __init__(self) -> None:
        """Initialize the search service."""
        self.entity_service = EntityService()
        self.reference_service = ReferenceService()

    def search(self, query: str, limit: int = 50) -> SearchResponse:
        """Search across all campaign and reference data."""
        results: list[SearchResult] = []
        query_lower = query.lower()

        # Search campaign entities
        results.extend(self._search_npcs(query_lower))
        results.extend(self._search_locations(query_lower))
        results.extend(self._search_sessions(query_lower))
        results.extend(self._search_characters(query_lower))

        # Search reference data
        ref_results = self.reference_service.search(query, limit=limit)
        for ref in ref_results:
            # Handle species-traits: slug may contain anchor
            if "#" in ref.slug:
                # Slug is "human#resourceful", path should be "/reference/species/human#resourceful"
                path = f"/reference/{ref.type}/{ref.slug}"
            else:
                path = f"/reference/{ref.type}/{ref.slug}"
            
            results.append(
                SearchResult(
                    name=ref.name,
                    slug=ref.slug,
                    type=ref.type,
                    category="reference",
                    path=path,
                )
            )

        # Sort by relevance (exact match first, then prefix, then contains)
        def sort_key(r: SearchResult) -> tuple:
            name_lower = r.name.lower()
            if name_lower == query_lower:
                return (0, name_lower)
            elif name_lower.startswith(query_lower):
                return (1, name_lower)
            else:
                return (2, name_lower)

        results.sort(key=sort_key)
        results = results[:limit]

        # Group by type
        by_type: dict[str, list[SearchResult]] = defaultdict(list)
        for r in results:
            by_type[r.type].append(r)

        return SearchResponse(
            query=query,
            total=len(results),
            results=results,
            by_type=dict(by_type),
        )

    def _search_npcs(self, query: str) -> list[SearchResult]:
        """Search NPCs by name."""
        results = []
        for npc in self.entity_service.list_npcs():
            if query in npc.name.lower():
                results.append(
                    SearchResult(
                        name=npc.name,
                        slug=npc.slug,
                        type="npc",
                        category="campaign",
                        path=f"/npcs/{npc.slug}",
                    )
                )
        return results

    def _search_locations(self, query: str) -> list[SearchResult]:
        """Search locations by name."""
        results = []
        for loc in self.entity_service.list_locations():
            if query in loc.name.lower():
                results.append(
                    SearchResult(
                        name=loc.name,
                        slug=loc.slug,
                        type="location",
                        category="campaign",
                        path=f"/locations/{loc.slug}",
                    )
                )
        return results

    def _search_sessions(self, query: str) -> list[SearchResult]:
        """Search sessions by title."""
        results = []
        for session in self.entity_service.list_sessions():
            if query in session.title.lower():
                results.append(
                    SearchResult(
                        name=f"Session {session.number}: {session.title}",
                        slug=str(session.number),
                        type="session",
                        category="campaign",
                        path=f"/sessions/{session.number}",
                    )
                )
        return results

    def _search_characters(self, query: str) -> list[SearchResult]:
        """Search party characters by name."""
        results = []
        for char in self.entity_service.list_characters():
            if query in char.name.lower():
                results.append(
                    SearchResult(
                        name=char.name,
                        slug=char.slug,
                        type="character",
                        category="campaign",
                        path=f"/party/characters/{char.slug}",
                    )
                )
        return results
