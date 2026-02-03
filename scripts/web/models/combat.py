"""
Combat state Pydantic models for the encounter runner.
"""

import re
from pydantic import BaseModel, ConfigDict
from typing import Optional, Literal


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CamelCaseModel(BaseModel):
    """Base model that accepts camelCase input and outputs camelCase."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Accept both snake_case and camelCase
    )


class Combatant(CamelCaseModel):
    """Individual combat participant."""

    id: str
    name: str
    type: Literal["monster", "player"]
    creature_slug: Optional[str] = None
    character_slug: Optional[str] = None
    initiative: int
    max_hp: int
    current_hp: int
    temp_hp: int = 0
    damage_taken: int = 0  # For players: tracks total damage taken (DM doesn't know PC HP)
    conditions: list[str] = []
    is_active: bool = False
    ac: int = 10  # Armor Class for quick reference
    dex_modifier: int = 0  # For rolling initiative


class DamageEvent(CamelCaseModel):
    """Single damage/healing event."""

    id: str
    round: int
    turn: int
    target_id: str
    target_name: str
    amount: int
    type: Literal["damage", "healing", "temp_hp"]
    source: Optional[str] = None
    timestamp: str


class CombatState(CamelCaseModel):
    """Full combat state for persistence."""

    encounter_id: str
    encounter_name: str
    round: int
    turn: int
    status: Literal["active", "paused", "completed"]
    started_at: str
    combatants: list[Combatant]
    damage_log: list[DamageEvent]


class CombatCreate(CamelCaseModel):
    """Request to start combat from an encounter."""

    include_party: bool = True
    selected_party_members: Optional[list[str]] = None  # List of character slugs to include


class CombatAction(BaseModel):
    """Apply damage, healing, or temp HP."""

    target_id: str
    amount: int
    type: Literal["damage", "healing", "temp_hp"]
    source: Optional[str] = None


class InitiativeEntry(BaseModel):
    """Set initiative for a combatant."""

    combatant_id: str
    initiative: int
