# 5e-cursor

D&D 5e reference data optimized for [Cursor AI](https://cursor.com). Extracts and indexes content from 5etools for efficient AI-assisted D&D gameplay.

## Quick Start

```bash
git clone https://github.com/frobones/5e-cursor.git
cd 5e-cursor
make
```

That's it. `make` initializes the submodule and extracts all reference data.

## What It Does

Extracts D&D 5e (2024) content from the 5etools data repository and converts it to:

- **Markdown files** - Human-readable reference documents
- **JSON indexes** - Fast lookups for AI context
- **Quick reference tables** - Compact stat summaries
- **Cross-reference files** - Grouped lookups (by CR, rarity, spell level, etc.)

## Source Books

| Book | Code | Type |
| ---- | ---- | ---- |
| Player's Handbook (2024) | XPHB | Core Rules |
| Dungeon Master's Guide (2024) | XDMG | Core Rules |
| Monster Manual (2024) | XMM | Core Rules |
| Astral Adventurer's Guide | AAG | Spelljammer |
| Boo's Astral Menagerie | BAM | Spelljammer |
| Light of Xaryxis | LoX | Adventure |
| Spelljammer Academy | SJA | Adventure |
| Eberron: Forge of the Artificer | EFA | Supplement (Artificer only) |

### Customizing Sources

By default, extraction includes **2024 Core + Spelljammer + Artificer**:
- XPHB, XDMG, XMM (2024 rules)
- AAG, BAM, LoX, SJA (Spelljammer)
- EFA (Artificer class only)

To customize:

**Option 1: Config file** - Copy `sources.yaml.example` to `sources.yaml`:

```yaml
# Use a preset
preset: 2024-core

# Or list specific sources
sources:
  - XPHB
  - XDMG
  - XMM
```

**Option 2: Command line override** (for one-off extractions):

```bash
make extract SOURCES="XPHB,XMM"
```

See `sources.yaml.example` for all available presets and source codes.

## Extracted Reference Data

| Category | Count | Path |
| -------- | ----- | ---- |
| Spells | 393 | `books/reference/spells/` |
| Creatures | 592 | `books/reference/creatures/` |
| Magic Items | 1,250 | `books/reference/items/` |
| Equipment | 264 | `books/reference/equipment/` |
| Classes | 13 + 53 subclasses | `books/reference/classes/` |
| Species | 21 | `books/reference/species/` |
| Feats | 77 | `books/reference/feats/` |
| Backgrounds | 18 | `books/reference/backgrounds/` |
| Rules/Conditions | 161 | `books/reference/rules/` |

See `books/README.md` for the complete list after extraction.

## AI-Optimized Indexes

| File | Purpose |
| ---- | ------- |
| `books/reference-index.json` | Master index (2,499 entries) |
| `books/keyword-index.json` | Semantic lookups (damage types, creature types, schools) |
| `books/cross-references/` | Grouped tables (creatures by CR, spells by level, etc.) |
| `books/reference/*/quick-reference.md` | Compact stat tables |

## Project Structure

```text
5e-cursor/
├── 5etools-src/              # Git submodule (5etools data)
├── books/                    # Extracted content (gitignored)
│   ├── core/                 # Core rulebooks
│   ├── spelljammer/          # Setting & adventures
│   ├── eberron/              # EFA (Artificer)
│   ├── reference/            # Individual entries
│   ├── cross-references/     # Grouped tables
│   ├── reference-index.json  # Master index
│   └── keyword-index.json    # Keyword lookups
├── scripts/
│   ├── extract_all.py        # Main extraction script
│   ├── extract_book.py       # Book extraction library
│   └── extractors/           # Category extractors
├── .cursor/rules/            # Cursor AI rules
├── .cursorignore             # Excludes 5etools-src from Cursor
├── Makefile                  # Build commands
└── README.md
```

## Makefile Commands

| Command | Description |
| ------- | ----------- |
| `make` | Initialize submodule and extract (default) |
| `make extract` | Run extraction only |
| `make submodule` | Initialize/update submodule only |
| `make clean` | Remove extracted books/ |
| `make help` | Show available commands |

## Cursor Integration

The `.cursor/rules/dnd-reference-lookup.mdc` rule guides Cursor on how to efficiently look up D&D reference data. The 5etools-src submodule is excluded via `.cursorignore` to keep AI context focused on the extracted markdown.

## Campaign Assistant

This project is designed for **AI-first D&D campaign management**. Just talk to Cursor AI in natural language—it has access to all reference data and campaign tools.

### Just Ask

Instead of running commands, simply tell the AI what you need:

| You Say | The AI Does |
| ------- | ----------- |
| *"Import my character from D&D Beyond: [url]"* | Fetches character, creates linked markdown sheet |
| *"Build a hard encounter for my party"* | Reads party level/size, generates balanced encounter |
| *"How does the prone condition work?"* | Looks up rules with inline citations |
| *"Create a new session called 'Into the Underdark'"* | Creates session file, updates session log |
| *"Add an NPC named Vex, she's a tavern owner ally"* | Creates NPC file, updates NPC index |
| *"What spells does Meilin have prepared?"* | Reads character sheet, lists spells |
| *"What happened in session 3?"* | Reads session summary |

The AI uses the extracted reference data and campaign tools automatically—you don't need to know the underlying commands.

After running `make` (which handles all setup), initialize your campaign:

```bash
python scripts/campaign/init_campaign.py "Spelljammer Adventures"
```

Or just ask the AI: *"Initialize a campaign called Spelljammer Adventures"*

### How It Works

1. **Reference Data** (`books/`) - Extracted D&D 5e content the AI can search and cite
2. **Campaign Data** (`campaign/`) - Your party, NPCs, locations, sessions in markdown
3. **Cursor Rules** (`.cursor/rules/`) - Guide the AI on how to use the data efficiently
4. **Campaign Tools** (`scripts/campaign/`) - Python scripts the AI invokes when needed

### What the AI Can Do

| Capability | Description |
| ---------- | ----------- |
| **Character Import** | Pull full character sheets from D&D Beyond with auto-linked features |
| **Encounter Building** | Generate balanced encounters using DMG XP thresholds |
| **Rules Arbitration** | Answer rules questions with inline quotes and source citations |
| **Session Tracking** | Create and review session summaries |
| **Campaign State** | Manage NPCs, locations, and campaign notes |
| **Reference Lookup** | Find spells, creatures, items, feats, conditions instantly |

### Campaign Data Structure

```text
campaign/
├── campaign.md            # Campaign overview
├── party/
│   ├── index.md           # Party roster
│   └── characters/        # Imported character sheets
├── npcs/
│   ├── index.md           # NPC index by role
│   └── *.md               # Individual NPCs
├── locations/
│   ├── index.md           # Location index
│   └── *.md               # Individual locations
├── sessions/
│   ├── index.md           # Session log
│   └── session-*.md       # Session summaries
└── encounters/
    ├── index.md           # Saved encounters
    └── *.md               # Individual encounters
```

### CLI Reference (Optional)

The AI uses these tools automatically, but you can also run them directly:

```bash
# Character import
python scripts/campaign/import_character.py <dndbeyond-url>

# Encounter builder
python scripts/campaign/encounter_builder.py --auto --difficulty hard

# Rules lookup
python scripts/campaign/rules_engine.py --spell "fireball"

# Session management
python scripts/campaign/session_manager.py new "Session Title"

# Campaign management
python scripts/campaign/campaign_manager.py add-npc "Name" --role ally
```

## License

Extraction scripts are provided as-is. D&D content is property of Wizards of the Coast and is not redistributed in this repository. Run `make` to generate content locally from the 5etools submodule.
