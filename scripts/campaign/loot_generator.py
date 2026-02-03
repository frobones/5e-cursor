#!/usr/bin/env python3
"""
Loot Generator - Generate treasure using DMG 2024 tables.

Usage:
    python scripts/campaign/loot_generator.py individual --cr 3
    python scripts/campaign/loot_generator.py individual --cr 5 --count 4
    python scripts/campaign/loot_generator.py hoard --cr 7
    python scripts/campaign/loot_generator.py hoard --cr 5 --add-to-session 3
    python scripts/campaign/loot_generator.py magic-item --table C
    python scripts/campaign/loot_generator.py magic-item --table F --count 3
    python scripts/campaign/loot_generator.py for-encounter "goblin-ambush"
    python scripts/campaign/loot_generator.py for-encounter "dragon-lair" --hoard
"""

import argparse
import random
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import slugify
from lib.reference_linker import ReferenceLinker


# =============================================================================
# Dice Rolling
# =============================================================================


@dataclass
class DiceRoll:
    """Represents a dice expression like 3d6 or 2d6×100."""

    count: int
    sides: int
    multiplier: int = 1

    def __str__(self) -> str:
        if self.multiplier == 1:
            return f"{self.count}d{self.sides}"
        return f"{self.count}d{self.sides}×{self.multiplier}"


def roll_dice(dice: DiceRoll, rng: random.Random) -> int:
    """Roll dice and return total."""
    total = sum(rng.randint(1, dice.sides) for _ in range(dice.count))
    return total * dice.multiplier


def roll_d100(rng: random.Random) -> int:
    """Roll d100 (1-100)."""
    return rng.randint(1, 100)


# =============================================================================
# CR Tier Mapping
# =============================================================================

# CR ranges to treasure tiers
CR_TIERS = [
    (0, 4, 1),
    (5, 10, 2),
    (11, 16, 3),
    (17, 30, 4),
]


def get_cr_tier(cr: float) -> int:
    """Convert CR to tier (1-4)."""
    for min_cr, max_cr, tier in CR_TIERS:
        if min_cr <= cr <= max_cr:
            return tier
    return 4  # Default to highest tier


def parse_cr(cr_str: str) -> float:
    """Parse CR string to float (e.g., '1/2' -> 0.5)."""
    cr_str = cr_str.strip()
    if "/" in cr_str:
        num, den = cr_str.split("/")
        return int(num) / int(den)
    try:
        return float(cr_str)
    except ValueError:
        raise ValueError(f"Invalid CR: {cr_str}. Use 0-30 or fractions (1/8, 1/4, 1/2)")


# =============================================================================
# Individual Treasure Tables (DMG 2024)
# =============================================================================

# Format: list of (max_roll, {coin_type: DiceRoll})
INDIVIDUAL_TREASURE = {
    1: [  # CR 0-4
        (30, {"cp": DiceRoll(5, 6)}),
        (60, {"sp": DiceRoll(4, 6)}),
        (70, {"ep": DiceRoll(3, 6)}),
        (95, {"gp": DiceRoll(3, 6)}),
        (100, {"pp": DiceRoll(1, 6)}),
    ],
    2: [  # CR 5-10
        (30, {"cp": DiceRoll(4, 6, 100), "ep": DiceRoll(1, 6, 10)}),
        (60, {"sp": DiceRoll(6, 6, 10), "gp": DiceRoll(2, 6, 10)}),
        (70, {"ep": DiceRoll(3, 6, 10), "gp": DiceRoll(2, 6, 10)}),
        (95, {"gp": DiceRoll(4, 6, 10)}),
        (100, {"gp": DiceRoll(2, 6, 10), "pp": DiceRoll(3, 6)}),
    ],
    3: [  # CR 11-16
        (20, {"sp": DiceRoll(4, 6, 100), "gp": DiceRoll(1, 6, 100)}),
        (35, {"ep": DiceRoll(1, 6, 100), "gp": DiceRoll(1, 6, 100)}),
        (75, {"gp": DiceRoll(2, 6, 100), "pp": DiceRoll(1, 6, 10)}),
        (100, {"gp": DiceRoll(2, 6, 100), "pp": DiceRoll(2, 6, 10)}),
    ],
    4: [  # CR 17+
        (15, {"ep": DiceRoll(2, 6, 1000), "gp": DiceRoll(8, 6, 100)}),
        (55, {"gp": DiceRoll(1, 6, 1000), "pp": DiceRoll(1, 6, 100)}),
        (100, {"gp": DiceRoll(1, 6, 1000), "pp": DiceRoll(2, 6, 100)}),
    ],
}

# =============================================================================
# Hoard Base Coins (DMG 2024)
# =============================================================================

HOARD_COINS = {
    1: {"cp": DiceRoll(6, 6, 100), "sp": DiceRoll(3, 6, 100), "gp": DiceRoll(2, 6, 10)},
    2: {"cp": DiceRoll(2, 6, 100), "sp": DiceRoll(2, 6, 1000), "gp": DiceRoll(6, 6, 100), "pp": DiceRoll(3, 6, 10)},
    3: {"sp": DiceRoll(4, 6, 1000), "gp": DiceRoll(1, 6, 1000), "pp": DiceRoll(5, 6, 100)},
    4: {"gp": DiceRoll(12, 6, 1000), "pp": DiceRoll(8, 6, 1000)},
}

# =============================================================================
# Hoard Gems/Art/Magic Tables (DMG 2024)
# =============================================================================

# Format: (max_roll, gem_art_info, magic_info)
# gem_art_info: ("gems"|"art", value, count_dice) or None
# magic_info: [(table, count_dice), ...] or None

