"""
Combat state service for managing active combat sessions.

Handles loading, saving, and updating combat state from JSON files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from web.models.combat import CombatState, Combatant, DamageEvent


class CombatService:
    """Service for combat state file operations."""

    def __init__(self, campaign_dir: Path | None = None):
        """Initialize with campaign directory path."""
        self.campaign_dir = campaign_dir or Path("campaign")
        self.encounters_dir = self.campaign_dir / "encounters"

    def _combat_file_path(self, encounter_slug: str) -> Path:
        """Get the path to a combat state file."""
        return self.encounters_dir / f"combat-{encounter_slug}.json"

    def combat_exists(self, encounter_slug: str) -> bool:
        """Check if a combat state file exists for an encounter."""
        return self._combat_file_path(encounter_slug).exists()

    def load_combat(self, encounter_slug: str) -> Optional[CombatState]:
        """Load combat state from file."""
        file_path = self._combat_file_path(encounter_slug)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Pydantic accepts both camelCase and snake_case with populate_by_name=True
            return CombatState(**data)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading combat state: {e}")
            return None

    def save_combat(self, combat: CombatState) -> None:
        """Save combat state to file."""
        self.encounters_dir.mkdir(parents=True, exist_ok=True)
        file_path = self._combat_file_path(combat.encounter_id)

        # Use Pydantic's built-in serialization with camelCase aliases
        data = combat.model_dump(by_alias=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def delete_combat(self, encounter_slug: str) -> bool:
        """Delete combat state file (end combat)."""
        file_path = self._combat_file_path(encounter_slug)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def update_combatant(
        self, encounter_slug: str, combatant_id: str, updates: dict
    ) -> Optional[CombatState]:
        """Update a specific combatant in the combat state."""
        combat = self.load_combat(encounter_slug)
        if not combat:
            return None

        for i, combatant in enumerate(combat.combatants):
            if combatant.id == combatant_id:
                combatant_dict = combatant.model_dump()
                combatant_dict.update(updates)
                combat.combatants[i] = Combatant(**combatant_dict)
                break

        self.save_combat(combat)
        return combat

    def add_damage_event(
        self, encounter_slug: str, event: DamageEvent
    ) -> Optional[CombatState]:
        """Add a damage event to the combat log."""
        combat = self.load_combat(encounter_slug)
        if not combat:
            return None

        combat.damage_log.append(event)
        self.save_combat(combat)
        return combat

    def advance_turn(self, encounter_slug: str) -> Optional[CombatState]:
        """Advance to the next turn in initiative order."""
        combat = self.load_combat(encounter_slug)
        if not combat:
            return None

        # Sort by initiative (descending)
        sorted_combatants = sorted(
            combat.combatants, key=lambda c: c.initiative, reverse=True
        )

        # Find current active and advance
        current_turn = combat.turn
        next_turn = current_turn + 1
        next_round = combat.round

        if next_turn >= len(sorted_combatants):
            next_turn = 0
            next_round += 1

        # Update active status
        for i, combatant in enumerate(sorted_combatants):
            combatant.is_active = i == next_turn

        combat.combatants = sorted_combatants
        combat.turn = next_turn
        combat.round = next_round

        self.save_combat(combat)
        return combat

    def list_active_combats(self) -> list[str]:
        """List all encounter slugs with active combat."""
        if not self.encounters_dir.exists():
            return []

        active = []
        for path in self.encounters_dir.glob("combat-*.json"):
            slug = path.stem.replace("combat-", "")
            active.append(slug)
        return active

    def _to_camel_case(self, data: dict) -> dict:
        """Convert snake_case keys to camelCase for frontend."""
        if isinstance(data, dict):
            return {
                self._snake_to_camel(k): self._to_camel_case(v) for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._to_camel_case(item) for item in data]
        return data

    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split("_")
        return components[0] + "".join(x.title() for x in components[1:])

    def _to_snake_case(self, data: dict) -> dict:
        """Convert camelCase keys to snake_case for Pydantic."""
        if isinstance(data, dict):
            return {
                self._camel_to_snake(k): self._to_snake_case(v) for k, v in data.items()
            }
        elif isinstance(data, list):
            return [self._to_snake_case(item) for item in data]
        return data

    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        import re
        # Insert underscore before uppercase letters and lowercase them
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
