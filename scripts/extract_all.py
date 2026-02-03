#!/usr/bin/env python3
"""
Extract all D&D books for Spelljammer campaign.

This script extracts content from the 5etools-src submodule and organizes it
into the books/ directory structure. Run this after cloning the repository
to regenerate the extracted content.

Usage:
    python scripts/extract_all.py
"""

import json
import subprocess
import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extract_book import EntryConverter
from extractors import (
    SpellExtractor, CreatureExtractor, ItemExtractor,
    FeatExtractor, BackgroundExtractor, SpeciesExtractor,
    ClassExtractor, EquipmentExtractor, RulesExtractor,
    VehicleExtractor, OptionalFeatureExtractor, TrapExtractor,
    LanguageExtractor, BastionExtractor, DeityExtractor,
    RewardExtractor, ObjectExtractor, DeckExtractor,
    SkillExtractor, ItemMasteryExtractor, EncounterExtractor, LootExtractor,
    IndexCollector
)
from lib.source_config import SourceConfig

# Global storage for extractors (for index generation)
EXTRACTORS = {}

# Global source configuration (loaded in main())
SOURCE_CONFIG: SourceConfig = None

# Repository root (parent of scripts/)
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "5etools-src" / "data"
BOOKS_DIR = REPO_ROOT / "books"
REFERENCE_DIR = BOOKS_DIR / "reference"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract_book.py"

# Books to extract (filtered by SOURCE_CONFIG)
# Each entry has a "code" field that maps to source codes
EXTRACTIONS = [
    # Core 2024 Rules
    {
        "name": "Player's Handbook 2024",
        "code": "XPHB",
        "source": DATA_DIR / "book" / "book-xphb.json",
        "output": BOOKS_DIR / "core" / "xphb",
    },
    {
        "name": "Dungeon Master's Guide 2024",
        "code": "XDMG",
        "source": DATA_DIR / "book" / "book-xdmg.json",
        "output": BOOKS_DIR / "core" / "xdmg",
    },
    {
        "name": "Monster Manual 2024",
        "code": "XMM",
        "source": DATA_DIR / "book" / "book-xmm.json",
        "output": BOOKS_DIR / "core" / "xmm",
    },
    # Spelljammer Setting
    {
        "name": "Astral Adventurer's Guide",
        "code": "AAG",
        "source": DATA_DIR / "book" / "book-aag.json",
        "output": BOOKS_DIR / "spelljammer" / "aag",
    },
    {
        "name": "Boo's Astral Menagerie (Book)",
        "code": "BAM",
        "source": DATA_DIR / "book" / "book-bam.json",
        "output": BOOKS_DIR / "spelljammer" / "bam",
    },
    {
        "name": "Boo's Astral Menagerie (Creatures)",
        "code": "BAM",
        "source": DATA_DIR / "bestiary" / "bestiary-bam.json",
        "output": BOOKS_DIR / "spelljammer" / "bam",
    },
    # Spelljammer Adventures
    {
        "name": "Light of Xaryxis",
        "code": "LoX",
        "source": DATA_DIR / "adventure" / "adventure-lox.json",
        "output": BOOKS_DIR / "spelljammer" / "adventures" / "lox",
    },
    {
        "name": "Spelljammer Academy",
        "code": "SJA",
        "source": DATA_DIR / "adventure" / "adventure-sja.json",
        "output": BOOKS_DIR / "spelljammer" / "adventures" / "sja",
    },
    # Eberron - EFA (Artificer class and player options only)
    {
        "name": "Eberron: Artificer & Options",
        "code": "EFA",
        "source": DATA_DIR / "book" / "book-efa.json",
        "output": BOOKS_DIR / "eberron" / "efa",
        "chapters": [0, 1, 2, 8],  # Intro, Artificer, Character Options, Magic Items
    },
    # Eberron - Full book (includes setting content)
    {
        "name": "Eberron: Forge of the Artificer (Full)",
        "code": "EFA-FULL",
        "source": DATA_DIR / "book" / "book-efa.json",
        "output": BOOKS_DIR / "eberron" / "efa",
        # No chapters filter = extract all
    },
    # Eberron: Rising from the Last War (player options only)
    {
        "name": "Eberron: Rising from the Last War (Options)",
        "code": "ERLW",
        "source": DATA_DIR / "book" / "book-erlw.json",
        "output": BOOKS_DIR / "eberron" / "erlw",
        "chapters": [0, 1, 12],  # Welcome, Character Creation, Treasures
    },
    # Eberron: Rising from the Last War (full book)
    {
        "name": "Eberron: Rising from the Last War (Full)",
        "code": "ERLW-FULL",
        "source": DATA_DIR / "book" / "book-erlw.json",
        "output": BOOKS_DIR / "eberron" / "erlw",
    },
    # Explorer's Guide to Wildemount (player options only)
    {
        "name": "Explorer's Guide to Wildemount (Options)",
        "code": "EGW",
        "source": DATA_DIR / "book" / "book-egw.json",
        "output": BOOKS_DIR / "wildemount" / "egw",
        "chapters": [5, 7],  # Character Options, Treasures
    },
    # Explorer's Guide to Wildemount (full book)
    {
        "name": "Explorer's Guide to Wildemount (Full)",
        "code": "EGW-FULL",
        "source": DATA_DIR / "book" / "book-egw.json",
        "output": BOOKS_DIR / "wildemount" / "egw",
    },
]

