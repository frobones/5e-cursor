"""
Reference data API endpoints.

Provides endpoints for browsing spells, creatures, items, and other reference data.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from web.models.reference import ReferenceIndex, ReferenceListItem, ReferenceDetail
from web.services.reference import ReferenceService

router = APIRouter()


class PaginatedReferenceResponse(BaseModel):
    """Paginated reference list response."""

    items: list[ReferenceListItem]
    total: int
    offset: int
    limit: int
    has_more: bool


@router.get("/reference", response_model=ReferenceIndex)
async def get_reference_index() -> ReferenceIndex:
    """Get reference data index with statistics."""
    service = ReferenceService()
    return service.get_index()


@router.get("/reference/search", response_model=list[ReferenceListItem])
async def search_reference(
    q: str = Query(..., description="Search query"),
    type: Optional[str] = Query(None, description="Filter by type (spells, creatures, items)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
) -> list[ReferenceListItem]:
    """Search reference data by name."""
    service = ReferenceService()
    return service.search(query=q, ref_type=type, limit=limit)


@router.get("/reference/{ref_type}", response_model=PaginatedReferenceResponse)
async def list_reference_by_type(
    ref_type: str,
    level: Optional[int] = Query(None, description="Filter spells by level"),
    cr: Optional[str] = Query(None, description="Filter creatures by CR"),
    rarity: Optional[str] = Query(None, description="Filter items by rarity"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=2000, description="Maximum results per page"),
) -> PaginatedReferenceResponse:
    """List reference data by type with optional filters and pagination."""
    service = ReferenceService()
    return service.list_by_type(
        ref_type=ref_type,
        level=level,
        cr=cr,
        rarity=rarity,
        offset=offset,
        limit=limit,
    )


@router.get("/reference/{ref_type}/{slug:path}", response_model=ReferenceDetail)
async def get_reference_detail(ref_type: str, slug: str) -> ReferenceDetail:
    """Get full reference content by type and slug.
    
    The slug can contain multiple path segments (e.g., gear/backpack).
    """
    service = ReferenceService()
    detail = service.get_detail(ref_type=ref_type, slug=slug)
    if not detail:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Reference not found: {ref_type}/{slug}")
    return detail
