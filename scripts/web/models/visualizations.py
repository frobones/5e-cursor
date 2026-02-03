"""
Visualization Pydantic models for timeline and relationship graph.
"""

from pydantic import BaseModel
from typing import Optional


class TimelineEvent(BaseModel):
    """Single event in the timeline."""

    in_game_date: str
    day: int
    title: str
    category: str
    description: Optional[str] = None
    session_number: Optional[int] = None
    entity_path: Optional[str] = None
    entity_type: Optional[str] = None


class TimelineDay(BaseModel):
    """Events grouped by day."""

    day: int
    in_game_date: str
    events: list[TimelineEvent]


class TimelineResponse(BaseModel):
    """Timeline visualization data."""

    current_day: int
    total_events: int
    days: list[TimelineDay]


class RelationshipNode(BaseModel):
    """Node in the relationship graph."""

    id: str
    name: str
    role: Optional[str] = None


class RelationshipEdge(BaseModel):
    """Edge in the relationship graph."""

    source: str
    target: str
    type: str
    description: Optional[str] = None


class RelationshipGraphResponse(BaseModel):
    """Relationship graph visualization data."""

    nodes: list[RelationshipNode]
    edges: list[RelationshipEdge]
    mermaid: str
