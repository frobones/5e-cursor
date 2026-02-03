#!/usr/bin/env python3
"""
D&D Beyond API client for character imports.

Fetches and parses character data from the D&D Beyond public API.
"""

import re
from dataclasses import dataclass, field
from typing import Any, Optional

import requests


# D&D Beyond API endpoint
CHARACTER_API_URL = "https://character-service.dndbeyond.com/character/v5/character/{character_id}"

# Stat ID to name mapping
STAT_NAMES = {
    1: "STR",
    2: "DEX",
    3: "CON",
    4: "INT",
    5: "WIS",
    6: "CHA",
}

# Alignment ID to name mapping
ALIGNMENTS = {
    1: "Lawful Good",
    2: "Neutral Good",
    3: "Chaotic Good",
    4: "Lawful Neutral",
    5: "True Neutral",
    6: "Chaotic Neutral",
    7: "Lawful Evil",
    8: "Neutral Evil",
    9: "Chaotic Evil",
}


@dataclass
class CharacterStats:
    """Character ability scores."""

    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Bonuses from race, class, etc.
    strength_bonus: int = 0
    dexterity_bonus: int = 0
    constitution_bonus: int = 0
    intelligence_bonus: int = 0
    wisdom_bonus: int = 0
    charisma_bonus: int = 0

    def total(self, stat: str) -> int:
        """Get total stat value including bonuses."""
        base = getattr(self, stat.lower())
        bonus = getattr(self, f"{stat.lower()}_bonus")
        return base + bonus

    def modifier(self, stat: str) -> int:
        """Get the modifier for a stat."""
        return (self.total(stat) - 10) // 2

    def modifier_str(self, stat: str) -> str:
        """Get modifier as a string with sign."""
        mod = self.modifier(stat)
        return f"+{mod}" if mod >= 0 else str(mod)


@dataclass
class ClassInfo:
    """Character class information."""

    name: str
    level: int
    is_starting: bool = True
    features: list[dict] = field(default_factory=list)
    hit_dice: int = 8


@dataclass
class InventoryItem:
    """An item in the character's inventory."""

    name: str
    quantity: int = 1
    equipped: bool = False
    item_type: str = ""
    armor_class: Optional[int] = None
    damage: Optional[str] = None
    damage_type: Optional[str] = None
    range: Optional[int] = None
    long_range: Optional[int] = None
    weight: float = 0.0
    properties: list[str] = field(default_factory=list)


@dataclass
class Character:
    """Parsed D&D Beyond character data."""

    id: int
    name: str
    player: str = ""
    species: str = ""
    classes: list[ClassInfo] = field(default_factory=list)
    level: int = 1
    background: str = ""
    alignment: str = ""

    # Physical
    gender: str = ""
    age: int = 0
    height: str = ""
    weight: int = 0
    hair: str = ""
    eyes: str = ""
    skin: str = ""

    # Stats
    stats: CharacterStats = field(default_factory=CharacterStats)
    proficiency_bonus: int = 2

    # Species info
    size: str = "Medium"
    creature_type: str = "Humanoid"

    # Combat
    max_hp: int = 0
    current_hp: int = 0
    temp_hp: int = 0
    armor_class: int = 10
    speed: int = 30

    # Proficiencies
    skill_proficiencies: list[str] = field(default_factory=list)
    skill_expertise: list[str] = field(default_factory=list)
    saving_throws: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    tool_proficiencies: list[str] = field(default_factory=list)
    weapon_proficiencies: list[str] = field(default_factory=list)
    armor_proficiencies: list[str] = field(default_factory=list)

    # Features
    species_traits: list[dict] = field(default_factory=list)
    class_features: list[dict] = field(default_factory=list)
    feats: list[dict] = field(default_factory=list)

    # Equipment
    inventory: list[InventoryItem] = field(default_factory=list)
    currency: dict[str, int] = field(default_factory=lambda: {"cp": 0, "sp": 0, "gp": 0, "ep": 0, "pp": 0})

    # Personality
    personality_traits: str = ""
    ideals: str = ""
    bonds: str = ""
    flaws: str = ""
    appearance: str = ""

    # Notes
    allies: str = ""
    enemies: str = ""
    organizations: str = ""
    backstory: str = ""

    # Source
    source_url: str = ""

    def class_string(self) -> str:
        """Get formatted class string (e.g., 'Rogue 3 / Wizard 2')."""
        parts = [f"{c.name} {c.level}" for c in self.classes]
        return " / ".join(parts)


