"""
Creature stats service for loading combat stats from 5etools JSON data.

Provides structured creature data for the combat tracker, including
AC, HP, abilities, speed, traits, and actions.
"""

import json
import re
from pathlib import Path
from typing import Optional, Any

from pydantic import BaseModel


class CreatureHP(BaseModel):
    """Hit points with average and dice formula."""

    average: int
    formula: str


class CreatureStats(BaseModel):
    """Full creature stat block for combat."""

    name: str
    size: str
    creature_type: str
    alignment: Optional[str] = None
    ac: int
    ac_source: Optional[str] = None
    hp: CreatureHP
    speed: dict[str, int]
    abilities: dict[str, int]  # str, dex, con, int, wis, cha
    saves: Optional[dict[str, str]] = None
    skills: Optional[dict[str, str]] = None
    damage_resistances: Optional[list[str]] = None
    damage_immunities: Optional[list[str]] = None
    damage_vulnerabilities: Optional[list[str]] = None
    condition_immunities: Optional[list[str]] = None
    senses: Optional[list[str]] = None
    passive_perception: int
    languages: Optional[list[str]] = None
    cr: str
    traits: Optional[list[dict[str, str]]] = None
    actions: Optional[list[dict[str, str]]] = None
    bonus_actions: Optional[list[dict[str, str]]] = None
    reactions: Optional[list[dict[str, str]]] = None
    legendary_actions: Optional[list[dict[str, str]]] = None


# Size code to full name mapping
SIZE_MAP = {
    "T": "Tiny",
    "S": "Small",
    "M": "Medium",
    "L": "Large",
    "H": "Huge",
    "G": "Gargantuan",
}

# Alignment code to full name mapping
ALIGNMENT_MAP = {
    "L": "Lawful",
    "N": "Neutral",
    "C": "Chaotic",
    "G": "Good",
    "E": "Evil",
    "U": "Unaligned",
    "A": "Any",
}


