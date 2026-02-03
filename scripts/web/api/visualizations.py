"""
Visualization API endpoints.

Provides endpoints for timeline and relationship graph data.
"""

from fastapi import APIRouter

from web.models.visualizations import TimelineResponse, RelationshipGraphResponse
from web.services.visualizations import VisualizationService

router = APIRouter()


@router.get("/timeline", response_model=TimelineResponse)
async def get_timeline() -> TimelineResponse:
    """Get timeline data for visualization."""
    service = VisualizationService()
    return service.get_timeline()


@router.get("/relationships", response_model=RelationshipGraphResponse)
async def get_relationships() -> RelationshipGraphResponse:
    """Get relationship graph data for visualization."""
    service = VisualizationService()
    return service.get_relationships()
