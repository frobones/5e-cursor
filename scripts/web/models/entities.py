"""
Entity Pydantic models for NPCs, locations, sessions, etc.
"""

from pydantic import BaseModel
from typing import Optional


class Connection(BaseModel):
    """NPC relationship connection."""

    target_name: str
    target_slug: Optional[str] = None
    type: str
    description: Optional[str] = None


class NPCListItem(BaseModel):
    """NPC summary for list views."""

    name: str
    slug: str
    role: str
    occupation: Optional[str] = None
    location: Optional[str] = None
    first_seen: Optional[str] = None


class NPCDetail(BaseModel):
    """Full NPC details."""

    name: str
    slug: str
    role: str
    content: str
    occupation: Optional[str] = None
    location: Optional[str] = None
    first_seen: Optional[str] = None
    connections: list[Connection] = []


class LocationListItem(BaseModel):
    """Location summary for list views."""

    name: str
    slug: str
    type: str
    region: Optional[str] = None
    discovered: Optional[str] = None


class LocationDetail(BaseModel):
    """Full location details."""

    name: str
    slug: str
    type: str
    content: str
    region: Optional[str] = None
    discovered: Optional[str] = None
    key_npcs: list[str] = []


class SessionListItem(BaseModel):
    """Session summary for list views."""

    number: int
    title: str
    date: str
    in_game_date: Optional[str] = None


class SessionDetail(BaseModel):
    """Full session details."""

    number: int
    title: str
    date: str
    content: str
    in_game_date: Optional[str] = None
    summary: Optional[str] = None
    npcs_encountered: list[str] = []
    locations_visited: list[str] = []


class CharacterListItem(BaseModel):
    """Party character summary."""

    name: str
    slug: str
    player: Optional[str] = None
    species: Optional[str] = None
    class_info: Optional[str] = None
    level: Optional[int] = None


class CharacterDetail(BaseModel):
    """Full character details."""

    name: str
    slug: str
    content: str
    player: Optional[str] = None
    species: Optional[str] = None
    class_info: Optional[str] = None
    level: Optional[int] = None


class PartyOverview(BaseModel):
    """Party overview information."""

    size: int
    average_level: Optional[float] = None
    characters: list[CharacterListItem]


class EncounterCreature(BaseModel):
    """Creature in an encounter."""

    name: str
    cr: str
    count: int
    xp: int


class EncounterListItem(BaseModel):
    """Encounter summary for list views."""

    name: str
    slug: str
    difficulty: str
    total_creatures: int
    party_level: int
    party_size: int = 4
    base_xp: int = 0  # Base XP for recalculating difficulty
    created: Optional[str] = None  # ISO date string


class EncounterDetail(BaseModel):
    """Full encounter details."""

    name: str
    slug: str
    content: str
    difficulty: str
    party_level: int
    party_size: int
    creatures: list[EncounterCreature] = []
    total_xp: int = 0
    has_active_combat: bool = False


class EncounterCreatureCreate(BaseModel):
    """Creature entry for encounter creation."""

    name: str
    slug: str
    cr: str
    xp: int
    count: int


class EncounterCreate(BaseModel):
    """Request to create a new encounter."""

    name: str
    party_level: int
    party_size: int
    creatures: list[EncounterCreatureCreate]


class EncounterUpdate(BaseModel):
    """Request to update an existing encounter."""

    name: Optional[str] = None
    party_level: Optional[int] = None
    party_size: Optional[int] = None
    creatures: Optional[list[EncounterCreatureCreate]] = None