class CreatureStatsService:
    """Service for loading creature stats from 5etools JSON files."""

    def __init__(self, bestiary_path: Optional[Path] = None):
        """Initialize the service.

        Args:
            bestiary_path: Path to the bestiary JSON files.
                          Defaults to 5etools-src/data/bestiary/
        """
        if bestiary_path is None:
            bestiary_path = Path("5etools-src/data/bestiary")
        self.bestiary_path = bestiary_path
        self._index: Optional[dict[str, dict]] = None

    def _build_index(self) -> dict[str, dict]:
        """Build an index of all creatures by slug."""
        index: dict[str, dict] = {}

        if not self.bestiary_path.exists():
            return index

        for json_file in self.bestiary_path.glob("bestiary-*.json"):
            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                for monster in data.get("monster", []):
                    name = monster.get("name", "")
                    if not name:
                        continue

                    # Create slug from name
                    slug = self._name_to_slug(name)

                    # Store by slug (first one wins for duplicates)
                    if slug not in index:
                        index[slug] = monster
            except (json.JSONDecodeError, IOError):
                continue

        return index

    def _name_to_slug(self, name: str) -> str:
        """Convert creature name to URL-safe slug."""
        slug = name.lower()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    def _get_index(self) -> dict[str, dict]:
        """Get or build the creature index."""
        if self._index is None:
            self._index = self._build_index()
        return self._index

    def get_creature_stats(self, slug: str) -> Optional[CreatureStats]:
        """Get creature stats by slug.

        Args:
            slug: URL-safe creature name (e.g., "goblin", "ancient-red-dragon")

        Returns:
            CreatureStats if found, None otherwise
        """
        index = self._get_index()
        monster = index.get(slug)

        if not monster:
            return None

        return self._parse_monster(monster)

    def _parse_monster(self, monster: dict) -> CreatureStats:
        """Parse a monster dict into CreatureStats."""
        # Parse size
        size_codes = monster.get("size", ["M"])
        size = SIZE_MAP.get(size_codes[0], "Medium") if size_codes else "Medium"

        # Parse type
        type_data = monster.get("type", "")
        if isinstance(type_data, dict):
            creature_type = type_data.get("type", "unknown")
        else:
            creature_type = str(type_data)

        # Parse alignment
        alignment = self._parse_alignment(monster.get("alignment", []))

        # Parse AC
        ac, ac_source = self._parse_ac(monster.get("ac", [10]))

        # Parse HP
        hp_data = monster.get("hp", {})
        if isinstance(hp_data, dict):
            hp = CreatureHP(
                average=hp_data.get("average", 1),
                formula=hp_data.get("formula", "1d4"),
            )
        else:
            hp = CreatureHP(average=int(hp_data), formula=str(hp_data))

        # Parse speed
        speed = self._parse_speed(monster.get("speed", {}))

        # Parse abilities
        abilities = {
            "str": monster.get("str", 10),
            "dex": monster.get("dex", 10),
            "con": monster.get("con", 10),
            "int": monster.get("int", 10),
            "wis": monster.get("wis", 10),
            "cha": monster.get("cha", 10),
        }

        # Parse saves
        saves = monster.get("save")

        # Parse skills
        skills = monster.get("skill")

        # Parse damage modifiers
        damage_resistances = self._parse_damage_list(monster.get("resist"))
        damage_immunities = self._parse_damage_list(monster.get("immune"))
        damage_vulnerabilities = self._parse_damage_list(monster.get("vulnerable"))
        condition_immunities = self._parse_condition_list(monster.get("conditionImmune"))

        # Parse senses
        senses = monster.get("senses")

        # Parse languages
        languages = monster.get("languages")

        # Parse CR
        cr_data = monster.get("cr", "0")
        if isinstance(cr_data, dict):
            cr = cr_data.get("cr", "0")
        else:
            cr = str(cr_data)

        # Parse traits and actions
        traits = self._parse_entries(monster.get("trait"))
        actions = self._parse_entries(monster.get("action"))
        bonus_actions = self._parse_entries(monster.get("bonus"))
        reactions = self._parse_entries(monster.get("reaction"))
        legendary_actions = self._parse_entries(monster.get("legendary"))

        return CreatureStats(
            name=monster.get("name", "Unknown"),
            size=size,
            creature_type=creature_type,
            alignment=alignment,
            ac=ac,
            ac_source=ac_source,
            hp=hp,
            speed=speed,
            abilities=abilities,
            saves=saves,
            skills=skills,
            damage_resistances=damage_resistances,
            damage_immunities=damage_immunities,
            damage_vulnerabilities=damage_vulnerabilities,
            condition_immunities=condition_immunities,
            senses=senses,
            passive_perception=monster.get("passive", 10),
            languages=languages,
            cr=cr,
            traits=traits,
            actions=actions,
            bonus_actions=bonus_actions,
            reactions=reactions,
            legendary_actions=legendary_actions,
        )

    def _parse_alignment(self, alignment: list) -> Optional[str]:
        """Parse alignment array into readable string."""
        if not alignment:
            return None

        parts = []
        for a in alignment:
            if isinstance(a, str):
                parts.append(ALIGNMENT_MAP.get(a, a))
            elif isinstance(a, dict):
                # Complex alignment like {"alignment": ["C", "G"]}
                if "alignment" in a:
                    for sub in a["alignment"]:
                        parts.append(ALIGNMENT_MAP.get(sub, sub))

        return " ".join(parts) if parts else None

    def _parse_ac(self, ac_data: list) -> tuple[int, Optional[str]]:
        """Parse AC array into value and source."""
        if not ac_data:
            return 10, None

        first = ac_data[0]
        if isinstance(first, int):
            return first, None
        elif isinstance(first, dict):
            ac_value = first.get("ac", 10)
            ac_from = first.get("from", [])
            ac_source = ", ".join(ac_from) if ac_from else None
            return ac_value, ac_source

        return 10, None

    def _parse_speed(self, speed_data: Any) -> dict[str, int]:
        """Parse speed into dict of movement types."""
        if not speed_data:
            return {"walk": 30}

        if isinstance(speed_data, int):
            return {"walk": speed_data}

        result = {}
        for key, value in speed_data.items():
            if isinstance(value, int):
                result[key] = value
            elif isinstance(value, dict):
                result[key] = value.get("number", 0)
            elif isinstance(value, bool):
                continue  # Skip boolean flags like "canHover"

        return result if result else {"walk": 30}

    def _parse_damage_list(self, data: Any) -> Optional[list[str]]:
        """Parse damage resistance/immunity/vulnerability list."""
        if not data:
            return None

        result = []
        for item in data:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                # Complex entry like {"resist": ["fire"], "note": "..."}
                if "resist" in item:
                    result.extend(item["resist"])
                elif "immune" in item:
                    result.extend(item["immune"])

        return result if result else None

    def _parse_condition_list(self, data: Any) -> Optional[list[str]]:
        """Parse condition immunity list."""
        if not data:
            return None

        result = []
        for item in data:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                if "conditionImmune" in item:
                    result.extend(item["conditionImmune"])

        return result if result else None

    def _parse_entries(self, entries: Optional[list]) -> Optional[list[dict[str, str]]]:
        """Parse trait/action entries into simple name/description pairs."""
        if not entries:
            return None

        result = []
        for entry in entries:
            if isinstance(entry, dict):
                name = entry.get("name", "")
                entries_text = entry.get("entries", [])

                # Clean the name (may contain tags like {@recharge 5})
                name = self._clean_tags(name)

                # Convert entries to text
                description = self._entries_to_text(entries_text)

                if name and description:
                    result.append({"name": name, "description": description})

        return result if result else None

    def _entries_to_text(self, entries: list) -> str:
        """Convert 5etools entries array to plain text."""
        parts = []
        for entry in entries:
            if isinstance(entry, str):
                # Clean up 5etools tags like {@damage 1d6} -> 1d6
                text = self._clean_tags(entry)
                parts.append(text)
            elif isinstance(entry, dict):
                # Nested entry types
                if entry.get("type") == "list":
                    items = entry.get("items", [])
                    for item in items:
                        if isinstance(item, str):
                            parts.append(f"• {self._clean_tags(item)}")
                elif "entries" in entry:
                    parts.append(self._entries_to_text(entry["entries"]))

        return " ".join(parts)

    def _clean_tags(self, text: str) -> str:
        """Remove 5etools tags from text and convert to readable format."""
        cleaned = text

        # ===== HIT AND ATTACK TAGS =====
        # {@h} = "Hit: " prefix
        cleaned = re.sub(r"\{@h\}", "Hit: ", cleaned)

        # {@hom} = "Hit or Miss: " prefix
        cleaned = re.sub(r"\{@hom\}", "Hit or Miss: ", cleaned)

        # {@hit X} = "+X" (the text often already has "to hit" after it)
        cleaned = re.sub(r"\{@hit\s+(\d+)\}", r"+\1", cleaned)

        # {@hitYourSpellAttack ...} = "your spell attack modifier"
        cleaned = re.sub(r"\{@hitYourSpellAttack[^}]*\}", "your spell attack modifier", cleaned)

        # ===== ATTACK TYPE TAGS (2024 format - atkr) =====
        # Handle combined m,r first (melee or ranged)
        cleaned = re.sub(r"\{@atkr\s+m,r\}", "Melee or Ranged Attack Roll:", cleaned)
        cleaned = re.sub(r"\{@atkr\s+m\}", "Melee Attack Roll:", cleaned)
        cleaned = re.sub(r"\{@atkr\s+r\}", "Ranged Attack Roll:", cleaned)

        # ===== ATTACK TYPE TAGS (2014 format - atk) =====
        # Combined attacks first
        cleaned = re.sub(r"\{@atk\s+mw,rw\}", "Melee or Ranged Weapon Attack:", cleaned)
        cleaned = re.sub(r"\{@atk\s+ms,rs\}", "Melee or Ranged Spell Attack:", cleaned)
        cleaned = re.sub(r"\{@atk\s+m,r\}", "Melee or Ranged Attack:", cleaned)
        # Single attack types
        cleaned = re.sub(r"\{@atk\s+mw\}", "Melee Weapon Attack:", cleaned)
        cleaned = re.sub(r"\{@atk\s+rw\}", "Ranged Weapon Attack:", cleaned)
        cleaned = re.sub(r"\{@atk\s+ms\}", "Melee Spell Attack:", cleaned)
        cleaned = re.sub(r"\{@atk\s+rs\}", "Ranged Spell Attack:", cleaned)

        # ===== SAVING THROW TAGS (2024 format) =====
        # {@actSave wis} = "Wisdom Saving Throw:"
        ability_map = {
            "str": "Strength",
            "dex": "Dexterity",
            "con": "Constitution",
            "int": "Intelligence",
            "wis": "Wisdom",
            "cha": "Charisma",
        }
        for abbr, full in ability_map.items():
            cleaned = re.sub(rf"\{{@actSave\s+{abbr}\}}", f"{full} Saving Throw:", cleaned)

        # {@dc X} = "DC X"
        cleaned = re.sub(r"\{@dc\s+(\d+)\}", r"DC \1", cleaned)

        # Save result markers
        cleaned = re.sub(r"\{@actSaveFail(?:\s+\d+)?\}", "Failure:", cleaned)
        cleaned = re.sub(r"\{@actSaveSuccess\}", "Success:", cleaned)
        cleaned = re.sub(r"\{@actSaveSuccessOrFail\}", "", cleaned)  # Just a marker
        cleaned = re.sub(r"\{@actSaveFailBy\s+\d+\}", "Failure by 5+:", cleaned)

        # ===== REACTION TAGS =====
        cleaned = re.sub(r"\{@actTrigger\}", "Trigger:", cleaned)
        cleaned = re.sub(r"\{@actResponse\}", "Response:", cleaned)

        # ===== RECHARGE TAG =====
        # {@recharge X} = "(Recharge X-6)" or "(Recharge 6)"
        cleaned = re.sub(
            r"\{@recharge\s*(\d+)?\}",
            lambda m: f"(Recharge {m.group(1)}-6)" if m.group(1) else "(Recharge 6)",
            cleaned,
        )

        # ===== REFERENCE TAGS WITH DISPLAY TEXT =====
        # Handle 3-part tags: {@tag Name|SOURCE|Display} -> Display
        # This covers variantrule, condition, spell with display overrides
        # Use [^|}]+ to stop at both pipe and close brace
        cleaned = re.sub(r"\{@\w+\s+[^|}]+\|[^|}]+\|([^}]+)\}", r"\1", cleaned)

        # {@quickref X||3||display} or {@quickref X||3} -> display or X
        # Pattern: {@quickref name|page|chapter|optional|display}
        cleaned = re.sub(r"\{@quickref\s+[^|]+\|[^|]*\|[^|]*\|[^|]*\|([^}]+)\}", r"\1", cleaned)
        cleaned = re.sub(r"\{@quickref\s+([^|}]+)[^}]*\}", r"\1", cleaned)

        # {@status X||display} -> display, or {@status X} -> X
        cleaned = re.sub(r"\{@status\s+[^|]+\|\|([^}]+)\}", r"\1", cleaned)

        # {@skillCheck ability score} -> "ability (score)"
        cleaned = re.sub(
            r"\{@skillCheck\s+(\w+)\s+(\d+)\}",
            lambda m: f"{m.group(1).replace('_', ' ').title()} ({m.group(2)})",
            cleaned,
        )

        # ===== GENERAL REFERENCE TAGS =====
        # Handle {@tag name|source} -> name (most 5etools refs: spell, creature, item, etc.)
        cleaned = re.sub(r"\{@\w+\s+([^}|]+)\|[^}]+\}", r"\1", cleaned)

        # Handle {@tag content} -> content (damage, dice, condition, skill, action, sense, etc.)
        cleaned = re.sub(r"\{@\w+\s+([^}|]+)\}", r"\1", cleaned)

        # ===== CLEANUP =====
        # Remove any remaining empty tags like {@i}, {@b}, {@note}, etc.
        cleaned = re.sub(r"\{@\w+\}", "", cleaned)

        # Clean up extra whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def list_creatures(self, limit: int = 100) -> list[dict[str, str]]:
        """List available creatures.

        Returns:
            List of dicts with name, slug, cr
        """
        index = self._get_index()
        result = []

        for slug, monster in list(index.items())[:limit]:
            cr = monster.get("cr", "0")
            if isinstance(cr, dict):
                cr = cr.get("cr", "0")

            result.append({
                "name": monster.get("name", "Unknown"),
                "slug": slug,
                "cr": str(cr),
            })

        return result
