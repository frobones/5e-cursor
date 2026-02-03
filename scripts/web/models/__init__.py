"""
Pydantic models for API requests and responses.
"""

from web.models.campaign import CampaignOverview, CampaignStats
from web.models.entities import (
    NPCListItem,
    NPCDetail,
    LocationListItem,
    LocationDetail,
    SessionListItem,
    SessionDetail,
    CharacterListItem,
    CharacterDetail,
    EncounterListItem,
    EncounterDetail,
    PartyOverview,
)
from web.models.reference import ReferenceIndex, ReferenceListItem, ReferenceDetail
from web.models.search import SearchResponse, SearchResult

__all__ = [
    "CampaignOverview",
    "CampaignStats",
    "NPCListItem",
    "NPCDetail",
    "LocationListItem",
    "LocationDetail",
    "SessionListItem",
    "SessionDetail",
    "CharacterListItem",
    "CharacterDetail",
    "EncounterListItem",
    "EncounterDetail",
    "PartyOverview",
    "ReferenceIndex",
    "ReferenceListItem",
    "ReferenceDetail",
    "SearchResponse",
    "SearchResult",
]