HOARD_TABLES = {
    1: [  # CR 0-4
        (6, None, None),
        (16, ("gems", 10, DiceRoll(2, 6)), None),
        (26, ("art", 25, DiceRoll(2, 4)), None),
        (36, ("gems", 50, DiceRoll(2, 6)), None),
        (44, ("gems", 10, DiceRoll(2, 6)), [("A", DiceRoll(1, 6))]),
        (52, ("art", 25, DiceRoll(2, 4)), [("A", DiceRoll(1, 6))]),
        (60, ("gems", 50, DiceRoll(2, 6)), [("A", DiceRoll(1, 6))]),
        (65, ("gems", 10, DiceRoll(2, 6)), [("B", DiceRoll(1, 4))]),
        (70, ("art", 25, DiceRoll(2, 4)), [("B", DiceRoll(1, 4))]),
        (75, ("gems", 50, DiceRoll(2, 6)), [("B", DiceRoll(1, 4))]),
        (78, ("gems", 10, DiceRoll(2, 6)), [("C", DiceRoll(1, 4))]),
        (80, ("art", 25, DiceRoll(2, 4)), [("C", DiceRoll(1, 4))]),
        (85, ("gems", 50, DiceRoll(2, 6)), [("C", DiceRoll(1, 4))]),
        (92, ("art", 25, DiceRoll(2, 4)), [("F", DiceRoll(1, 4))]),
        (97, ("gems", 50, DiceRoll(2, 6)), [("F", DiceRoll(1, 4))]),
        (99, ("art", 25, DiceRoll(2, 4)), [("G", None)]),
        (100, ("gems", 50, DiceRoll(2, 6)), [("G", None)]),
    ],
    2: [  # CR 5-10
        (4, None, None),
        (10, ("art", 25, DiceRoll(2, 4)), None),
        (16, ("gems", 50, DiceRoll(3, 6)), None),
        (22, ("gems", 100, DiceRoll(3, 6)), None),
        (28, ("art", 250, DiceRoll(2, 4)), None),
        (32, ("art", 25, DiceRoll(2, 4)), [("A", DiceRoll(1, 6))]),
        (36, ("gems", 50, DiceRoll(3, 6)), [("A", DiceRoll(1, 6))]),
        (40, ("gems", 100, DiceRoll(3, 6)), [("A", DiceRoll(1, 6))]),
        (44, ("art", 250, DiceRoll(2, 4)), [("A", DiceRoll(1, 6))]),
        (49, ("art", 25, DiceRoll(2, 4)), [("B", DiceRoll(1, 4))]),
        (54, ("gems", 50, DiceRoll(3, 6)), [("B", DiceRoll(1, 4))]),
        (59, ("gems", 100, DiceRoll(3, 6)), [("B", DiceRoll(1, 4))]),
        (63, ("art", 250, DiceRoll(2, 4)), [("B", DiceRoll(1, 4))]),
        (66, ("art", 25, DiceRoll(2, 4)), [("C", DiceRoll(1, 4))]),
        (69, ("gems", 50, DiceRoll(3, 6)), [("C", DiceRoll(1, 4))]),
        (72, ("gems", 100, DiceRoll(3, 6)), [("C", DiceRoll(1, 4))]),
        (74, ("art", 250, DiceRoll(2, 4)), [("C", DiceRoll(1, 4))]),
        (76, ("art", 25, DiceRoll(2, 4)), [("D", None)]),
        (78, ("gems", 50, DiceRoll(3, 6)), [("D", None)]),
        (79, ("gems", 100, DiceRoll(3, 6)), [("D", None)]),
        (80, ("art", 250, DiceRoll(2, 4)), [("D", None)]),
        (84, ("art", 25, DiceRoll(2, 4)), [("F", DiceRoll(1, 4))]),
        (88, ("gems", 50, DiceRoll(3, 6)), [("F", DiceRoll(1, 4))]),
        (91, ("gems", 100, DiceRoll(3, 6)), [("F", DiceRoll(1, 4))]),
        (94, ("art", 250, DiceRoll(2, 4)), [("F", DiceRoll(1, 4))]),
        (96, ("gems", 100, DiceRoll(3, 6)), [("G", DiceRoll(1, 4))]),
        (98, ("art", 250, DiceRoll(2, 4)), [("G", DiceRoll(1, 4))]),
        (99, ("gems", 100, DiceRoll(3, 6)), [("H", None)]),
        (100, ("art", 250, DiceRoll(2, 4)), [("H", None)]),
    ],
    3: [  # CR 11-16
        (3, None, None),
        (6, ("art", 250, DiceRoll(2, 4)), None),
        (9, ("art", 750, DiceRoll(2, 4)), None),
        (12, ("gems", 500, DiceRoll(3, 6)), None),
        (15, ("gems", 1000, DiceRoll(3, 6)), None),
        (19, ("art", 250, DiceRoll(2, 4)), [("A", DiceRoll(1, 4)), ("B", DiceRoll(1, 6))]),
        (23, ("art", 750, DiceRoll(2, 4)), [("A", DiceRoll(1, 4)), ("B", DiceRoll(1, 6))]),
        (26, ("gems", 500, DiceRoll(3, 6)), [("A", DiceRoll(1, 4)), ("B", DiceRoll(1, 6))]),
        (29, ("gems", 1000, DiceRoll(3, 6)), [("A", DiceRoll(1, 4)), ("B", DiceRoll(1, 6))]),
        (35, ("art", 250, DiceRoll(2, 4)), [("C", DiceRoll(1, 6))]),
        (40, ("art", 750, DiceRoll(2, 4)), [("C", DiceRoll(1, 6))]),
        (45, ("gems", 500, DiceRoll(3, 6)), [("C", DiceRoll(1, 6))]),
        (50, ("gems", 1000, DiceRoll(3, 6)), [("C", DiceRoll(1, 6))]),
        (54, ("art", 250, DiceRoll(2, 4)), [("D", DiceRoll(1, 4))]),
        (58, ("art", 750, DiceRoll(2, 4)), [("D", DiceRoll(1, 4))]),
        (62, ("gems", 500, DiceRoll(3, 6)), [("D", DiceRoll(1, 4))]),
        (66, ("gems", 1000, DiceRoll(3, 6)), [("D", DiceRoll(1, 4))]),
        (68, ("art", 250, DiceRoll(2, 4)), [("E", None)]),
        (70, ("art", 750, DiceRoll(2, 4)), [("E", None)]),
        (72, ("gems", 500, DiceRoll(3, 6)), [("E", None)]),
        (74, ("gems", 1000, DiceRoll(3, 6)), [("E", None)]),
        (76, ("art", 250, DiceRoll(2, 4)), [("F", None), ("G", DiceRoll(1, 4))]),
        (78, ("art", 750, DiceRoll(2, 4)), [("F", None), ("G", DiceRoll(1, 4))]),
        (80, ("gems", 500, DiceRoll(3, 6)), [("F", None), ("G", DiceRoll(1, 4))]),
        (82, ("gems", 1000, DiceRoll(3, 6)), [("F", None), ("G", DiceRoll(1, 4))]),
        (85, ("art", 250, DiceRoll(2, 4)), [("H", DiceRoll(1, 4))]),
        (88, ("art", 750, DiceRoll(2, 4)), [("H", DiceRoll(1, 4))]),
        (90, ("gems", 500, DiceRoll(3, 6)), [("H", DiceRoll(1, 4))]),
        (92, ("gems", 1000, DiceRoll(3, 6)), [("H", DiceRoll(1, 4))]),
        (94, ("art", 250, DiceRoll(2, 4)), [("I", None)]),
        (96, ("art", 750, DiceRoll(2, 4)), [("I", None)]),
        (98, ("gems", 500, DiceRoll(3, 6)), [("I", None)]),
        (100, ("gems", 1000, DiceRoll(3, 6)), [("I", None)]),
    ],
    4: [  # CR 17+
        (2, None, None),
        (5, ("gems", 1000, DiceRoll(3, 6)), None),
        (8, ("art", 2500, DiceRoll(1, 10)), None),
        (11, ("art", 7500, DiceRoll(1, 4)), None),
        (14, ("gems", 5000, DiceRoll(1, 8)), None),
        (22, ("gems", 1000, DiceRoll(3, 6)), [("C", DiceRoll(1, 8))]),
        (30, ("art", 2500, DiceRoll(1, 10)), [("C", DiceRoll(1, 8))]),
        (38, ("art", 7500, DiceRoll(1, 4)), [("C", DiceRoll(1, 8))]),
        (46, ("gems", 5000, DiceRoll(1, 8)), [("C", DiceRoll(1, 8))]),
        (52, ("gems", 1000, DiceRoll(3, 6)), [("D", DiceRoll(1, 6))]),
        (58, ("art", 2500, DiceRoll(1, 10)), [("D", DiceRoll(1, 6))]),
        (63, ("art", 7500, DiceRoll(1, 4)), [("D", DiceRoll(1, 6))]),
        (68, ("gems", 5000, DiceRoll(1, 8)), [("D", DiceRoll(1, 6))]),
        (69, ("gems", 1000, DiceRoll(3, 6)), [("E", DiceRoll(1, 6))]),
        (70, ("art", 2500, DiceRoll(1, 10)), [("E", DiceRoll(1, 6))]),
        (71, ("art", 7500, DiceRoll(1, 4)), [("E", DiceRoll(1, 6))]),
        (72, ("gems", 5000, DiceRoll(1, 8)), [("E", DiceRoll(1, 6))]),
        (74, ("gems", 1000, DiceRoll(3, 6)), [("G", DiceRoll(1, 4))]),
        (76, ("art", 2500, DiceRoll(1, 10)), [("G", DiceRoll(1, 4))]),
        (78, ("art", 7500, DiceRoll(1, 4)), [("G", DiceRoll(1, 4))]),
        (80, ("gems", 5000, DiceRoll(1, 8)), [("G", DiceRoll(1, 4))]),
        (85, ("gems", 1000, DiceRoll(3, 6)), [("H", DiceRoll(1, 6))]),
        (90, ("art", 2500, DiceRoll(1, 10)), [("H", DiceRoll(1, 6))]),
        (95, ("art", 7500, DiceRoll(1, 4)), [("H", DiceRoll(1, 6))]),
        (100, ("gems", 5000, DiceRoll(1, 8)), [("I", DiceRoll(1, 6))]),
    ],
}

