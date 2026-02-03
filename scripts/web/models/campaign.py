"""
Campaign-level Pydantic models.
"""

from pydantic import BaseModel
from typing import Optional


class CampaignStats(BaseModel):
    """Statistics about campaign entities."""

    npcs: int
    locations: int
    sessions: int
    encounters: int
    party_size: int


class CampaignOverview(BaseModel):
    """Campaign overview information."""

    name: str
    setting: Optional[str] = None
    current_session: int
    created: Optional[str] = None
    stats: CampaignStats
