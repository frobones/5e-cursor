"""
Reference data Pydantic models.
"""

from pydantic import BaseModel
from typing import Optional, Any


class ReferenceTypeStats(BaseModel):
    """Statistics for a reference type."""

    count: int
    type: str


class ReferenceIndex(BaseModel):
    """Reference data index statistics."""

    total_entries: int
    by_type: dict[str, int]


class ReferenceListItem(BaseModel):
    """Reference item summary."""

    name: str
    slug: str
    type: str
    source: Optional[str] = None
    metadata: dict[str, Any] = {}


class ReferenceDetail(BaseModel):
    """Full reference content."""

    name: str
    slug: str
    type: str
    source: Optional[str] = None
    content: str
    metadata: dict[str, Any] = {}