# =============================================================================
# Gem Lists by Value (DMG 2024)
# =============================================================================

GEMS = {
    10: [
        "Azurite", "Banded agate", "Blue quartz", "Eye agate", "Hematite",
        "Lapis lazuli", "Malachite", "Moss agate", "Obsidian", "Rhodochrosite",
        "Tiger eye", "Turquoise",
    ],
    50: [
        "Bloodstone", "Carnelian", "Chalcedony", "Chrysoprase", "Citrine",
        "Jasper", "Moonstone", "Onyx", "Quartz", "Sardonyx",
        "Star rose quartz", "Zircon",
    ],
    100: [
        "Amber", "Amethyst", "Chrysoberyl", "Coral", "Garnet",
        "Jade", "Jet", "Pearl", "Spinel", "Tourmaline",
    ],
    500: [
        "Alexandrite", "Aquamarine", "Black pearl", "Blue spinel", "Peridot", "Topaz",
    ],
    1000: [
        "Black opal", "Blue sapphire", "Emerald", "Fire opal", "Opal",
        "Star ruby", "Star sapphire", "Yellow sapphire",
    ],
    5000: [
        "Black sapphire", "Diamond", "Jacinth", "Ruby",
    ],
}

# =============================================================================
# Art Object Lists by Value (DMG 2024)
# =============================================================================

