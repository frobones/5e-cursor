"""
Documentation API endpoints.

Serves project documentation (docs/*.md) for the Web UI.
"""

from fastapi import APIRouter, HTTPException

from web.models.docs import DocDetail, DocListItem
from web.services.docs import DocsService

router = APIRouter()


@router.get("/docs", response_model=list[DocListItem])
async def list_docs() -> list[DocListItem]:
    """List all documentation pages in reading order."""
    service = DocsService()
    return service.list_docs()


@router.get("/docs/{slug}", response_model=DocDetail)
async def get_doc(slug: str) -> DocDetail:
    """Get a single documentation page by slug (e.g. 00-guide, 01-introduction)."""
    service = DocsService()
    doc = service.get_doc(slug)
    if doc is None:
        raise HTTPException(status_code=404, detail="Documentation not found")
    return doc
