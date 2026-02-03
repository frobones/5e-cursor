"""
Entity API endpoints.

Provides endpoints for NPCs, locations, sessions, party, and encounters.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

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
    EncounterCreate,
    EncounterUpdate,
    PartyOverview,
)
from web.services.entities import EntityService

router = APIRouter()


# NPC endpoints
@router.get("/npcs", response_model=list[NPCListItem])
async def list_npcs(role: Optional[str] = Query(None, description="Filter by role")) -> list[NPCListItem]:
    """List all NPCs, optionally filtered by role."""
    service = EntityService()
    return service.list_npcs(role=role)


@router.get("/npcs/{slug}", response_model=NPCDetail)
async def get_npc(slug: str) -> NPCDetail:
    """Get NPC details by slug."""
    service = EntityService()
    npc = service.get_npc(slug)
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC not found: {slug}")
    return npc


# Location endpoints
@router.get("/locations", response_model=list[LocationListItem])
async def list_locations(
    location_type: Optional[str] = Query(None, alias="type", description="Filter by type")
) -> list[LocationListItem]:
    """List all locations, optionally filtered by type."""
    service = EntityService()
    return service.list_locations(location_type=location_type)


@router.get("/locations/{slug}", response_model=LocationDetail)
async def get_location(slug: str) -> LocationDetail:
    """Get location details by slug."""
    service = EntityService()
    location = service.get_location(slug)
    if not location:
        raise HTTPException(status_code=404, detail=f"Location not found: {slug}")
    return location


# Session endpoints
@router.get("/sessions", response_model=list[SessionListItem])
async def list_sessions() -> list[SessionListItem]:
    """List all sessions."""
    service = EntityService()
    return service.list_sessions()


@router.get("/sessions/{number}", response_model=SessionDetail)
async def get_session(number: int) -> SessionDetail:
    """Get session details by number."""
    service = EntityService()
    session = service.get_session(number)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session not found: {number}")
    return session


# Party endpoints
@router.get("/party", response_model=PartyOverview)
async def get_party() -> PartyOverview:
    """Get party overview."""
    service = EntityService()
    return service.get_party()


@router.get("/party/characters", response_model=list[CharacterListItem])
async def list_characters() -> list[CharacterListItem]:
    """List all party characters."""
    service = EntityService()
    return service.list_characters()


@router.get("/party/characters/{slug}", response_model=CharacterDetail)
async def get_character(slug: str) -> CharacterDetail:
    """Get character details by slug."""
    service = EntityService()
    character = service.get_character(slug)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character not found: {slug}")
    return character


@router.get("/party/characters/{slug}/stats")
async def get_character_stats(slug: str):
    """Get character combat stats by slug (from JSON file)."""
    from web.services.character_stats import CharacterStatsService, CharacterStats

    service = CharacterStatsService()
    stats = service.get_character_stats(slug)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Character stats not found: {slug}. Create a JSON file at campaign/party/characters/{slug}.json"
        )
    return stats


# Encounter endpoints
@router.get("/encounters", response_model=list[EncounterListItem])
async def list_encounters() -> list[EncounterListItem]:
    """List all saved encounters."""
    service = EntityService()
    return service.list_encounters()


@router.get("/encounters/{slug}", response_model=EncounterDetail)
async def get_encounter(slug: str) -> EncounterDetail:
    """Get encounter details by slug."""
    service = EntityService()
    encounter = service.get_encounter(slug)
    if not encounter:
        raise HTTPException(status_code=404, detail=f"Encounter not found: {slug}")
    return encounter


@router.post("/encounters", response_model=EncounterDetail)
async def create_encounter(encounter: EncounterCreate) -> EncounterDetail:
    """Create a new encounter."""
    service = EntityService()
    try:
        return service.create_encounter(encounter)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.put("/encounters/{slug}", response_model=EncounterDetail)
async def update_encounter(slug: str, update: EncounterUpdate) -> EncounterDetail:
    """Update an existing encounter."""
    service = EntityService()
    result = service.update_encounter(slug, update)
    if not result:
        raise HTTPException(status_code=404, detail=f"Encounter not found: {slug}")
    return result