ART_OBJECTS = {
    25: [
        "Silver ewer", "Carved bone statuette", "Small gold bracelet",
        "Cloth-of-gold vestments", "Black velvet mask with silver thread",
        "Copper chalice with silver filigree", "Pair of engraved bone dice",
        "Small mirror in painted wooden frame", "Embroidered silk handkerchief",
        "Gold locket with painted portrait",
    ],
    250: [
        "Gold ring set with bloodstones", "Carved ivory statuette",
        "Large gold bracelet", "Silver necklace with gemstone pendant",
        "Bronze crown", "Silk robe with gold embroidery",
        "Large well-made tapestry", "Brass mug with jade inlay",
        "Box of turquoise animal figurines", "Gold bird cage with electrum filigree",
    ],
    750: [
        "Silver chalice set with moonstones", "Silver-plated longsword with jet in hilt",
        "Carved harp of exotic wood with ivory inlay", "Small gold idol",
        "Gold dragon comb set with red garnets", "Bottle stopper with gold and amethysts",
        "Ceremonial electrum dagger with black pearl", "Silver and gold brooch",
        "Obsidian statuette with gold fittings", "Painted gold war mask",
    ],
    2500: [
        "Fine gold chain set with fire opal", "Old masterpiece painting",
        "Embroidered mantle set with moonstones", "Platinum bracelet with sapphire",
        "Embroidered glove set with jewel chips", "Jeweled anklet",
        "Gold music box", "Gold circlet with four aquamarines",
        "Eye patch with blue sapphire and moonstone", "Necklace of small pink pearls",
    ],
    7500: [
        "Jeweled gold crown", "Jeweled platinum ring",
        "Small gold statuette set with rubies", "Gold cup set with emeralds",
        "Gold jewelry box with platinum filigree", "Painted gold child's sarcophagus",
        "Jade game board with solid gold playing pieces",
        "Bejeweled ivory drinking horn with gold filigree",
    ],
}

# =============================================================================
# Magic Item Tables A-I (DMG 2024)
# =============================================================================