# Master index content
README_CONTENT = '''# D&D 5e Reference Library

This directory contains extracted D&D 5th Edition content organized for a **Spelljammer campaign**. Content is sourced from the 5etools data repository and converted to markdown for easy reference.

## Quick Reference

| Book | Code | Type | Location |
| ---- | ---- | ---- | -------- |
| Player's Handbook (2024) | XPHB | Core Rules | [core/xphb/](core/xphb/) |
| Dungeon Master's Guide (2024) | XDMG | Core Rules | [core/xdmg/](core/xdmg/) |
| Monster Manual (2024) | XMM | Core Rules | [core/xmm/](core/xmm/) |
| Astral Adventurer's Guide | AAG | Spelljammer | [spelljammer/aag/](spelljammer/aag/) |
| Boo's Astral Menagerie | BAM | Spelljammer | [spelljammer/bam/](spelljammer/bam/) |
| Light of Xaryxis | LoX | Adventure | [spelljammer/adventures/lox/](spelljammer/adventures/lox/) |
| Spelljammer Academy | SJA | Adventure | [spelljammer/adventures/sja/](spelljammer/adventures/sja/) |
| Eberron: Forge of the Artificer | EFA | Supplement | [eberron/efa/](eberron/efa/) |

---

## Core Rules (2024 Edition)

### Player's Handbook (XPHB)

The essential rulebook for players, covering character creation, classes, spells, and gameplay.

| Chapter | File |
| ------- | ---- |
| Introduction | [00-introduction-welcome-to-adventure.md](core/xphb/00-introduction-welcome-to-adventure.md) |
| Playing the Game | [01-chapter-1-playing-the-game.md](core/xphb/01-chapter-1-playing-the-game.md) |
| Creating a Character | [02-chapter-2-creating-a-character.md](core/xphb/02-chapter-2-creating-a-character.md) |
| Character Classes | [03-chapter-3-character-classes.md](core/xphb/03-chapter-3-character-classes.md) |
| Character Origins | [04-chapter-4-character-origins.md](core/xphb/04-chapter-4-character-origins.md) |
| Feats | [05-chapter-5-feats.md](core/xphb/05-chapter-5-feats.md) |
| Equipment | [06-chapter-6-equipment.md](core/xphb/06-chapter-6-equipment.md) |
| Spells | [07-chapter-7-spells.md](core/xphb/07-chapter-7-spells.md) |
| The Multiverse | [08-appendix-a-the-multiverse.md](core/xphb/08-appendix-a-the-multiverse.md) |
| Creature Stat Blocks | [09-appendix-b-creature-stat-blocks.md](core/xphb/09-appendix-b-creature-stat-blocks.md) |
| Rules Glossary | [10-rules-glossary.md](core/xphb/10-rules-glossary.md) |

### Dungeon Master's Guide (XDMG)

Guide for running games, creating adventures, and building worlds.

| Chapter | File |
| ------- | ---- |
| The Basics | [00-chapter-1-the-basics.md](core/xdmg/00-chapter-1-the-basics.md) |
| Running the Game | [01-chapter-2-running-the-game.md](core/xdmg/01-chapter-2-running-the-game.md) |
| DM's Toolbox | [02-chapter-3-dms-toolbox.md](core/xdmg/02-chapter-3-dms-toolbox.md) |
| Creating Adventures | [03-chapter-4-creating-adventures.md](core/xdmg/03-chapter-4-creating-adventures.md) |
| Creating Campaigns | [04-chapter-5-creating-campaigns.md](core/xdmg/04-chapter-5-creating-campaigns.md) |
| Cosmology | [05-chapter-6-cosmology.md](core/xdmg/05-chapter-6-cosmology.md) |
| Treasure | [06-chapter-7-treasure.md](core/xdmg/06-chapter-7-treasure.md) |
| Bastions | [07-chapter-8-bastions.md](core/xdmg/07-chapter-8-bastions.md) |
| Lore Glossary | [08-appendix-a-lore-glossary.md](core/xdmg/08-appendix-a-lore-glossary.md) |
| Maps | [09-appendix-b-maps.md](core/xdmg/09-appendix-b-maps.md) |
| Tracking Sheets | [10-appendix-c-tracking-sheets.md](core/xdmg/10-appendix-c-tracking-sheets.md) |

### Monster Manual (XMM)

Comprehensive bestiary of D&D monsters.

| Section | File |
| ------- | ---- |
| How to Use a Monster | [00-how-to-use-a-monster.md](core/xmm/00-how-to-use-a-monster.md) |
| Monsters A to Z | [01-monsters-a-to-z.md](core/xmm/01-monsters-a-to-z.md) |
| Animals | [02-animals.md](core/xmm/02-animals.md) |
| Monster Lists | [03-monster-lists.md](core/xmm/03-monster-lists.md) |

---

## Spelljammer Setting

### Astral Adventurer's Guide (AAG)

Essential guide for Spelljammer campaigns covering space travel, ships, and the Rock of Bral.

| Chapter | File |
| ------- | ---- |
| Introduction | [00-introduction-vast-oceans-of-adventure.md](spelljammer/aag/00-introduction-vast-oceans-of-adventure.md) |
| Character Options | [01-chapter-1-character-options.md](spelljammer/aag/01-chapter-1-character-options.md) |
| Astral Adventuring | [02-chapter-2-astral-adventuring.md](spelljammer/aag/02-chapter-2-astral-adventuring.md) |
| The Rock of Bral | [03-chapter-3-the-rock-of-bral.md](spelljammer/aag/03-chapter-3-the-rock-of-bral.md) |
| Additional Tables | [04-additional-spelljammer-tables.md](spelljammer/aag/04-additional-spelljammer-tables.md) |

### Boo's Astral Menagerie (BAM)

Bestiary of Spelljammer creatures and space-faring monsters.

- [Introduction](spelljammer/bam/00-introduction.md)
- [Creature Index](spelljammer/bam/index.md) - 72 creatures including:
  - Astral Elves (Aristocrat, Commander, Honor Guard, Star Priest, Warrior)
  - Giff (Shipmate, Shock Trooper, Warlord)
  - Lunar & Solar Dragons (Wyrmling through Ancient)
  - Neogi (Hatchling Swarm, Pirate, Void Hunter)
  - Scavvers (Brown, Gray, Night, Void)
  - And many more...

---

## Spelljammer Adventures

### Light of Xaryxis (LoX)

Epic adventure to save your world from the Xaryxian Empire. Designed for levels 5-8.

| Part | File |
| ---- | ---- |
| Introduction | [00-introduction-wildspace-awaits.md](spelljammer/adventures/lox/00-introduction-wildspace-awaits.md) |
| Part 1: Seeds of Destruction | [01-part-1-seeds-of-destruction.md](spelljammer/adventures/lox/01-part-1-seeds-of-destruction.md) |
| Part 2: Terrors of the Void | [02-part-2-terrors-of-the-void.md](spelljammer/adventures/lox/02-part-2-terrors-of-the-void.md) |
| Part 3: Chaos in Doomspace | [03-part-3-chaos-in-doomspace.md](spelljammer/adventures/lox/03-part-3-chaos-in-doomspace.md) |
| Part 4: Saviors of the Multiverse | [04-part-4-saviors-of-the-multiverse.md](spelljammer/adventures/lox/04-part-4-saviors-of-the-multiverse.md) |

### Spelljammer Academy (SJA)

Introductory adventure series for new spelljammers. Designed for levels 1-4.

| Adventure | File |
| --------- | ---- |
| Orientation | [00-spelljammer-academy-orientation.md](spelljammer/adventures/sja/00-spelljammer-academy-orientation.md) |
| Trial by Fire | [01-spelljammer-academy-trial-by-fire.md](spelljammer/adventures/sja/01-spelljammer-academy-trial-by-fire.md) |
| Realmspace Sortie | [02-spelljammer-academy-realmspace-sortie.md](spelljammer/adventures/sja/02-spelljammer-academy-realmspace-sortie.md) |
| Behold H'Catha | [03-spelljammer-academy-behold-hcatha.md](spelljammer/adventures/sja/03-spelljammer-academy-behold-hcatha.md) |

---

## Eberron Supplement

### Eberron: Forge of the Artificer (EFA)

Selected content from Eberron for use with the Spelljammer campaign. Includes the Artificer class, Eberron species, and magic items.

**Note:** Only selected chapters are extracted (Artificer, Character Options, Magic Items). Dragonmark content is excluded.

| Chapter | File |
| ------- | ---- |
| Introduction | [00-introduction.md](eberron/efa/00-introduction.md) |
| Chapter 1: Artificer | [01-chapter-01-artificer.md](eberron/efa/01-chapter-01-artificer.md) |
| Chapter 2: Character Options | [02-chapter-02-character-options.md](eberron/efa/02-chapter-02-character-options.md) |
| Appendix: Magic Items | [08-appendix-magic-items.md](eberron/efa/08-appendix-magic-items.md) |

---

## Campaign Quick Links

### For Players

- **Character Creation**: [XPHB Chapter 2](core/xphb/02-chapter-2-creating-a-character.md)
- **Spelljammer Backgrounds**: [AAG Chapter 1](spelljammer/aag/01-chapter-1-character-options.md)
- **Classes**: [XPHB Chapter 3](core/xphb/03-chapter-3-character-classes.md)
- **Artificer Class**: [EFA Chapter 1](eberron/efa/01-chapter-01-artificer.md)
- **Species/Origins**: [XPHB Chapter 4](core/xphb/04-chapter-4-character-origins.md)
- **Spells**: [XPHB Chapter 7](core/xphb/07-chapter-7-spells.md)
- **Equipment**: [XPHB Chapter 6](core/xphb/06-chapter-6-equipment.md)
- **Rules Reference**: [XPHB Rules Glossary](core/xphb/10-rules-glossary.md)

### For DMs

- **Running the Game**: [XDMG Chapter 2](core/xdmg/01-chapter-2-running-the-game.md)
- **Spelljammer Rules**: [AAG Chapter 2](spelljammer/aag/02-chapter-2-astral-adventuring.md)
- **The Rock of Bral**: [AAG Chapter 3](spelljammer/aag/03-chapter-3-the-rock-of-bral.md)
- **Spelljammer Creatures**: [BAM Creature Index](spelljammer/bam/index.md)
- **Treasure**: [XDMG Chapter 7](core/xdmg/06-chapter-7-treasure.md)
- **Cosmology**: [XDMG Chapter 6](core/xdmg/05-chapter-6-cosmology.md)

---

## Reference Data

Individual entries for cross-referencing. Each entry has its own markdown file.

### Character Creation

| Reference | Description | Location |
| --------- | ----------- | -------- |
| Classes | 12 classes with subclasses | [reference/classes/](reference/classes/) |
| Species | Player species options | [reference/species/](reference/species/) |
| Backgrounds | Character backgrounds | [reference/backgrounds/](reference/backgrounds/) |
| Feats | Origin and general feats | [reference/feats/](reference/feats/) |

### Spells

- **[Spell Index](reference/spells/index.md)** - Spells organized by level
- Individual spell files in `reference/spells/{level}/`
- Example: [Fireball](reference/spells/3rd-level/fireball.md)

### Creatures

- **[Creature Index](reference/creatures/index.md)** - Creatures organized by CR
- Individual creature files in `reference/creatures/`
- Example: [Adult Red Dragon](reference/creatures/adult-red-dragon.md)

### Items

| Reference | Description | Location |
| --------- | ----------- | -------- |
| Magic Items | Wondrous items, weapons, armor | [reference/items/](reference/items/) |
| Equipment | Mundane gear, weapons, armor | [reference/equipment/](reference/equipment/) |

### Rules Glossary

| Reference | Description | Location |
| --------- | ----------- | -------- |
| Conditions | Blinded, Charmed, Prone, etc. | [reference/rules/conditions/](reference/rules/conditions/) |
| Actions | Attack, Dash, Dodge, etc. | [reference/rules/actions/](reference/rules/actions/) |
| Senses | Darkvision, Blindsight, etc. | [reference/rules/senses/](reference/rules/senses/) |
| Glossary | All rules definitions | [reference/rules/glossary/](reference/rules/glossary/) |

### Spelljammer

| Reference | Description | Location |
| --------- | ----------- | -------- |
| Vehicles | Spelljammer ships | [reference/vehicles/](reference/vehicles/) |

### Additional Reference

| Reference | Description | Location |
| --------- | ----------- | -------- |
| Optional Features | Invocations, Maneuvers, Metamagic | [reference/optional-features/](reference/optional-features/) |
| Traps and Hazards | Traps and environmental hazards | [reference/traps-hazards/](reference/traps-hazards/) |
| Languages | Standard and exotic languages | [reference/languages/](reference/languages/) |
| Bastions | Bastion facilities (2024 DMG) | [reference/bastions/](reference/bastions/) |
| Deities | Gods and pantheons | [reference/deities/](reference/deities/) |
| Rewards | Boons, blessings, charms | [reference/rewards/](reference/rewards/) |
| Objects | Interactive objects | [reference/objects/](reference/objects/) |
| Decks | Card decks (Deck of Many Things, etc.) | [reference/decks/](reference/decks/) |
| Skills | All 18 skills | [reference/skills/](reference/skills/) |
| Weapon Mastery | Cleave, Graze, Nick, etc. | [reference/mastery/](reference/mastery/) |
| Encounters | Random encounter tables | [reference/encounters/](reference/encounters/) |
| Loot Tables | Treasure tables | [reference/loot/](reference/loot/) |

---

## Source

Content extracted from [5etools](https://5e.tools/) data repository using `scripts/extract_all.py`.
'''


