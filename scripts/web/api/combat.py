"""
Combat state API endpoints.

Provides endpoints for starting, managing, and ending combat sessions.
"""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from web.models.combat import (
    CombatState,
    CombatCreate,
    Combatant,
    DamageEvent,
)
from web.services.combat import CombatService
from web.services.creature_stats import CreatureStatsService
from web.services.entities import EntityService

router = APIRouter()


def get_campaign_dir() -> Path:
    """Get the campaign directory path."""
    return Path("campaign")


@router.get("/combat/{slug}", response_model=CombatState)
async def get_combat(slug: str) -> CombatState:
    """Get combat state for an encounter."""
    service = CombatService(get_campaign_dir())
    combat = service.load_combat(slug)
    if not combat:
        raise HTTPException(status_code=404, detail=f"No active combat for encounter: {slug}")
    return combat


@router.post("/combat/{slug}", response_model=CombatState)
async def start_combat(slug: str, request: CombatCreate) -> CombatState:
    """Start a new combat session from an encounter."""
    entity_service = EntityService()
    combat_service = CombatService(get_campaign_dir())

    # Check if combat already exists
    existing = combat_service.load_combat(slug)
    if existing and existing.status == "active":
        raise HTTPException(
            status_code=409,
            detail="Combat already active. End or resume the existing combat.",
        )

    # Get encounter details
    encounter = entity_service.get_encounter(slug)
    if not encounter:
        raise HTTPException(status_code=404, detail=f"Encounter not found: {slug}")

    # Expand creatures into individual combatants
    combatants: list[Combatant] = []
    creature_stats_service = CreatureStatsService()

    for creature in encounter.creatures:
        # Get HP, AC, and DEX modifier from creature stats (5etools JSON data)
        creature_slug = creature.name.lower().replace(" ", "-")
        stats = creature_stats_service.get_creature_stats(creature_slug)

        if stats:
            max_hp = stats.hp.average
            ac = stats.ac
            # Calculate DEX modifier from abilities
            dex_score = stats.abilities.get("dex", 10) if stats.abilities else 10
            dex_modifier = (dex_score - 10) // 2
        else:
            max_hp = 10  # Fallback default HP
            ac = 10
            dex_modifier = 0

        for i in range(creature.count):
            combatant_id = f"monster-{creature_slug}-{i + 1}"
            name = f"{creature.name} {i + 1}" if creature.count > 1 else creature.name

            combatants.append(
                Combatant(
                    id=combatant_id,
                    name=name,
                    type="monster",
                    creature_slug=creature_slug,
                    initiative=0,
                    max_hp=max_hp,
                    current_hp=max_hp,
                    temp_hp=0,
                    damage_taken=0,
                    conditions=[],
                    is_active=False,
                    ac=ac,
                    dex_modifier=dex_modifier,
                )
            )

    # Add party members if requested
    if request.include_party:
        from web.services.character_stats import CharacterStatsService
        char_stats_service = CharacterStatsService()

        party = entity_service.get_party()
        for char in party.characters:
            # Filter by selected members if provided
            if request.selected_party_members is not None:
                if char.slug not in request.selected_party_members:
                    continue

            # Get AC and DEX modifier from character stats JSON
            char_stats = char_stats_service.get_character_stats(char.slug)
            if char_stats:
                ac = char_stats.ac
                dex_score = char_stats.abilities.get("dex", 10) if char_stats.abilities else 10
                dex_modifier = (dex_score - 10) // 2
            else:
                ac = 10
                dex_modifier = 0

            combatants.append(
                Combatant(
                    id=f"player-{char.slug}",
                    name=char.name,
                    type="player",
                    character_slug=char.slug,
                    initiative=0,
                    max_hp=0,  # Players don't track HP (DM doesn't know)
                    current_hp=0,
                    temp_hp=0,
                    damage_taken=0,  # Track damage taken instead
                    conditions=[],
                    is_active=False,
                    ac=ac,
                    dex_modifier=dex_modifier,
                )
            )

    # Create combat state
    combat = CombatState(
        encounter_id=slug,
        encounter_name=encounter.name,
        round=1,
        turn=0,
        status="active",
        started_at=datetime.utcnow().isoformat() + "Z",
        combatants=combatants,
        damage_log=[],
    )

    # Save to file
    combat_service.save_combat(combat)

    return combat


@router.put("/combat/{slug}", response_model=CombatState)
async def update_combat(slug: str, combat: CombatState) -> CombatState:
    """Update combat state (full replacement)."""
    service = CombatService(get_campaign_dir())

    existing = service.load_combat(slug)
    if not existing:
        raise HTTPException(status_code=404, detail=f"No active combat for encounter: {slug}")

    # Validate the encounter ID matches
    if combat.encounter_id != slug:
        raise HTTPException(status_code=400, detail="Encounter ID mismatch")

    # Save updated state
    service.save_combat(combat)

    return combat


@router.delete("/combat/{slug}")
async def end_combat(slug: str) -> dict:
    """End combat and archive the state."""
    service = CombatService(get_campaign_dir())

    if not service.combat_exists(slug):
        raise HTTPException(status_code=404, detail=f"No active combat for encounter: {slug}")

    service.delete_combat(slug)

    return {"status": "ok", "message": f"Combat ended for encounter: {slug}"}


@router.get("/combat", response_model=list[str])
async def list_active_combats() -> list[str]:
    """List all encounters with active combat."""
    service = CombatService(get_campaign_dir())
    return service.list_active_combats()