MAGIC_ITEM_TABLES = {
    "A": [
        (50, "Potion of Healing"),
        (60, "Spell Scroll (Cantrip)"),
        (70, "Potion of Climbing"),
        (90, "Spell Scroll (1st Level)"),
        (94, "Spell Scroll (2nd Level)"),
        (98, "Potion of Greater Healing"),
        (100, "Bag of Holding"),
    ],
    "B": [
        (15, "Potion of Greater Healing"),
        (22, "Potion of Fire Breath"),
        (29, "Potion of Resistance"),
        (34, "Ammunition, +1"),
        (39, "Potion of Animal Friendship"),
        (44, "Potion of Hill Giant Strength"),
        (49, "Potion of Growth"),
        (54, "Potion of Water Breathing"),
        (59, "Spell Scroll (2nd Level)"),
        (64, "Spell Scroll (3rd Level)"),
        (67, "Bag of Holding"),
        (70, "Keoghtom's Ointment"),
        (73, "Oil of Slipperiness"),
        (75, "Dust of Disappearance"),
        (77, "Dust of Dryness"),
        (79, "Dust of Sneezing and Choking"),
        (81, "Elemental Gem"),
        (83, "Philter of Love"),
        (100, "Potion of Heroism"),
    ],
    "C": [
        (15, "Potion of Superior Healing"),
        (22, "Spell Scroll (4th Level)"),
        (27, "Ammunition, +2"),
        (32, "Potion of Clairvoyance"),
        (37, "Potion of Diminution"),
        (42, "Potion of Gaseous Form"),
        (47, "Potion of Frost Giant Strength"),
        (52, "Potion of Stone Giant Strength"),
        (57, "Potion of Heroism"),
        (62, "Potion of Invulnerability"),
        (67, "Potion of Mind Reading"),
        (72, "Spell Scroll (5th Level)"),
        (75, "Elixir of Health"),
        (78, "Oil of Etherealness"),
        (81, "Potion of Fire Giant Strength"),
        (84, "Quaal's Feather Token"),
        (87, "Scroll of Protection"),
        (89, "Bag of Beans"),
        (91, "Bead of Force"),
        (100, "Chime of Opening"),
    ],
    "D": [
        (20, "Potion of Supreme Healing"),
        (30, "Potion of Invisibility"),
        (40, "Potion of Speed"),
        (50, "Spell Scroll (6th Level)"),
        (57, "Spell Scroll (7th Level)"),
        (62, "Ammunition, +3"),
        (67, "Oil of Sharpness"),
        (72, "Potion of Flying"),
        (77, "Potion of Cloud Giant Strength"),
        (82, "Potion of Longevity"),
        (87, "Potion of Vitality"),
        (92, "Spell Scroll (8th Level)"),
        (95, "Horseshoes of a Zephyr"),
        (98, "Nolzur's Marvelous Pigments"),
        (100, "Bag of Devouring"),
    ],
    "E": [
        (30, "Spell Scroll (8th Level)"),
        (55, "Potion of Storm Giant Strength"),
        (70, "Potion of Supreme Healing"),
        (85, "Spell Scroll (9th Level)"),
        (93, "Universal Solvent"),
        (98, "Arrow of Slaying"),
        (100, "Sovereign Glue"),
    ],
    "F": [
        (15, "Weapon, +1"),
        (18, "Shield, +1"),
        (21, "Sentinel Shield"),
        (23, "Amulet of Proof against Detection and Location"),
        (25, "Boots of Elvenkind"),
        (27, "Boots of Striding and Springing"),
        (29, "Bracers of Archery"),
        (31, "Brooch of Shielding"),
        (33, "Broom of Flying"),
        (35, "Cloak of Elvenkind"),
        (37, "Cloak of Protection"),
        (39, "Gauntlets of Ogre Power"),
        (41, "Hat of Disguise"),
        (43, "Javelin of Lightning"),
        (45, "Pearl of Power"),
        (47, "Rod of the Pact Keeper, +1"),
        (49, "Slippers of Spider Climbing"),
        (51, "Staff of the Adder"),
        (53, "Staff of the Python"),
        (55, "Sword of Vengeance"),
        (57, "Trident of Fish Command"),
        (59, "Wand of Magic Missiles"),
        (61, "Wand of the War Mage, +1"),
        (63, "Wand of Web"),
        (65, "Weapon of Warning"),
        (67, "Adamantine Armor (Chain Mail)"),
        (69, "Adamantine Armor (Chain Shirt)"),
        (71, "Adamantine Armor (Scale Mail)"),
        (74, "Bag of Tricks (Gray)"),
        (76, "Bag of Tricks (Rust)"),
        (78, "Bag of Tricks (Tan)"),
        (80, "Boots of the Winterlands"),
        (82, "Circlet of Blasting"),
        (84, "Deck of Illusions"),
        (86, "Eversmoking Bottle"),
        (88, "Eyes of Charming"),
        (90, "Eyes of the Eagle"),
        (92, "Figurine of Wondrous Power (Silver Raven)"),
        (94, "Gem of Brightness"),
        (96, "Gloves of Missile Snaring"),
        (98, "Gloves of Swimming and Climbing"),
        (100, "Gloves of Thievery"),
    ],
    "G": [
        (11, "Weapon, +2"),
        (14, "Figurine of Wondrous Power"),
        (18, "Adamantine Armor (Breastplate)"),
        (21, "Amulet of Health"),
        (24, "Armor of Resistance"),
        (27, "Armor, +1"),
        (30, "Arrow-Catching Shield"),
        (33, "Belt of Dwarvenkind"),
        (36, "Belt of Hill Giant Strength"),
        (39, "Berserker Axe"),
        (42, "Boots of Levitation"),
        (45, "Boots of Speed"),
        (48, "Bowl of Commanding Water Elementals"),
        (51, "Bracers of Defense"),
        (54, "Brazier of Commanding Fire Elementals"),
        (57, "Cape of the Mountebank"),
        (60, "Censer of Controlling Air Elementals"),
        (63, "Armor, +2 (Chain Mail)"),
        (66, "Cloak of Displacement"),
        (69, "Cloak of the Bat"),
        (72, "Cube of Force"),
        (75, "Daern's Instant Fortress"),
        (77, "Dagger of Venom"),
        (79, "Dimensional Shackles"),
        (81, "Dragon Slayer"),
        (83, "Elven Chain"),
        (85, "Flame Tongue"),
        (87, "Gem of Seeing"),
        (89, "Giant Slayer"),
        (91, "Glamoured Studded Leather"),
        (93, "Helm of Teleportation"),
        (95, "Horn of Blasting"),
        (97, "Horn of Valhalla (Silver)"),
        (99, "Instrument of the Bards (Canaith Mandolin)"),
        (100, "Ioun Stone (Awareness)"),
    ],
    "H": [
        (10, "Weapon, +3"),
        (12, "Amulet of the Planes"),
        (14, "Carpet of Flying"),
        (16, "Crystal Ball"),
        (18, "Ring of Regeneration"),
        (20, "Ring of Shooting Stars"),
        (22, "Ring of Telekinesis"),
        (24, "Robe of Scintillating Colors"),
        (26, "Robe of Stars"),
        (28, "Rod of Absorption"),
        (30, "Rod of Alertness"),
        (32, "Rod of Security"),
        (34, "Rod of the Pact Keeper, +3"),
        (36, "Scimitar of Speed"),
        (38, "Shield, +3"),
        (40, "Staff of Fire"),
        (42, "Staff of Frost"),
        (44, "Staff of Power"),
        (46, "Staff of Striking"),
        (48, "Staff of Thunder and Lightning"),
        (50, "Sword of Sharpness"),
        (52, "Wand of Polymorph"),
        (54, "Wand of the War Mage, +3"),
        (56, "Armor, +2"),
        (58, "Armor, +3 (Half Plate)"),
        (60, "Armor of Invulnerability"),
        (62, "Belt of Fire Giant Strength"),
        (64, "Belt of Frost Giant Strength"),
        (66, "Candle of Invocation"),
        (68, "Cloak of Arachnida"),
        (70, "Dancing Sword"),
        (72, "Demon Armor"),
        (74, "Dragon Scale Mail"),
        (76, "Dwarven Plate"),
        (78, "Dwarven Thrower"),
        (80, "Efreeti Bottle"),
        (82, "Figurine of Wondrous Power (Obsidian Steed)"),
        (84, "Frost Brand"),
        (86, "Helm of Brilliance"),
        (88, "Horn of Valhalla (Bronze)"),
        (90, "Instrument of the Bards (Anstruth Harp)"),
        (92, "Ioun Stone (Absorption)"),
        (94, "Mirror of Life Trapping"),
        (96, "Nine Lives Stealer"),
        (98, "Oathbow"),
        (100, "Spellguard Shield"),
    ],
    "I": [
        (5, "Defender"),
        (10, "Hammer of Thunderbolts"),
        (15, "Luck Blade"),
        (20, "Sword of Answering"),
        (23, "Holy Avenger"),
        (26, "Ring of Djinni Summoning"),
        (29, "Ring of Invisibility"),
        (32, "Ring of Spell Turning"),
        (35, "Rod of Lordly Might"),
        (38, "Staff of the Magi"),
        (41, "Vorpal Sword"),
        (43, "Belt of Cloud Giant Strength"),
        (45, "Armor, +3 (Breastplate)"),
        (47, "Belt of Storm Giant Strength"),
        (49, "Cloak of Invisibility"),
        (51, "Crystal Ball (Legendary)"),
        (53, "Iron Flask"),
        (55, "Armor, +3 (Studded Leather)"),
        (57, "Ioun Stone (Greater Absorption)"),
        (59, "Apparatus of Kwalish"),
        (61, "Armor of Invulnerability"),
        (63, "Belt of Storm Giant Strength"),
        (65, "Cubic Gate"),
        (67, "Deck of Many Things"),
        (69, "Efreeti Chain"),
        (71, "Horn of Valhalla (Iron)"),
        (73, "Instrument of the Bards (Ollamh Harp)"),
        (75, "Ioun Stone (Regeneration)"),
        (77, "Plate Armor of Etherealness"),
        (79, "Plate Armor of Resistance"),
        (81, "Ring of Air Elemental Command"),
        (83, "Ring of Earth Elemental Command"),
        (85, "Ring of Fire Elemental Command"),
        (87, "Ring of Three Wishes"),
        (89, "Ring of Water Elemental Command"),
        (91, "Sphere of Annihilation"),
        (93, "Talisman of Pure Good"),
        (95, "Talisman of the Sphere"),
        (97, "Talisman of Ultimate Evil"),
        (99, "Tome of the Stilled Tongue"),
        (100, "Well of Many Worlds"),
    ],
}