def check_submodule():
    """Ensure the 5etools-src submodule is initialized."""
    if not DATA_DIR.exists():
        print("Error: 5etools-src submodule not found.")
        print("Run: git submodule update --init --recursive")
        sys.exit(1)


def extract_book(name: str, source: Path, output: Path, chapters: list = None):
    """Extract a single book using extract_book.py.

    Args:
        name: Display name for the book
        source: Path to the source JSON file
        output: Path to output directory
        chapters: Optional list of chapter indices to extract (0-based). If None, extract all.
    """
    if not source.exists():
        print(f"  Warning: Source not found: {source}")
        return False

    output.mkdir(parents=True, exist_ok=True)

    if chapters is not None:
        # Use chapter filtering - extract directly here
        return _extract_book_with_chapters(name, source, output, chapters)

    result = subprocess.run(
        [sys.executable, str(EXTRACT_SCRIPT), str(source), str(output)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"  Error extracting {name}:")
        print(result.stderr)
        return False

    return True


def _extract_book_with_chapters(name: str, source: Path, output: Path, chapters: list) -> bool:
    """Extract specific chapters from a book.

    Args:
        name: Display name for the book
        source: Path to the source JSON file
        output: Path to output directory
        chapters: List of chapter indices to extract (0-based)
    """
    # Import here to avoid circular imports
    from extract_book import BookExtractor, EntryConverter, TagConverter

    try:
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)

        sections = data.get('data', [])
        if not sections:
            print(f"  Warning: No data sections found in {source}")
            return False

        output.mkdir(parents=True, exist_ok=True)
        converter = EntryConverter(heading_level=1)
        chapter_set = set(chapters)

        extracted_count = 0
        for idx, section in enumerate(sections):
            if idx not in chapter_set:
                continue

            if not isinstance(section, dict):
                continue

            section_name = section.get('name', f'Section {idx}')
            safe_name = _make_safe_filename(section_name)
            filename = f"{idx:02d}-{safe_name}.md"

            # Build content
            parts = []
            page = section.get('page', '')

            if section_name:
                parts.append(f"# {TagConverter.convert_tags(section_name)}")
                if page:
                    parts.append(f"*Page {page}*")
                parts.append("")

            entries = section.get('entries', [])
            content = converter.convert(entries, 0)
            if content:
                parts.append(content)

            output_path = output / filename
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(parts))

            print(f"    Created: {filename}")
            extracted_count += 1

        print(f"    Extracted {extracted_count} of {len(sections)} chapters (filtered)")
        return True

    except Exception as e:
        print(f"  Error extracting {name}: {e}")
        return False


