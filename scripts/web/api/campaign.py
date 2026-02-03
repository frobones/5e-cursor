"""
Campaign API endpoints.

Provides campaign overview and context information.
"""

from fastapi import APIRouter, HTTPException

from web.models.campaign import CampaignOverview, CampaignStats
from web.services.campaign import CampaignService

router = APIRouter()


@router.get("/campaign", response_model=CampaignOverview)
async def get_campaign() -> CampaignOverview:
    """Get campaign overview information."""
    service = CampaignService()

    if not service.campaign_exists():
        raise HTTPException(
            status_code=404,
            detail="No campaign found. Initialize one with: python scripts/campaign/init_campaign.py",
        )

    return service.get_overview()


@router.get("/campaign/stats", response_model=CampaignStats)
async def get_campaign_stats() -> CampaignStats:
    """Get campaign entity statistics."""
    service = CampaignService()

    if not service.campaign_exists():
        raise HTTPException(status_code=404, detail="No campaign found")

    return service.get_stats()