# =============================================================================
# Treasure Dataclass
# =============================================================================


@dataclass
class Treasure:
    """Generated treasure container."""

    coins: dict[str, int] = field(default_factory=dict)
    gems: list[tuple[int, str]] = field(default_factory=list)
    art_objects: list[tuple[int, str]] = field(default_factory=list)
    magic_items: list[str] = field(default_factory=list)
    source_cr: Optional[float] = None
    treasure_type: str = "hoard"


# =============================================================================
# Loot Generator
# =============================================================================


class LootGenerator:
    """Generates treasure using DMG 2024 tables."""

    def __init__(
        self,
        reference_index_path: Optional[Path] = None,
        seed: Optional[int] = None,
    ):
        """Initialize the generator.

        Args:
            reference_index_path: Path to reference-index.json for item linking
            seed: Random seed for deterministic output
        """
        self.rng = random.Random(seed)
        self.linker: Optional[ReferenceLinker] = None

        if reference_index_path:
            try:
                self.linker = ReferenceLinker(reference_index_path.parent)
            except FileNotFoundError:
                pass  # No reference data available

    def generate_individual(self, cr: float, count: int = 1) -> Treasure:
        """Generate individual treasure for defeated creatures.

        Args:
            cr: Challenge Rating of creatures
            count: Number of creatures

        Returns:
            Treasure with coins only
        """
        tier = get_cr_tier(cr)
        table = INDIVIDUAL_TREASURE[tier]

        coins: dict[str, int] = {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}

        for _ in range(count):
            roll = roll_d100(self.rng)
            for threshold, coin_dice in table:
                if roll <= threshold:
                    for coin_type, dice in coin_dice.items():
                        coins[coin_type] += roll_dice(dice, self.rng)
                    break

        # Remove zero values
        coins = {k: v for k, v in coins.items() if v > 0}

        return Treasure(
            coins=coins,
            source_cr=cr,
            treasure_type="individual",
        )

    def generate_hoard(self, cr: float) -> Treasure:
        """Generate a treasure hoard.

        Args:
            cr: Challenge Rating for hoard tier

        Returns:
            Treasure with coins, gems, art objects, and magic items
        """
        tier = get_cr_tier(cr)

        # Roll base coins
        coins: dict[str, int] = {}
        for coin_type, dice in HOARD_COINS[tier].items():
            coins[coin_type] = roll_dice(dice, self.rng)

        # Remove zero values
        coins = {k: v for k, v in coins.items() if v > 0}

        # Roll for gems/art and magic items
        roll = roll_d100(self.rng)
        gems: list[tuple[int, str]] = []
        art_objects: list[tuple[int, str]] = []
        magic_items: list[str] = []

        table = HOARD_TABLES[tier]
        for threshold, gem_art_info, magic_info in table:
            if roll <= threshold:
                # Handle gems/art
                if gem_art_info:
                    item_type, value, count_dice = gem_art_info
                    item_count = roll_dice(count_dice, self.rng)
                    items = self._select_gems_or_art(item_type, value, item_count)
                    if item_type == "gems":
                        gems = items
                    else:
                        art_objects = items

                # Handle magic items
                if magic_info:
                    for table_letter, count_dice in magic_info:
                        item_count = roll_dice(count_dice, self.rng) if count_dice else 1
                        magic_items.extend(self.roll_magic_item_table(table_letter, item_count))

                break

        return Treasure(
            coins=coins,
            gems=gems,
            art_objects=art_objects,
            magic_items=magic_items,
            source_cr=cr,
            treasure_type="hoard",
        )

    def roll_magic_item_table(self, table: str, count: int = 1) -> list[str]:
        """Roll on a specific magic item table.

        Args:
            table: Table letter (A-I)
            count: Number of items to roll

        Returns:
            List of item names
        """
        table_upper = table.upper()
        if table_upper not in MAGIC_ITEM_TABLES:
            raise ValueError(f"Invalid magic item table: {table}. Use A-I.")

        items = []
        table_data = MAGIC_ITEM_TABLES[table_upper]

        for _ in range(count):
            roll = roll_d100(self.rng)
            for threshold, item_name in table_data:
                if roll <= threshold:
                    items.append(item_name)
                    break

        return items

    def _select_gems_or_art(
        self,
        item_type: str,
        value: int,
        count: int,
    ) -> list[tuple[int, str]]:
        """Select random gems or art objects.

        Args:
            item_type: "gems" or "art"
            value: Value tier in gp
            count: Number to select

        Returns:
            List of (value, name) tuples
        """
        pool = GEMS.get(value, []) if item_type == "gems" else ART_OBJECTS.get(value, [])

        if not pool:
            # Fallback for missing value tiers
            singular = "gem" if item_type == "gems" else "art object"
            return [(value, f"{value} gp {singular}")] * count

        return [(value, self.rng.choice(pool)) for _ in range(count)]


# =============================================================================
# Output Formatting
# =============================================================================