def _make_safe_filename(name: str) -> str:
    """Convert a name to a safe filename."""
    import re
    safe = name.lower()
    safe = re.sub(r'[^\w\s-]', '', safe)
    safe = re.sub(r'[-\s]+', '-', safe)
    return safe.strip('-')[:50]


def create_readme():
    """Create the master index README."""
    readme_path = BOOKS_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(README_CONTENT)
    print(f"Created: {readme_path.relative_to(REPO_ROOT)}")


def extract_spells():
    """Extract spells to individual files."""
    print("Extracting spells...")
    spells_dir = REFERENCE_DIR / "spells"

    extractor = SpellExtractor(str(spells_dir))

    # Map source codes to spell files
    spell_files = {
        "XPHB": "spells-xphb.json",
        "PHB": "spells-phb.json",
        "XGE": "spells-xge.json",
        "TCE": "spells-tce.json",
        "AAG": "spells-aag.json",
        "AI": "spells-ai.json",
        "EGW": "spells-egw.json",
        "FTD": "spells-ftd.json",
        "IDRotF": "spells-idrotf.json",
        "SCC": "spells-scc.json",
        "GGR": "spells-ggr.json",
        "LLK": "spells-llk.json",
    }

    total = 0
    for source in SOURCE_CONFIG.sources:
        if source in spell_files:
            spell_file = DATA_DIR / "spells" / spell_files[source]
            if spell_file.exists():
                count = extractor.extract_file(str(spell_file))
                print(f"  {source}: {count} spells")
                total += count

    if total == 0:
        print("  No spell files found for configured sources")

    # Create index
    extractor.create_index()

    # Store for index generation
    EXTRACTORS['spells'] = extractor
    print(f"  -> {spells_dir.relative_to(REPO_ROOT)}/")