def extract_character_id(url: str) -> int:
    """Extract character ID from a D&D Beyond URL.

    Args:
        url: D&D Beyond character URL (e.g., https://www.dndbeyond.com/characters/157884334)

    Returns:
        Character ID

    Raises:
        ValueError: If URL format is invalid
    """
    # Match various URL formats
    patterns = [
        r"dndbeyond\.com/characters/(\d+)",
        r"^(\d+)$",  # Just the ID
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return int(match.group(1))

    raise ValueError(f"Could not extract character ID from: {url}")


def fetch_character_json(character_id: int) -> dict[str, Any]:
    """Fetch raw character JSON from D&D Beyond API.

    Args:
        character_id: D&D Beyond character ID

    Returns:
        Raw API response as dict

    Raises:
        requests.HTTPError: If API request fails
        ValueError: If character is not accessible
    """
    url = CHARACTER_API_URL.format(character_id=character_id)

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not data.get("success"):
        raise ValueError(f"Failed to fetch character: {data.get('message', 'Unknown error')}")

    if not data.get("data"):
        raise ValueError("Character not accessible. Ensure the character's privacy is set to 'Public' in D&D Beyond.")

    return data


def _parse_stats(data: dict) -> CharacterStats:
    """Parse ability scores from character data."""
    stats = CharacterStats()

    # Base stats
    for stat in data.get("stats", []):
        stat_id = stat.get("id")
        value = stat.get("value", 10)
        if stat_id == 1:
            stats.strength = value
        elif stat_id == 2:
            stats.dexterity = value
        elif stat_id == 3:
            stats.constitution = value
        elif stat_id == 4:
            stats.intelligence = value
        elif stat_id == 5:
            stats.wisdom = value
        elif stat_id == 6:
            stats.charisma = value

    # Parse modifiers for stat bonuses
    for source in ["race", "class", "feat", "background"]:
        for mod in data.get("modifiers", {}).get(source, []):
            if mod.get("type") == "bonus":
                subtype = mod.get("subType", "")
                value = mod.get("value", 0) or 0
                if "strength" in subtype:
                    stats.strength_bonus += value
                elif "dexterity" in subtype:
                    stats.dexterity_bonus += value
                elif "constitution" in subtype:
                    stats.constitution_bonus += value
                elif "intelligence" in subtype:
                    stats.intelligence_bonus += value
                elif "wisdom" in subtype:
                    stats.wisdom_bonus += value
                elif "charisma" in subtype:
                    stats.charisma_bonus += value

    return stats


def _parse_proficiencies(data: dict) -> tuple[list[str], list[str], list[str], list[str], list[str], list[str], list[str]]:
    """Parse all proficiencies from character data.

    Returns:
        Tuple of (skills, expertise, saving_throws, languages, tools, weapons, armor)
    """
    skills = []
    expertise = []
    saving_throws = []
    languages = []
    tools = []
    weapons = []
    armor = []

    for source in ["race", "class", "feat", "background"]:
        for mod in data.get("modifiers", {}).get(source, []):
            mod_type = mod.get("type", "")
            subtype = mod.get("subType", "")
            friendly = mod.get("friendlySubtypeName", subtype.replace("-", " ").title())

            if mod_type == "proficiency":
                if "saving-throws" in subtype:
                    stat = subtype.replace("-saving-throws", "").upper()
                    if stat not in saving_throws:
                        saving_throws.append(stat)
                elif subtype in ["light-armor", "medium-armor", "heavy-armor", "shields"]:
                    if friendly not in armor:
                        armor.append(friendly)
                elif "weapons" in subtype or subtype in ["simple-weapons", "martial-weapons"]:
                    if friendly not in weapons:
                        weapons.append(friendly)
                elif "kit" in subtype or "tools" in subtype or "supplies" in subtype:
                    if friendly not in tools:
                        tools.append(friendly)
                else:
                    # Assume it's a skill
                    if friendly not in skills:
                        skills.append(friendly)

            elif mod_type == "expertise":
                if friendly not in expertise:
                    expertise.append(friendly)

            elif mod_type == "language":
                lang = friendly.replace("-", " ").title()
                if lang not in languages:
                    languages.append(lang)

    return skills, expertise, saving_throws, languages, tools, weapons, armor


def _parse_classes(data: dict) -> list[ClassInfo]:
    """Parse class information from character data."""
    classes = []

    for cls in data.get("classes", []):
        definition = cls.get("definition", {})
        char_level = cls.get("level", 1)
        features = []

        for feature in cls.get("classFeatures", []):
            feat_def = feature.get("definition", {})
            if feat_def:
                # Only include features the character has earned at their level
                required_level = feat_def.get("requiredLevel", 1)
                if required_level <= char_level:
                    features.append({
                        "name": feat_def.get("name", ""),
                        "description": feat_def.get("description", ""),
                        "snippet": feat_def.get("snippet", ""),
                        "level": required_level,
                    })

        classes.append(ClassInfo(
            name=definition.get("name", "Unknown"),
            level=char_level,
            is_starting=cls.get("isStartingClass", False),
            features=features,
            hit_dice=definition.get("hitDice", 8),
        ))

    return classes


def _parse_inventory(data: dict) -> list[InventoryItem]:
    """Parse inventory from character data."""
    items = []

    for item in data.get("inventory", []):
        definition = item.get("definition", {})
        damage = definition.get("damage")
        properties = definition.get("properties", []) or []

        items.append(InventoryItem(
            name=definition.get("name", "Unknown"),
            quantity=item.get("quantity", 1),
            equipped=item.get("equipped", False),
            item_type=definition.get("type", ""),
            armor_class=definition.get("armorClass"),
            damage=damage.get("diceString") if damage else None,
            damage_type=definition.get("damageType"),
            range=definition.get("range"),
            long_range=definition.get("longRange"),
            weight=definition.get("weight", 0.0) or 0.0,
            properties=[p.get("name", "") for p in properties] if properties else [],
        ))

    return items


def parse_character(data: dict) -> Character:
    """Parse character data from API response.

    Args:
        data: Raw API response dict (the outer envelope with 'data' key)

    Returns:
        Parsed Character object
    """
    char_data = data.get("data", data)

    # Parse stats
    stats = _parse_stats(char_data)

    # Parse proficiencies
    skills, expertise, saves, languages, tools, weapons, armor = _parse_proficiencies(char_data)

    # Parse classes
    classes = _parse_classes(char_data)
    total_level = sum(c.level for c in classes)
    proficiency_bonus = 2 + (total_level - 1) // 4

    # Parse inventory
    inventory = _parse_inventory(char_data)

    # Calculate HP
    base_hp = char_data.get("baseHitPoints", 0)
    bonus_hp = char_data.get("bonusHitPoints", 0) or 0
    override_hp = char_data.get("overrideHitPoints")
    con_mod = stats.modifier("constitution")
    max_hp = override_hp if override_hp else base_hp + bonus_hp + (con_mod * total_level)

    # Calculate AC (simplified - just base + dex for light armor)
    dex_mod = stats.modifier("dexterity")
    base_ac = 10 + dex_mod
    for item in inventory:
        if item.equipped and item.armor_class:
            base_ac = item.armor_class + dex_mod  # Simplified, doesn't handle max dex bonus
            break

    # Parse species/race info
    race = char_data.get("race", {})
    
    # Size mapping from D&D Beyond size IDs
    SIZE_MAP = {
        1: "Tiny",
        2: "Small", 
        3: "Medium",
        4: "Large",
        5: "Huge",
        6: "Gargantuan",
    }
    size_id = race.get("sizeId", 3)
    species_size = SIZE_MAP.get(size_id, "Medium")
    
    # Parse creature type - default to Humanoid
    species_type = "Humanoid"
    type_info = race.get("type", None)
    if type_info:
        species_type = type_info if isinstance(type_info, str) else "Humanoid"
    
    # Parse speed from race or walking speed
    base_speed = race.get("weightSpeeds", {}).get("normal", {}).get("walk", 30)
    if base_speed == 0:
        base_speed = 30  # Default if not found
    
    # Parse species traits
    species_traits = []
    for trait in race.get("racialTraits", []):
        trait_def = trait.get("definition", {})
        if trait_def:
            species_traits.append({
                "name": trait_def.get("name", ""),
                "description": trait_def.get("description", ""),
                "snippet": trait_def.get("snippet", ""),
            })

    # Parse feats
    feats = []
    for feat in char_data.get("feats", []):
        feat_def = feat.get("definition", {})
        if feat_def:
            feats.append({
                "name": feat_def.get("name", ""),
                "description": feat_def.get("description", ""),
                "snippet": feat_def.get("snippet", ""),
            })

    # Collect all class features
    class_features = []
    for cls in classes:
        for feature in cls.features:
            feature["class"] = cls.name
            class_features.append(feature)

    # Parse traits
    traits = char_data.get("traits", {})
    notes = char_data.get("notes", {})

    # Parse currency
    currency = char_data.get("currencies", {})

    return Character(
        id=char_data.get("id", 0),
        name=char_data.get("name", "Unknown"),
        player=char_data.get("username", ""),
        species=race.get("fullName", race.get("baseName", "Unknown")),
        classes=classes,
        level=total_level,
        background=char_data.get("background", {}).get("definition", {}).get("name", ""),
        alignment=ALIGNMENTS.get(char_data.get("alignmentId", 0), ""),
        gender=char_data.get("gender", ""),
        age=char_data.get("age", 0),
        height=char_data.get("height", ""),
        weight=char_data.get("weight", 0),
        hair=char_data.get("hair", ""),
        eyes=char_data.get("eyes", ""),
        skin=char_data.get("skin", ""),
        stats=stats,
        proficiency_bonus=proficiency_bonus,
        max_hp=max_hp,
        current_hp=max_hp - char_data.get("removedHitPoints", 0),
        temp_hp=char_data.get("temporaryHitPoints", 0),
        armor_class=base_ac,
        speed=base_speed,
        size=species_size,
        creature_type=species_type,
        skill_proficiencies=skills,
        skill_expertise=expertise,
        saving_throws=saves,
        languages=languages,
        tool_proficiencies=tools,
        weapon_proficiencies=weapons,
        armor_proficiencies=armor,
        species_traits=species_traits,
        class_features=class_features,
        feats=feats,
        inventory=inventory,
        currency=currency,
        personality_traits=traits.get("personalityTraits", ""),
        ideals=traits.get("ideals", ""),
        bonds=traits.get("bonds", ""),
        flaws=traits.get("flaws", ""),
        appearance=traits.get("appearance", ""),
        allies=notes.get("allies", ""),
        enemies=notes.get("enemies", ""),
        organizations=notes.get("organizations", ""),
        backstory=notes.get("backstory", ""),
        source_url=f"https://www.dndbeyond.com/characters/{char_data.get('id', 0)}",
    )


def fetch_character(url_or_id: str) -> Character:
    """Fetch and parse a character from D&D Beyond.

    Args:
        url_or_id: D&D Beyond character URL or ID

    Returns:
        Parsed Character object

    Raises:
        ValueError: If URL is invalid or character not accessible
        requests.HTTPError: If API request fails
    """
    character_id = extract_character_id(url_or_id)
    data = fetch_character_json(character_id)
    return parse_character(data)