class TreasureFormatter:
    """Formats treasure for output."""

    def __init__(self, linker: Optional[ReferenceLinker] = None):
        """Initialize formatter.

        Args:
            linker: Reference linker for magic item links
        """
        self.linker = linker

    def format_console(self, treasure: Treasure, title: Optional[str] = None) -> str:
        """Format treasure for console output.

        Args:
            treasure: Treasure to format
            title: Optional title override

        Returns:
            Formatted markdown string
        """
        if title is None:
            if treasure.treasure_type == "individual":
                cr_str = f"CR {treasure.source_cr}" if treasure.source_cr is not None else ""
                title = f"Individual Treasure ({cr_str})" if cr_str else "Individual Treasure"
            else:
                tier = get_cr_tier(treasure.source_cr) if treasure.source_cr is not None else 1
                tier_ranges = {1: "0-4", 2: "5-10", 3: "11-16", 4: "17+"}
                title = f"Treasure Hoard (CR {tier_ranges[tier]})"

        lines = [f"## {title}", ""]

        # Coins
        if treasure.coins:
            coin_parts = []
            for coin_type in ["pp", "gp", "ep", "sp", "cp"]:
                if treasure.coins.get(coin_type, 0) > 0:
                    coin_parts.append(f"{treasure.coins[coin_type]:,} {coin_type}")
            if coin_parts:
                lines.append(f"**Coins:** {', '.join(coin_parts)}")
                lines.append("")

        # Gems
        if treasure.gems:
            by_value: dict[int, list[str]] = {}
            for value, name in treasure.gems:
                by_value.setdefault(value, []).append(name)
            for value in sorted(by_value.keys()):
                names = by_value[value]
                lines.append(f"**Gems ({len(names)}x {value} gp):**")
                for name in names:
                    lines.append(f"- {name}")
            lines.append("")

        # Art Objects
        if treasure.art_objects:
            by_value = {}
            for value, name in treasure.art_objects:
                by_value.setdefault(value, []).append(name)
            for value in sorted(by_value.keys()):
                names = by_value[value]
                lines.append(f"**Art Objects ({len(names)}x {value} gp):**")
                for name in names:
                    lines.append(f"- {name}")
            lines.append("")

        # Magic Items
        if treasure.magic_items:
            lines.append("**Magic Items:**")
            for item in treasure.magic_items:
                link = self._link_item(item)
                lines.append(f"- {link}")
            lines.append("")

        return "\n".join(lines)

    def _link_item(self, item_name: str) -> str:
        """Create a reference link for an item.

        Args:
            item_name: Name of the magic item

        Returns:
            Markdown link or plain name with [No Reference]
        """
        if self.linker:
            # Try to find item in reference data
            entry = self.linker.find(item_name, "items")
            if entry:
                path = entry.get("path", "")
                if path:
                    return f"[{item_name}](../../books/{path})"

        return f"{item_name} [No Reference]"


# =============================================================================
# Session Integration
# =============================================================================