def extract_creatures():
    """Extract creatures to individual files."""
    print("Extracting creatures...")
    creatures_dir = REFERENCE_DIR / "creatures"

    extractor = CreatureExtractor(str(creatures_dir))

    # Map source codes to bestiary files
    bestiary_files = {
        "XMM": "bestiary-xmm.json",
        "MM": "bestiary-mm.json",
        "MPMM": "bestiary-mpmm.json",
        "VGM": "bestiary-vgm.json",
        "MTF": "bestiary-mtf.json",
        "BAM": "bestiary-bam.json",
        "XPHB": "bestiary-xphb.json",
        "XDMG": "bestiary-xdmg.json",
        "FTD": "bestiary-ftd.json",
        "IDRotF": "bestiary-idrotf.json",
        "BGG": "bestiary-bgg.json",
        "GGR": "bestiary-ggr.json",
        "EGW": "bestiary-egw.json",
        "ERLW": "bestiary-erlw.json",
        "MOT": "bestiary-mot.json",
    }

    total = 0
    for source in SOURCE_CONFIG.sources:
        if source in bestiary_files:
            creature_file = DATA_DIR / "bestiary" / bestiary_files[source]
            if creature_file.exists():
                count = extractor.extract_file(str(creature_file))
                print(f"  {source}: {count} creatures")
                total += count

    if total == 0:
        print("  No bestiary files found for configured sources")

    # Create index
    extractor.create_index()
    print(f"  -> {creatures_dir.relative_to(REPO_ROOT)}/")

    # Store for index generation
    EXTRACTORS['creatures'] = extractor


def extract_items():
    """Extract magic items to individual files."""
    print("Extracting magic items...")
    items_dir = REFERENCE_DIR / "items"

    # Use configured sources
    extractor = ItemExtractor(str(items_dir), sources=SOURCE_CONFIG.sources)

    items_file = DATA_DIR / "items.json"
    if items_file.exists():
        count = extractor.extract_file(str(items_file))
        print(f"  Total: {count} magic items")

    # Create index
    extractor.create_index()
    print(f"  -> {items_dir.relative_to(REPO_ROOT)}/")

    # Store for index generation
    EXTRACTORS['items'] = extractor


def extract_feats():
    """Extract feats to individual files."""
    print("Extracting feats...")
    feats_dir = REFERENCE_DIR / "feats"

    extractor = FeatExtractor(str(feats_dir), sources=SOURCE_CONFIG.sources)

    feats_file = DATA_DIR / "feats.json"
    if feats_file.exists():
        count = extractor.extract_file(str(feats_file))
        print(f"  Total: {count} feats")

    # Create index
    extractor.create_index()
    EXTRACTORS['feats'] = extractor
    print(f"  -> {feats_dir.relative_to(REPO_ROOT)}/")


def extract_backgrounds():
    """Extract backgrounds to individual files."""
    print("Extracting backgrounds...")
    bg_dir = REFERENCE_DIR / "backgrounds"

    extractor = BackgroundExtractor(str(bg_dir), sources=SOURCE_CONFIG.sources)

    bg_file = DATA_DIR / "backgrounds.json"
    if bg_file.exists():
        count = extractor.extract_file(str(bg_file))
        print(f"  Total: {count} backgrounds")

    # Create index
    extractor.create_index()
    EXTRACTORS['backgrounds'] = extractor
    print(f"  -> {bg_dir.relative_to(REPO_ROOT)}/")


def extract_species():
    """Extract species/races to individual files."""
    print("Extracting species...")
    species_dir = REFERENCE_DIR / "species"

    extractor = SpeciesExtractor(str(species_dir), sources=SOURCE_CONFIG.sources)

    races_file = DATA_DIR / "races.json"
    if races_file.exists():
        count = extractor.extract_file(str(races_file))
        print(f"  Total: {count} species")

    # Create index
    extractor.create_index()
    EXTRACTORS['species'] = extractor
    print(f"  -> {species_dir.relative_to(REPO_ROOT)}/")


def extract_classes():
    """Extract classes and subclasses to individual files."""
    print("Extracting classes...")
    classes_dir = REFERENCE_DIR / "classes"

    class_dir = DATA_DIR / "class"
    class_files = [
        'class-barbarian.json',
        'class-bard.json',
        'class-cleric.json',
        'class-druid.json',
        'class-fighter.json',
        'class-monk.json',
        'class-paladin.json',
        'class-ranger.json',
        'class-rogue.json',
        'class-sorcerer.json',
        'class-warlock.json',
        'class-wizard.json',
    ]

    # Map sources to their class files
    source_class_files = {
        "XPHB": class_files,
        "PHB": class_files,  # Same files, different source filter
        "EFA": ['class-artificer.json'],
        "TCE": [],  # TCE adds subclasses, not classes
        "XGE": [],  # XGE adds subclasses, not classes
    }

    total = 0
    main_extractor = None

    for source in SOURCE_CONFIG.sources:
        if source not in source_class_files:
            continue

        files = source_class_files[source]
        if not files:
            continue

        extractor = ClassExtractor(str(classes_dir), source=source)

        source_count = 0
        for class_file in files:
            class_path = class_dir / class_file
            if class_path.exists():
                count = extractor.extract_file(str(class_path))
                source_count += count

        if source_count > 0:
            print(f"  {source}: {source_count} classes")
            total += source_count

            if main_extractor is None:
                main_extractor = extractor
            else:
                main_extractor.index_entries.extend(extractor.index_entries)

    if main_extractor is None:
        # No classes extracted, create empty extractor
        main_extractor = ClassExtractor(str(classes_dir), source='XPHB')
        print("  No class files found for configured sources")

    print(f"  Total: {total} classes")

    # Create index
    main_extractor.create_index()
    EXTRACTORS['classes'] = main_extractor
    print(f"  -> {classes_dir.relative_to(REPO_ROOT)}/")


