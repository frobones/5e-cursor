"""
Search-related Pydantic models.
"""

from pydantic import BaseModel
from typing import Optional


class SearchResult(BaseModel):
    """Single search result."""

    name: str
    slug: str
    type: str
    category: str  # "campaign" or "reference"
    excerpt: Optional[str] = None
    path: str


class SearchResponse(BaseModel):
    """Search response with grouped results."""

    query: str
    total: int
    results: list[SearchResult]
    by_type: dict[str, list[SearchResult]]