def find_loot_section(content: str) -> Optional[int]:
    """Find the Loot & Rewards section in session content.

    Args:
        content: Session file content

    Returns:
        Position after header or None if not found
    """
    patterns = [
        r"^## Loot & Rewards\s*$",
        r"^## Loot and Rewards\s*$",
        r"^## Treasure\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.end()

    return None


def append_to_session(
    session_number: int,
    treasure_md: str,
    campaign_dir: Path,
) -> Path:
    """Append treasure to a session's Loot & Rewards section.

    Args:
        session_number: Session number
        treasure_md: Formatted treasure markdown
        campaign_dir: Path to campaign directory

    Returns:
        Path to updated session file
    """
    session_file = campaign_dir / "sessions" / f"session-{session_number:03d}.md"

    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")

    content = session_file.read_text(encoding="utf-8")

    # Find the Loot & Rewards section
    section_pos = find_loot_section(content)

    if section_pos:
        # Find next section or end
        next_section = re.search(r"^## ", content[section_pos:], re.MULTILINE)
        if next_section:
            insert_pos = section_pos + next_section.start()
        else:
            insert_pos = len(content)

        # Insert treasure before next section
        before = content[:insert_pos].rstrip()
        after = content[insert_pos:].lstrip()

        # Format the treasure block
        treasure_block = f"\n\n---\n\n{treasure_md.strip()}"

        if after:
            new_content = before + treasure_block + "\n\n" + after
        else:
            new_content = before + treasure_block + "\n"
    else:
        # Add the section at the end
        new_content = content.rstrip() + f"\n\n## Loot & Rewards\n\n{treasure_md.strip()}\n"

    session_file.write_text(new_content, encoding="utf-8")
    return session_file


# =============================================================================
# Encounter Integration
# =============================================================================


def load_encounter_cr(encounter_name: str, campaign_dir: Path) -> float:
    """Load CR from an encounter file.

    Args:
        encounter_name: Name of the encounter
        campaign_dir: Path to campaign directory

    Returns:
        Highest CR found in encounter
    """
    cr, _ = load_encounter_cr_and_count(encounter_name, campaign_dir)
    return cr


def load_encounter_cr_and_count(encounter_name: str, campaign_dir: Path) -> tuple[float, int]:
    """Load CR and total creature count from an encounter file.

    Args:
        encounter_name: Name of the encounter
        campaign_dir: Path to campaign directory

    Returns:
        Tuple of (highest CR, total creature count)
    """
    encounter_file = campaign_dir / "encounters" / f"{slugify(encounter_name)}.md"

    if not encounter_file.exists():
        encounter_file = campaign_dir / "encounters" / f"{encounter_name}.md"

    if not encounter_file.exists():
        raise FileNotFoundError(f"Encounter not found: {encounter_name}")

    content = encounter_file.read_text(encoding="utf-8")

    # Look for creature table rows: | Name | CR | XP | Count | Total XP |
    # Capture CR and Count (columns 2 and 4)
    row_pattern = r"^\|\s*[^|]+\s*\|\s*(\d+(?:/\d+)?)\s*\|\s*\d[\d,]*\s*\|\s*(\d+)\s*\|\s*[\d,]+\s*\|"
    matches = re.findall(row_pattern, content, re.MULTILINE)

    if matches:
        crs = [parse_cr(cr) for cr, _ in matches]
        total_count = sum(int(count) for _, count in matches)
        return max(crs), total_count

    # Fallback: CR only from text
    cr_text_pattern = r"CR\s+(\d+(?:/\d+)?)"
    cr_matches = re.findall(cr_text_pattern, content)
    if cr_matches:
        crs = [parse_cr(c) for c in cr_matches]
        return max(crs), 1

    raise ValueError(f"Could not determine CR from encounter: {encounter_name}")


# =============================================================================
# CLI
# =============================================================================


def find_repo_root() -> Path:
    """Find the repository root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "books").exists() or (current / "scripts").exists():
            return current
        current = current.parent
    return Path.cwd()


def main():
    parser = argparse.ArgumentParser(
        description="Generate D&D 5e treasure using DMG 2024 tables.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate individual treasure for a CR 3 creature
    python scripts/campaign/loot_generator.py individual --cr 3

    # Generate individual treasure for 4 creatures
    python scripts/campaign/loot_generator.py individual --cr 5 --count 4

    # Generate a treasure hoard for CR 7
    python scripts/campaign/loot_generator.py hoard --cr 7

    # Roll on Magic Item Table C
    python scripts/campaign/loot_generator.py magic-item --table C

    # Generate per-creature loot for a saved encounter (default)
    python scripts/campaign/loot_generator.py for-encounter "goblin-ambush"
    # Or generate a single hoard
    python scripts/campaign/loot_generator.py for-encounter "goblin-ambush" --hoard

    # Generate and save to session
    python scripts/campaign/loot_generator.py hoard --cr 5 --add-to-session 3
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Individual treasure
    individual_parser = subparsers.add_parser(
        "individual",
        help="Generate individual treasure (coins only)",
    )
    individual_parser.add_argument(
        "--cr",
        type=str,
        required=True,
        help="Challenge Rating (0-30, or 1/8, 1/4, 1/2)",
    )
    individual_parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of creatures (default: 1)",
    )
    individual_parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducible output",
    )

    # Hoard
    hoard_parser = subparsers.add_parser(
        "hoard",
        help="Generate treasure hoard (coins, gems, art, magic items)",
    )
    hoard_parser.add_argument(
        "--cr",
        type=str,
        required=True,
        help="Challenge Rating (0-30, or 1/8, 1/4, 1/2)",
    )
    hoard_parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducible output",
    )
    hoard_parser.add_argument(
        "--add-to-session",
        type=int,
        metavar="N",
        help="Append loot to session N",
    )

    # Magic item
    magic_parser = subparsers.add_parser(
        "magic-item",
        help="Roll on a specific magic item table",
    )
    magic_parser.add_argument(
        "--table", "-t",
        type=str,
        required=True,
        help="Table letter (A-I)",
    )
    magic_parser.add_argument(
        "--count", "-n",
        type=int,
        default=1,
        help="Number of items to roll (default: 1)",
    )
    magic_parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducible output",
    )

    # For encounter
    encounter_parser = subparsers.add_parser(
        "for-encounter",
        help="Generate loot for a saved encounter",
    )
    encounter_parser.add_argument(
        "encounter",
        type=str,
        help="Encounter name (from campaign/encounters/)",
    )
    encounter_parser.add_argument(
        "--hoard", "-H",
        action="store_true",
        help="Generate a single hoard instead of per-creature individual treasure (default)",
    )
    encounter_parser.add_argument(
        "--seed", "-s",
        type=int,
        help="Random seed for reproducible output",
    )
    encounter_parser.add_argument(
        "--add-to-session",
        type=int,
        metavar="N",
        help="Append loot to session N",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Find repo root
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"
    books_dir = repo_root / "books"
    index_path = books_dir / "reference-index.json"

    # Initialize generator
    seed = getattr(args, "seed", None)
    generator = LootGenerator(
        reference_index_path=index_path if index_path.exists() else None,
        seed=seed,
    )

    # Initialize formatter
    try:
        linker = ReferenceLinker(books_dir)
    except FileNotFoundError:
        linker = None
    formatter = TreasureFormatter(linker)

    # Handle commands
    try:
        if args.command == "individual":
            cr = parse_cr(args.cr)
            treasure = generator.generate_individual(cr, args.count)
            output = formatter.format_console(treasure)
            print(output)

        elif args.command == "hoard":
            cr = parse_cr(args.cr)
            treasure = generator.generate_hoard(cr)
            output = formatter.format_console(treasure)
            print(output)

            if args.add_to_session:
                if not campaign_dir.exists():
                    print("\nError: Campaign directory not found. Run init_campaign.py first.")
                    sys.exit(1)
                session_path = append_to_session(args.add_to_session, output, campaign_dir)
                print(f"\nLoot added to: {session_path}")

        elif args.command == "magic-item":
            items = generator.roll_magic_item_table(args.table, args.count)
            print(f"## Magic Item Table {args.table.upper()}\n")
            for item in items:
                if linker:
                    entry = linker.find(item, "items")
                    if entry and entry.get("path"):
                        print(f"- [{item}](../../books/{entry['path']})")
                    else:
                        print(f"- {item} [No Reference]")
                else:
                    print(f"- {item}")

        elif args.command == "for-encounter":
            if not campaign_dir.exists():
                print("Error: Campaign directory not found. Run init_campaign.py first.")
                sys.exit(1)

            cr, creature_count = load_encounter_cr_and_count(args.encounter, campaign_dir)
            print(f"Encounter '{args.encounter}' - CR {cr}, {creature_count} creature(s)")
            print()

            if args.hoard:
                treasure = generator.generate_hoard(cr)
            else:
                treasure = generator.generate_individual(cr, creature_count)

            output = formatter.format_console(treasure, f"Treasure ({args.encounter})")
            print(output)

            if args.add_to_session:
                session_path = append_to_session(args.add_to_session, output, campaign_dir)
                print(f"\nLoot added to: {session_path}")

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