def extract_class_features():
    """Extract class features as individual searchable files."""
    print("Extracting class features...")
    features_dir = REFERENCE_DIR / "class-features"
    features_dir.mkdir(parents=True, exist_ok=True)

    index_entries = []
    class_dir = DATA_DIR / "class"

    class_files = [
        'class-barbarian.json', 'class-bard.json', 'class-cleric.json',
        'class-druid.json', 'class-fighter.json', 'class-monk.json',
        'class-paladin.json', 'class-ranger.json', 'class-rogue.json',
        'class-sorcerer.json', 'class-warlock.json', 'class-wizard.json',
        'class-artificer.json',
    ]

    # Use configured sources
    seen_features = set()

    for class_file in class_files:
        class_path = class_dir / class_file
        if not class_path.exists():
            continue

        with open(class_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        class_features = data.get('classFeature', [])

        for feature in class_features:
            source = feature.get('source', '').upper()
            if not SOURCE_CONFIG.includes(source):
                continue

            name = feature.get('name', '')
            class_name = feature.get('className', '')
            level = feature.get('level', 1)

            # Skip duplicates
            key = f"{name}|{class_name}"
            if key in seen_features:
                continue
            seen_features.add(key)

            # Create feature file
            safe_name = _make_safe_filename(name)
            safe_class = _make_safe_filename(class_name)
            filename = f"{safe_class}-{safe_name}.md"
            feature_path = features_dir / filename

            # Convert entries to markdown
            converter = EntryConverter(heading_level=2)
            entries = feature.get('entries', [])
            content = converter.convert(entries, 0) if entries else ''

            md_content = f"""# {name}

*{class_name} Feature (Level {level})*

**Source:** {source}

---

{content}
"""
            with open(feature_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            index_entries.append({
                'name': name,
                'class': class_name,
                'level': level,
                'path': filename,
            })

    # Create a mock extractor object for the index
    class ClassFeatureExtractor:
        def __init__(self, entries):
            self.index_entries = entries

    EXTRACTORS['class-features'] = ClassFeatureExtractor(index_entries)
    print(f"  Total: {len(index_entries)} class features")
    print(f"  -> {features_dir.relative_to(REPO_ROOT)}/")


def extract_equipment():
    """Extract mundane equipment to individual files."""
    print("Extracting equipment...")
    equip_dir = REFERENCE_DIR / "equipment"

    extractor = EquipmentExtractor(str(equip_dir), sources=SOURCE_CONFIG.sources)

    # Extract base items (weapons, armor) from items-base.json
    base_items_file = DATA_DIR / "items-base.json"
    if base_items_file.exists():
        base_count = extractor.extract_base_items(str(base_items_file))
        print(f"  Base items: {base_count}")

    # Extract other mundane items from items.json
    items_file = DATA_DIR / "items.json"
    if items_file.exists():
        count = extractor.extract_file(str(items_file))
        print(f"  Other items: {count}")

    total = len(extractor.index_entries)
    print(f"  Total: {total} equipment items")

    # Create index
    extractor.create_index()
    print(f"  -> {equip_dir.relative_to(REPO_ROOT)}/")

    # Store for index generation
    EXTRACTORS['equipment'] = extractor


def extract_rules():
    """Extract rules glossary entries to individual files."""
    print("Extracting rules glossary...")
    rules_dir = REFERENCE_DIR / "rules"

    extractor = RulesExtractor(str(rules_dir), sources=SOURCE_CONFIG.sources)

    # Extract conditions and status effects
    conditions_file = DATA_DIR / "conditionsdiseases.json"
    if conditions_file.exists():
        count = extractor.extract_conditions(str(conditions_file))
        print(f"  Conditions/Status: {count}")

    # Extract diseases
    if conditions_file.exists():
        count = extractor.extract_diseases(str(conditions_file))
        print(f"  Diseases: {count}")

    # Extract actions
    actions_file = DATA_DIR / "actions.json"
    if actions_file.exists():
        count = extractor.extract_actions(str(actions_file))
        print(f"  Actions: {count}")

    # Extract senses
    senses_file = DATA_DIR / "senses.json"
    if senses_file.exists():
        count = extractor.extract_senses(str(senses_file))
        print(f"  Senses: {count}")

    # Extract variant rules
    rules_file = DATA_DIR / "variantrules.json"
    if rules_file.exists():
        count = extractor.extract_variant_rules(str(rules_file))
        print(f"  Glossary: {count}")

    # Create index
    extractor.create_index()
    EXTRACTORS['rules'] = extractor
    print(f"  -> {rules_dir.relative_to(REPO_ROOT)}/")


def extract_vehicles():
    """Extract vehicles/ships to individual files."""
    print("Extracting vehicles...")
    vehicles_dir = REFERENCE_DIR / "vehicles"

    extractor = VehicleExtractor(str(vehicles_dir), sources=SOURCE_CONFIG.sources)
    EXTRACTORS['vehicles'] = extractor

    vehicles_file = DATA_DIR / "vehicles.json"
    if vehicles_file.exists():
        count = extractor.extract_file(str(vehicles_file))
        print(f"  Total: {count} vehicles")

    extractor.create_index()
    print(f"  -> {vehicles_dir.relative_to(REPO_ROOT)}/")


def extract_optional_features():
    """Extract optional features (invocations, maneuvers, metamagic)."""
    print("Extracting optional features...")
    features_dir = REFERENCE_DIR / "optional-features"

    extractor = OptionalFeatureExtractor(str(features_dir), sources=SOURCE_CONFIG.sources)
    EXTRACTORS['optional-features'] = extractor

    features_file = DATA_DIR / "optionalfeatures.json"
    if features_file.exists():
        count = extractor.extract_file(str(features_file))
        print(f"  Total: {count} features")

    extractor.create_index()
    print(f"  -> {features_dir.relative_to(REPO_ROOT)}/")


def extract_traps():
    """Extract traps and hazards to individual files."""
    print("Extracting traps and hazards...")
    traps_dir = REFERENCE_DIR / "traps-hazards"

    extractor = TrapExtractor(str(traps_dir), sources=SOURCE_CONFIG.sources)
    EXTRACTORS['traps'] = extractor

    traps_file = DATA_DIR / "trapshazards.json"
    if traps_file.exists():
        counts = extractor.extract_file(str(traps_file))
        print(f"  Traps: {counts['traps']}")
        print(f"  Hazards: {counts['hazards']}")

    extractor.create_index()
    print(f"  -> {traps_dir.relative_to(REPO_ROOT)}/")


def extract_languages():
    """Extract languages to individual files."""
    print("Extracting languages...")
    languages_dir = REFERENCE_DIR / "languages"

    extractor = LanguageExtractor(str(languages_dir))
    EXTRACTORS['languages'] = extractor

    languages_file = DATA_DIR / "languages.json"
    if languages_file.exists():
        count = extractor.extract_file(str(languages_file))
        print(f"  Total: {count} languages")

    extractor.create_index()
    print(f"  -> {languages_dir.relative_to(REPO_ROOT)}/")


def extract_bastions():
    """Extract bastion facilities to individual files."""
    print("Extracting bastion facilities...")
    bastions_dir = REFERENCE_DIR / "bastions"

    extractor = BastionExtractor(str(bastions_dir))
    EXTRACTORS['bastions'] = extractor

    bastions_file = DATA_DIR / "bastions.json"
    if bastions_file.exists():
        count = extractor.extract_file(str(bastions_file))
        print(f"  Total: {count} facilities")

    extractor.create_index()
    print(f"  -> {bastions_dir.relative_to(REPO_ROOT)}/")


def extract_deities():
    """Extract deities to individual files."""
    print("Extracting deities...")
    deities_dir = REFERENCE_DIR / "deities"

    extractor = DeityExtractor(str(deities_dir))
    EXTRACTORS['deities'] = extractor

    deities_file = DATA_DIR / "deities.json"
    if deities_file.exists():
        count = extractor.extract_file(str(deities_file))
        print(f"  Total: {count} deities")

    extractor.create_index()
    print(f"  -> {deities_dir.relative_to(REPO_ROOT)}/")


def extract_rewards():
    """Extract rewards (boons, blessings) to individual files."""
    print("Extracting rewards...")
    rewards_dir = REFERENCE_DIR / "rewards"

    extractor = RewardExtractor(str(rewards_dir))
    EXTRACTORS['rewards'] = extractor

    rewards_file = DATA_DIR / "rewards.json"
    if rewards_file.exists():
        count = extractor.extract_file(str(rewards_file))
        print(f"  Total: {count} rewards")

    extractor.create_index()
    print(f"  -> {rewards_dir.relative_to(REPO_ROOT)}/")


def extract_objects():
    """Extract objects to individual files."""
    print("Extracting objects...")
    objects_dir = REFERENCE_DIR / "objects"

    extractor = ObjectExtractor(str(objects_dir))
    EXTRACTORS['objects'] = extractor

    objects_file = DATA_DIR / "objects.json"
    if objects_file.exists():
        count = extractor.extract_file(str(objects_file))
        print(f"  Total: {count} objects")

    extractor.create_index()
    print(f"  -> {objects_dir.relative_to(REPO_ROOT)}/")


def extract_decks():
    """Extract decks and cards to individual files."""
    print("Extracting decks...")
    decks_dir = REFERENCE_DIR / "decks"

    extractor = DeckExtractor(str(decks_dir))
    EXTRACTORS['decks'] = extractor

    decks_file = DATA_DIR / "decks.json"
    if decks_file.exists():
        count = extractor.extract_file(str(decks_file))
        print(f"  Total: {count} decks")

    extractor.create_index()
    print(f"  -> {decks_dir.relative_to(REPO_ROOT)}/")


def extract_skills():
    """Extract skills to individual files."""
    print("Extracting skills...")
    skills_dir = REFERENCE_DIR / "skills"

    extractor = SkillExtractor(str(skills_dir))
    EXTRACTORS['skills'] = extractor

    skills_file = DATA_DIR / "skills.json"
    if skills_file.exists():
        count = extractor.extract_file(str(skills_file))
        print(f"  Total: {count} skills")

    extractor.create_index()
    print(f"  -> {skills_dir.relative_to(REPO_ROOT)}/")


def extract_item_mastery():
    """Extract weapon mastery properties to individual files."""
    print("Extracting weapon mastery...")
    mastery_dir = REFERENCE_DIR / "mastery"

    extractor = ItemMasteryExtractor(str(mastery_dir))
    EXTRACTORS['mastery'] = extractor

    base_items_file = DATA_DIR / "items-base.json"
    if base_items_file.exists():
        count = extractor.extract_file(str(base_items_file))
        print(f"  Total: {count} mastery properties")

    extractor.create_index()
    print(f"  -> {mastery_dir.relative_to(REPO_ROOT)}/")


def extract_encounters():
    """Extract encounter tables to individual files."""
    print("Extracting encounters...")
    encounters_dir = REFERENCE_DIR / "encounters"

    extractor = EncounterExtractor(str(encounters_dir))
    EXTRACTORS['encounters'] = extractor

    encounters_file = DATA_DIR / "encounters.json"
    if encounters_file.exists():
        count = extractor.extract_file(str(encounters_file))
        print(f"  Total: {count} encounter tables")

    extractor.create_index()
    print(f"  -> {encounters_dir.relative_to(REPO_ROOT)}/")


def extract_loot():
    """Extract loot tables to individual files."""
    print("Extracting loot tables...")
    loot_dir = REFERENCE_DIR / "loot"

    extractor = LootExtractor(str(loot_dir))
    EXTRACTORS['loot'] = extractor

    loot_file = DATA_DIR / "loot.json"
    if loot_file.exists():
        count = extractor.extract_file(str(loot_file))
        print(f"  Total: {count} loot tables")

    extractor.create_index()
    print(f"  -> {loot_dir.relative_to(REPO_ROOT)}/")


def generate_indexes():
    """Generate AI-optimized indexes from collected extractor data."""
    print("Generating AI-optimized indexes...")

    collector = IndexCollector()

    # Collect entries from extractors
    if 'spells' in EXTRACTORS:
        collector.add_entries('spells', EXTRACTORS['spells'].index_entries)
    if 'creatures' in EXTRACTORS:
        collector.add_entries('creatures', EXTRACTORS['creatures'].index_entries)
    if 'items' in EXTRACTORS:
        collector.add_entries('items', EXTRACTORS['items'].index_entries)
    if 'equipment' in EXTRACTORS:
        collector.add_entries('equipment', EXTRACTORS['equipment'].index_entries)

    # Add additional extractors for comprehensive search
    if 'feats' in EXTRACTORS:
        collector.add_entries('feats', EXTRACTORS['feats'].index_entries)
    if 'backgrounds' in EXTRACTORS:
        collector.add_entries('backgrounds', EXTRACTORS['backgrounds'].index_entries)
    if 'species' in EXTRACTORS:
        collector.add_entries('species', EXTRACTORS['species'].index_entries)
    if 'classes' in EXTRACTORS:
        collector.add_entries('classes', EXTRACTORS['classes'].index_entries)
    if 'class-features' in EXTRACTORS:
        collector.add_entries('class-features', EXTRACTORS['class-features'].index_entries)

    # Add rules (flatten the dict structure)
    if 'rules' in EXTRACTORS:
        rules_extractor = EXTRACTORS['rules']
        for category, entries in rules_extractor.index_entries.items():
            collector.add_entries('rules', entries)

    # Add skills
    if 'skills' in EXTRACTORS:
        collector.add_entries('skills', EXTRACTORS['skills'].index_entries)

    # Add species traits for searchability
    if 'species' in EXTRACTORS:
        collector.add_entries('species-traits', EXTRACTORS['species'].trait_entries)

    # Add languages
    if 'languages' in EXTRACTORS:
        collector.add_entries('languages', EXTRACTORS['languages'].index_entries)

    # Add vehicles
    if 'vehicles' in EXTRACTORS:
        collector.add_entries('vehicles', EXTRACTORS['vehicles'].index_entries)

    # Add optional features
    if 'optional-features' in EXTRACTORS:
        collector.add_entries('optional-features', EXTRACTORS['optional-features'].index_entries)

    # Add traps and hazards (flatten the dict structure)
    if 'traps' in EXTRACTORS:
        traps_extractor = EXTRACTORS['traps']
        for category, entries in traps_extractor.index_entries.items():
            collector.add_entries('traps-hazards', entries)

    # Add bastions
    if 'bastions' in EXTRACTORS:
        collector.add_entries('bastions', EXTRACTORS['bastions'].index_entries)

    # Add deities
    if 'deities' in EXTRACTORS:
        collector.add_entries('deities', EXTRACTORS['deities'].index_entries)

    # Add rewards
    if 'rewards' in EXTRACTORS:
        collector.add_entries('rewards', EXTRACTORS['rewards'].index_entries)

    # Add objects
    if 'objects' in EXTRACTORS:
        collector.add_entries('objects', EXTRACTORS['objects'].index_entries)

    # Add decks
    if 'decks' in EXTRACTORS:
        collector.add_entries('decks', EXTRACTORS['decks'].index_entries)

    # Add weapon mastery
    if 'mastery' in EXTRACTORS:
        collector.add_entries('mastery', EXTRACTORS['mastery'].index_entries)

    # Add encounter tables
    if 'encounters' in EXTRACTORS:
        collector.add_entries('encounter-tables', EXTRACTORS['encounters'].index_entries)

    # Add loot tables
    if 'loot' in EXTRACTORS:
        collector.add_entries('loot-tables', EXTRACTORS['loot'].index_entries)

    # Generate master JSON index
    collector.generate_master_json(BOOKS_DIR / "reference-index.json")

    # Generate quick reference files
    collector.generate_quick_references(REFERENCE_DIR)

    # Generate cross-reference tables
    cross_ref_dir = BOOKS_DIR / "cross-references"
    collector.generate_cross_references(cross_ref_dir)

    # Generate keyword index
    collector.generate_keyword_index(BOOKS_DIR / "keyword-index.json")

    print(f"  -> {BOOKS_DIR.relative_to(REPO_ROOT)}/reference-index.json")
    print(f"  -> {BOOKS_DIR.relative_to(REPO_ROOT)}/keyword-index.json")
    print(f"  -> {cross_ref_dir.relative_to(REPO_ROOT)}/")


def main():
    global SOURCE_CONFIG

    print("=" * 60)
    print("D&D Book Extraction for Spelljammer Campaign")
    print("=" * 60)
    print()

    # Load source configuration
    print("Loading source configuration...")
    SOURCE_CONFIG = SourceConfig.load(repo_root=REPO_ROOT)
    print(f"  Sources: {', '.join(SOURCE_CONFIG.sources)}")
    print()

    # Check submodule
    check_submodule()

    # Create books directory
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Extract books (filtered by source config)
    print("Extracting books...")
    print()

    extracted_count = 0
    for extraction in EXTRACTIONS:
        code = extraction.get("code", "")
        if not SOURCE_CONFIG.includes(code):
            continue  # Skip books not in configured sources

        name = extraction["name"]
        source = extraction["source"]
        output = extraction["output"]
        chapters = extraction.get("chapters")  # Optional chapter filter

        print(f"  {name}...")
        if extract_book(name, source, output, chapters=chapters):
            print(f"    -> {output.relative_to(REPO_ROOT)}/")
            extracted_count += 1

    if extracted_count == 0:
        print("  No books matched configured sources")

    print()

    # Extract reference data
    print("Extracting reference data...")
    print()

    extract_spells()
    print()

    extract_creatures()
    print()

    extract_items()
    print()

    extract_feats()
    print()

    extract_backgrounds()
    print()

    extract_species()
    print()

    extract_classes()
    print()

    extract_class_features()
    print()

    extract_equipment()
    print()

    extract_rules()
    print()

    extract_vehicles()
    print()

    extract_optional_features()
    print()

    extract_traps()
    print()

    extract_languages()
    print()

    extract_bastions()
    print()

    extract_deities()
    print()

    extract_rewards()
    print()

    extract_objects()
    print()

    extract_decks()
    print()

    extract_skills()
    print()

    extract_item_mastery()
    print()

    extract_encounters()
    print()

    extract_loot()
    print()

    # Create README
    print("Creating master index...")
    create_readme()

    print()

    # Generate AI-optimized indexes
    generate_indexes()

    print()
    print("=" * 60)
    print("Extraction complete!")
    print(f"Books available in: {BOOKS_DIR.relative_to(REPO_ROOT)}/")
    print(f"Reference data in: {REFERENCE_DIR.relative_to(REPO_ROOT)}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
