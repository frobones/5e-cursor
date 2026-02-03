# 5e-cursor

**AI-first D&D 5e campaign management for [Cursor](https://cursor.com).**

Import characters from D&D Beyond, build balanced encounters, look up rules with citations, track sessions, and generate rich NPCs and locations—all through natural language conversation with your AI assistant. Extracts and indexes 5etools content for efficient AI context.

## No Coding Required

[Cursor](https://cursor.com) is a free code editor with built-in AI that can read your files and run commands for you. You don't need to be a developer to use this project—once set up, you just chat with the AI in plain English to manage your campaign. The AI handles all the technical details behind the scenes.

New to the project? Start with the [Introduction](docs/01-introduction.md) for a friendly overview. For thorough usage instructions, see the [User Guide](docs/00-guide.md) (getting started, campaign setup, AI workflows, Web UI, CLI reference, and optional tools).

## Quick Start

1. **Clone the repository** - In Cursor, click the **Clone Repository** button and paste:

   ```text
   https://github.com/frobones/5e-cursor.git
   ```

2. **Run setup** - Open the terminal (`` Ctrl+` ``) and run:

   ```bash
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
├── books/                    # Extracted reference content (gitignored)
│   ├── core/                 # Core rulebooks (XPHB, XDMG, XMM)
│   ├── reference/            # Individual entries (spells, creatures, etc.)
│   ├── cross-references/     # Grouped tables (by CR, spell level, etc.)
│   ├── reference-index.json  # Master name-to-path index
│   └── keyword-index.json    # Semantic keyword lookups
├── campaign/                 # Your campaign data (gitignored)
│   ├── party/characters/     # Imported character sheets
│   ├── npcs/                 # Campaign NPCs
│   ├── locations/            # Campaign locations
│   ├── sessions/             # Session summaries
│   └── encounters/           # Saved encounters
├── frontend/                 # Campaign Web UI (React + Vite)
│   ├── src/
│   │   ├── pages/            # Dashboard, NPCs, Sessions, etc.
│   │   ├── components/       # Layout, markdown viewer, search
│   │   └── services/         # API client
│   └── package.json
├── scripts/
│   ├── extract_all.py        # Reference data extraction
│   ├── extractors/           # Category extractors
│   ├── campaign/             # Campaign management tools
│   │   ├── import_character.py
│   │   ├── encounter_builder.py
│   │   ├── rules_engine.py
│   │   ├── session_manager.py
│   │   ├── campaign_manager.py
│   │   ├── loot_generator.py
│   │   ├── transcribe_session.py
│   │   ├── timeline_generator.py
│   │   └── relationship_graph.py
│   ├── web/                  # Web UI backend (FastAPI)
│   │   ├── main.py           # API server entry point
│   │   ├── api/              # Route handlers
│   │   ├── services/         # Campaign & reference data access
│   │   └── models/           # Pydantic request/response models
│   └── lib/                  # Shared utilities
├── .cursor/rules/            # Cursor AI rules
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
| `make web-ui` | Start Web UI (frontend + backend) |
| `make web-ui-stop` | Stop Web UI servers |
| `make demo-campaign` | Extract demo campaign for testing |
| `make demo-campaign-clean` | Remove demo campaign |
| `make help` | Show available commands |

## Cursor Integration

The `.cursor/rules/dnd-reference-lookup.mdc` rule guides Cursor on how to efficiently look up D&D reference data. The 5etools-src submodule is excluded via `.cursorignore` to keep AI context focused on the extracted markdown.

## Campaign Assistant

This project is designed for **AI-first D&D campaign management**. Instead of learning commands or navigating menus, you just talk to Cursor AI in natural language. The AI has access to all your reference data, campaign files, and tools—so it can answer rules questions, build encounters, track your world, and keep everything organized for you.

### Just Ask

Instead of running commands, simply tell the AI what you need:

| You Say | The AI Does |
| ------- | ----------- |
| *"Import my character from D&D Beyond: [url]"* | Fetches character, creates linked markdown sheet |
| *"Update all my characters from D&D Beyond"* | Refreshes character data from D&D Beyond |
| *"Build a hard encounter for my party"* | Reads party level/size, generates balanced encounter |
| *"How does the prone condition work?"* | Looks up rules with inline citations |
| *"Create a new session called 'Into the Underdark'"* | Creates session file, updates session log |
| *"Add an NPC named Vex, she's a tavern owner ally"* | Creates NPC file, updates NPC index |
| *"What spells does Meilin have prepared?"* | Reads character sheet, lists spells |
| *"What happened in session 3?"* | Reads session summary |
| *"Create a blacksmith NPC for the market district"* | Generates rich NPC with description, personality, secrets |
| *"Add a hidden temple in the forest"* | Creates location with sensory details, encounters, hooks |

The AI uses the extracted reference data and campaign tools automatically—you don't need to know the underlying commands.

### AI-Assisted NPC & Location Generation

Just describe what you need, and the AI expands it into campaign-consistent content:

**NPCs** get: physical description, personality traits, voice/mannerisms, connections to existing NPCs, secrets, and combat stats.

**Locations** get: sensory details (sights, sounds, smells), notable features, key NPCs, connections to nearby places, potential encounters, and hidden secrets.

The AI checks for name conflicts, maintains setting consistency, and connects new entities to your existing campaign elements.

### Your World, Remembered

Your campaign lives in organized markdown files—party roster, NPCs, locations, session summaries, and encounters. The AI can read all of it, so it understands your world's context and history.

**Session tracking** lets you record what happened each session. Later you can ask *"What happened in session 3?"* or *"When did we last see Captain Vex?"* and get answers based on your actual session notes.

**World awareness** means the AI maintains knowledge of your party composition, NPC relationships, location connections, and campaign history. When you ask for a new encounter or NPC, suggestions stay consistent with your established world—no more generic content that ignores your setting.

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
| **Character Update** | Refresh imported characters from D&D Beyond (single or batch) |
| **Encounter Building** | Generate balanced encounters using DMG XP thresholds |
| **Rules Arbitration** | Answer rules questions with inline quotes and source citations |
| **Session Tracking** | Create and review session summaries |
| **Campaign State** | Manage NPCs, locations, and campaign notes |
| **AI-Assisted Generation** | Create rich NPCs and locations from partial descriptions |
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
# Campaign initialization
python scripts/campaign/init_campaign.py "Campaign Name"

# Character management
python scripts/campaign/import_character.py import <url>      # Import from D&D Beyond
python scripts/campaign/import_character.py list              # List all characters
python scripts/campaign/import_character.py update "Name"     # Update one character
python scripts/campaign/import_character.py update --all      # Update all characters

# Encounter builder
python scripts/campaign/encounter_builder.py --auto --difficulty hard
python scripts/campaign/encounter_builder.py --level 5 --size 4 --type undead

# Rules lookup
python scripts/campaign/rules_engine.py "prone condition"     # Natural language query
python scripts/campaign/rules_engine.py --spell "fireball"    # Direct spell lookup
python scripts/campaign/rules_engine.py --condition "stunned" # Direct condition lookup

# Session management
python scripts/campaign/session_manager.py new "Session Title"
python scripts/campaign/session_manager.py list
python scripts/campaign/session_manager.py show 3

# NPC and location management
python scripts/campaign/campaign_manager.py add-npc "Name" --role ally
python scripts/campaign/campaign_manager.py add-location "Place" --type tavern
python scripts/campaign/campaign_manager.py list-npcs
python scripts/campaign/campaign_manager.py list-locations

# AI support (context gathering)
python scripts/campaign/campaign_manager.py context           # Campaign summary
python scripts/campaign/campaign_manager.py check-name "Name" # Validate availability
```

## Web UI

Browse your campaign in a modern web interface with all your data at your fingertips.

### Starting the Web UI

```bash
# Terminal 1: Start the backend API
cd scripts && python -m web.main

# Terminal 2: Start the frontend dev server
cd frontend && npm run dev
```

Then open http://localhost:5173 in your browser.

### Features

| Feature | Description |
| ------- | ----------- |
| **Dashboard** | Campaign overview with stats, recent sessions, and quick links |
| **NPC Browser** | Browse all NPCs with role filtering and relationship connections |
| **Location Browser** | Explore campaign locations with descriptions and notable features |
| **Session History** | Review all sessions with full markdown rendering |
| **Party Tracker** | View party composition and individual character sheets |
| **Encounter Library** | Saved encounters with difficulty ratings and creature lists |
| **Encounter Builder** | Build balanced encounters with real-time difficulty calculation |
| **Combat Tracker** | Run encounters with initiative, HP, conditions, and stat lookups |
| **Campaign Timeline** | Chronological view of all events, NPC appearances, and discoveries |
| **Relationship Graph** | Interactive Mermaid diagram showing NPC connections |
| **Reference Browser** | Search spells, creatures, items with level/CR/rarity filters |
| **Global Search** | Press Cmd+K to search across all campaign content |
| **Live Reload** | Auto-refreshes when campaign files change |

### Development

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# Run linting
cd frontend && npm run lint

# Build for production
cd frontend && npm run build
```

## License

Extraction scripts are provided as-is. D&D content is property of Wizards of the Coast and is not redistributed in this repository. Run `make` to generate content locally from the 5etools submodule.
