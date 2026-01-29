#!/usr/bin/env python3
"""
Extract all D&D books for Spelljammer campaign.

This script extracts content from the 5etools-src submodule and organizes it
into the books/ directory structure. Run this after cloning the repository
to regenerate the extracted content.

Usage:
    python scripts/extract_all.py
"""

import subprocess
import sys
from pathlib import Path

# Add scripts dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from extractors import SpellExtractor, CreatureExtractor, ItemExtractor

# Repository root (parent of scripts/)
REPO_ROOT = Path(__file__).parent.parent
DATA_DIR = REPO_ROOT / "5etools-src" / "data"
BOOKS_DIR = REPO_ROOT / "books"
REFERENCE_DIR = BOOKS_DIR / "reference"
EXTRACT_SCRIPT = REPO_ROOT / "scripts" / "extract_book.py"

# Books to extract
EXTRACTIONS = [
    # Core 2024 Rules
    {
        "name": "Player's Handbook 2024",
        "source": DATA_DIR / "book" / "book-xphb.json",
        "output": BOOKS_DIR / "core" / "xphb",
    },
    {
        "name": "Dungeon Master's Guide 2024",
        "source": DATA_DIR / "book" / "book-xdmg.json",
        "output": BOOKS_DIR / "core" / "xdmg",
    },
    {
        "name": "Monster Manual 2024",
        "source": DATA_DIR / "book" / "book-xmm.json",
        "output": BOOKS_DIR / "core" / "xmm",
    },
    # Spelljammer Setting
    {
        "name": "Astral Adventurer's Guide",
        "source": DATA_DIR / "book" / "book-aag.json",
        "output": BOOKS_DIR / "spelljammer" / "aag",
    },
    {
        "name": "Boo's Astral Menagerie (Book)",
        "source": DATA_DIR / "book" / "book-bam.json",
        "output": BOOKS_DIR / "spelljammer" / "bam",
    },
    {
        "name": "Boo's Astral Menagerie (Creatures)",
        "source": DATA_DIR / "bestiary" / "bestiary-bam.json",
        "output": BOOKS_DIR / "spelljammer" / "bam",
    },
    # Spelljammer Adventures
    {
        "name": "Light of Xaryxis",
        "source": DATA_DIR / "adventure" / "adventure-lox.json",
        "output": BOOKS_DIR / "spelljammer" / "adventures" / "lox",
    },
    {
        "name": "Spelljammer Academy",
        "source": DATA_DIR / "adventure" / "adventure-sja.json",
        "output": BOOKS_DIR / "spelljammer" / "adventures" / "sja",
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

## Campaign Quick Links

### For Players

- **Character Creation**: [XPHB Chapter 2](core/xphb/02-chapter-2-creating-a-character.md)
- **Spelljammer Backgrounds**: [AAG Chapter 1](spelljammer/aag/01-chapter-1-character-options.md)
- **Classes**: [XPHB Chapter 3](core/xphb/03-chapter-3-character-classes.md)
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

Individual entries for cross-referencing. Each spell, creature, and item has its own file.

### Spells

- **[Spell Index](reference/spells/index.md)** - 393 spells organized by level
- Individual spell files in `reference/spells/{level}/`
- Example: [Fireball](reference/spells/3rd-level/fireball.md)

### Creatures

- **[Creature Index](reference/creatures/index.md)** - 575 creatures organized by CR
- Individual creature files in `reference/creatures/`
- Example: [Adult Red Dragon](reference/creatures/adult-red-dragon.md)

### Magic Items

- **[Item Index](reference/items/index.md)** - 1,244 items organized by rarity
- Individual item files in `reference/items/`
- Example: [Bag of Holding](reference/items/bag-of-holding.md)

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


def extract_book(name: str, source: Path, output: Path):
    """Extract a single book using extract_book.py."""
    if not source.exists():
        print(f"  Warning: Source not found: {source}")
        return False

    output.mkdir(parents=True, exist_ok=True)

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

    # Extract from XPHB (2024 PHB)
    xphb_spells = DATA_DIR / "spells" / "spells-xphb.json"
    if xphb_spells.exists():
        count = extractor.extract_file(str(xphb_spells))
        print(f"  XPHB: {count} spells")

    # Extract from AAG (Spelljammer)
    aag_spells = DATA_DIR / "spells" / "spells-aag.json"
    if aag_spells.exists():
        count = extractor.extract_file(str(aag_spells))
        print(f"  AAG: {count} spells")

    # Create index
    extractor.create_index()
    print(f"  -> {spells_dir.relative_to(REPO_ROOT)}/")


def extract_creatures():
    """Extract creatures to individual files."""
    print("Extracting creatures...")
    creatures_dir = REFERENCE_DIR / "creatures"

    extractor = CreatureExtractor(str(creatures_dir))

    # Extract from XMM (2024 Monster Manual)
    xmm_creatures = DATA_DIR / "bestiary" / "bestiary-xmm.json"
    if xmm_creatures.exists():
        count = extractor.extract_file(str(xmm_creatures))
        print(f"  XMM: {count} creatures")

    # Extract from BAM (Boo's Astral Menagerie)
    bam_creatures = DATA_DIR / "bestiary" / "bestiary-bam.json"
    if bam_creatures.exists():
        count = extractor.extract_file(str(bam_creatures))
        print(f"  BAM: {count} creatures")

    # Create index
    extractor.create_index()
    print(f"  -> {creatures_dir.relative_to(REPO_ROOT)}/")


def extract_items():
    """Extract items to individual files."""
    print("Extracting items...")
    items_dir = REFERENCE_DIR / "items"

    # Filter to only our target sources
    sources = ['XDMG', 'XPHB', 'AAG', 'DMG']
    extractor = ItemExtractor(str(items_dir), sources=sources)

    items_file = DATA_DIR / "items.json"
    if items_file.exists():
        count = extractor.extract_file(str(items_file))
        print(f"  Total: {count} items")

    # Create index
    extractor.create_index()
    print(f"  -> {items_dir.relative_to(REPO_ROOT)}/")


def main():
    print("=" * 60)
    print("D&D Book Extraction for Spelljammer Campaign")
    print("=" * 60)
    print()

    # Check submodule
    check_submodule()

    # Create books directory
    BOOKS_DIR.mkdir(parents=True, exist_ok=True)
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Extract all books
    print("Extracting books...")
    print()

    for extraction in EXTRACTIONS:
        name = extraction["name"]
        source = extraction["source"]
        output = extraction["output"]

        print(f"  {name}...")
        if extract_book(name, source, output):
            print(f"    -> {output.relative_to(REPO_ROOT)}/")

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

    # Create README
    print("Creating master index...")
    create_readme()

    print()
    print("=" * 60)
    print("Extraction complete!")
    print(f"Books available in: {BOOKS_DIR.relative_to(REPO_ROOT)}/")
    print(f"Reference data in: {REFERENCE_DIR.relative_to(REPO_ROOT)}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
