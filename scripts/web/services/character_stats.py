"""
Character stats service for loading PC stat blocks from JSON files.

This service loads structured character data for display in the combat tracker.
"""

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class CharacterHP(BaseModel):
    """Hit points with current and max."""

    current: int
    max: int


class CharacterStats(BaseModel):
    """Full character stat block for combat display."""

    name: str
    player: str
    species: str
    character_class: str  # 'class' is reserved in Python
    background: Optional[str] = None
    alignment: Optional[str] = None
    size: str = "Medium"
    creature_type: str = "Humanoid"
    ac: int
    ac_source: Optional[str] = None
    hp: CharacterHP
    speed: dict[str, int]
    abilities: dict[str, int]  # str, dex, con, int, wis, cha
    proficiency_bonus: int
    saves: Optional[dict[str, str]] = None
    skills: Optional[dict[str, str]] = None
    passive_perception: int = 10
    languages: Optional[list[str]] = None
    tools: Optional[list[str]] = None
    traits: Optional[list[dict[str, str]]] = None
    actions: Optional[list[dict[str, str]]] = None
    bonus_actions: Optional[list[dict[str, str]]] = None
    reactions: Optional[list[dict[str, str]]] = None
    feats: Optional[list[str]] = None
    source: Optional[str] = None
    last_updated: Optional[str] = None


class CharacterStatsService:
    """Service for loading character stats from JSON files."""

    def __init__(self, party_path: Optional[Path] = None):
        if party_path is None:
            party_path = Path("campaign/party/characters")
        self.party_path = party_path
        self._index: Optional[dict[str, Path]] = None

    def _build_index(self) -> dict[str, Path]:
        """Build an index of character slugs to file paths."""
        index = {}
        if not self.party_path.exists():
            return index

        for json_file in self.party_path.glob("*.json"):
            slug = json_file.stem  # filename without extension
            index[slug] = json_file

        return index

    def _get_index(self) -> dict[str, Path]:
        """Get or build the character index."""
        if self._index is None:
            self._index = self._build_index()
        return self._index

    def get_character_stats(self, slug: str) -> Optional[CharacterStats]:
        """Get character stats by slug (filename without extension)."""
        index = self._get_index()
        json_path = index.get(slug)

        if not json_path or not json_path.exists():
            return None

        try:
            data = json.loads(json_path.read_text())
            return self._parse_character(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing character {slug}: {e}")
            return None

    def _parse_character(self, data: dict) -> CharacterStats:
        """Parse character JSON into CharacterStats model."""
        # Parse HP
        hp_data = data.get("hp", {})
        hp = CharacterHP(
            current=hp_data.get("current", hp_data.get("max", 10)),
            max=hp_data.get("max", 10),
        )

        # Parse speed
        speed = data.get("speed", {"walk": 30})
        if isinstance(speed, int):
            speed = {"walk": speed}

        # Parse abilities
        abilities = data.get("abilities", {})

        return CharacterStats(
            name=data.get("name", "Unknown"),
            player=data.get("player", "Unknown"),
            species=data.get("species", "Unknown"),
            character_class=data.get("class", "Unknown"),
            background=data.get("background"),
            alignment=data.get("alignment"),
            size=data.get("size", "Medium"),
            creature_type=data.get("creatureType", "Humanoid"),
            ac=data.get("ac", 10),
            ac_source=data.get("acSource"),
            hp=hp,
            speed=speed,
            abilities=abilities,
            proficiency_bonus=data.get("proficiencyBonus", 2),
            saves=data.get("saves"),
            skills=data.get("skills"),
            passive_perception=data.get("passivePerception", 10),
            languages=data.get("languages"),
            tools=data.get("tools"),
            traits=data.get("traits"),
            actions=data.get("actions"),
            bonus_actions=data.get("bonusActions"),
            reactions=data.get("reactions"),
            feats=data.get("feats"),
            source=data.get("source"),
            last_updated=data.get("lastUpdated"),
        )

    def list_characters(self) -> list[dict[str, str]]:
        """List all characters with basic info."""
        index = self._get_index()
        characters = []

        for slug, path in index.items():
            try:
                data = json.loads(path.read_text())
                characters.append({
                    "name": data.get("name", slug),
                    "slug": slug,
                    "player": data.get("player", "Unknown"),
                    "class": data.get("class", "Unknown"),
                })
            except json.JSONDecodeError:
                continue

        return sorted(characters, key=lambda x: x["name"])
