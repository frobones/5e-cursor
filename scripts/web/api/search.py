"""
Search API endpoints.

Provides full-text search across campaign and reference data.
"""

from fastapi import APIRouter, Query

from web.models.search import SearchResponse, SearchResult
from web.services.search import SearchService

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
) -> SearchResponse:
    """Search across all campaign and reference data."""
    service = SearchService()
    return service.search(query=q, limit=limit)
