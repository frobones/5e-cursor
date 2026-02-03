"""
Documentation Pydantic models.
"""

from pydantic import BaseModel


class DocListItem(BaseModel):
    """Documentation file summary."""

    slug: str
    title: str


class DocDetail(BaseModel):
    """Full documentation content."""

    slug: str
    title: str
    content: str
