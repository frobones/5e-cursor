# CLI Reference

This document lists all campaign and reference-related commands. Run from the repository root with your virtual environment activated. For workflows and context, see [Campaign Management](05-campaign-management.md) and [Using the AI](04-using-the-ai.md).

## Campaign Initialization

```bash
python scripts/campaign/init_campaign.py "Campaign Name"
```

Creates `campaign/` and all subdirectories, `campaign.md`, and index files. See [Campaign Setup](03-campaign-setup.md).

---

## Character Management (import_character.py)

| Command | Description |
| ------- | ----------- |
| `import <url>` | Import a character from a D&D Beyond character sheet URL. Character must be Public. |
| `list` | List all imported characters (names and file paths). |
| `update "Name"` | Refresh one character’s data from D&D Beyond by name. |
| `update --all` | Refresh all imported characters. |

**Examples:**

```bash
python scripts/campaign/import_character.py import "https://www.dndbeyond.com/characters/12345"
python scripts/campaign/import_character.py list
python scripts/campaign/import_character.py update "Meilin Starwell"
python scripts/campaign/import_character.py update --all
```

---

## Encounter Builder (encounter_builder.py)

| Option | Description |
| ------ | ----------- |
| `--auto` | Use party level and size from campaign data. |
| `--level N` | Party level (when not using `--auto`). |
| `--size N` | Party size (when not using `--auto`). |
| `--difficulty easy \| medium \| hard \| deadly` | Target difficulty. |
| `--type TYPE` | Restrict creatures by type (e.g. undead, beast). |
| `--output PATH` | Write encounter to a markdown file (e.g. `campaign/encounters/name.md`). |

**Examples:**

```bash
python scripts/campaign/encounter_builder.py --auto --difficulty hard
python scripts/campaign/encounter_builder.py --level 5 --size 4 --difficulty medium
python scripts/campaign/encounter_builder.py --auto --difficulty hard --type undead
python scripts/campaign/encounter_builder.py --auto --difficulty medium --output campaign/encounters/goblin-ambush.md
```

---

## Rules Lookup (rules_engine.py)

| Usage | Description |
| ----- | ----------- |
| `"query"` | Natural language query (e.g. "prone condition", "fireball range"). |
| `--spell "name"` | Direct spell lookup. |
| `--condition "name"` | Direct condition lookup. |
| `--creature "name"` | Creature lookup. |
| `--item "name"` | Item lookup. |

**Examples:**

```bash
python scripts/campaign/rules_engine.py "prone condition"
python scripts/campaign/rules_engine.py --spell "fireball"
python scripts/campaign/rules_engine.py --condition "stunned"
```

---

## Session Management (session_manager.py)

| Command | Description |
| ------- | ----------- |
| `new "Title"` | Create a new session file and update the session index. |
| `list` | List all sessions (number, title, date). |
| `show N` | Print the content of session N. |

**Options for `new`:**

| Option | Description |
| ------ | ----------- |
| `--in-game-date "..."` | In-game date string (e.g. "Day 5") for timeline. |

**Examples:**

```bash
python scripts/campaign/session_manager.py new "Into the Caves"
python scripts/campaign/session_manager.py new "Into the Caves" --in-game-date "Day 5"
python scripts/campaign/session_manager.py list
python scripts/campaign/session_manager.py show 3
```

---

## NPC and Location Management (campaign_manager.py)

### NPCs

| Command | Description |
| ------- | ----------- |
| `add-npc "Name"` | Create an NPC. Default role is neutral. |
| `list-npcs` | List all NPCs. |
| `show-npc "Name"` | Print one NPC’s file content. |

**Options for `add-npc`:** `--role` (ally \| neutral \| enemy), `--description`, `--occupation`, `--location`, `--personality`, `--voice`, `--secrets`, `--combat`, `--notes`, `--first-seen "..."` (for timeline).

### Locations

| Command | Description |
| ------- | ----------- |
| `add-location "Name"` | Create a location. |
| `list-locations` | List all locations. |
| `show-location "Name"` | Print one location’s file content. |

**Options for `add-location`:** `--type` (tavern, dungeon, city, etc.), `--description`, `--region`, `--discovered "..."` (for timeline), `--sights`, `--sounds`, `--smells`, `--encounters`, `--secrets`, `--notes`.

### Relationships

| Command | Description |
| ------- | ----------- |
| `add-relationship "SourceNPC" "TargetNPC"` | Add a relationship between two NPCs. |

**Options:** `--type` (ally, enemy, family, employer, employee, rival, neutral, romantic, mentor, student), `--description "..."`, `--one-way` (do not add inverse link).

### AI / Context

| Command | Description |
| ------- | ----------- |
| `context` | Print a campaign summary (counts, recent sessions, etc.) for AI context. |
| `check-name "Name"` | Check if a name is already used (NPC or location). Optional: `--allow-npc`, `--allow-location`. |

**Examples:**

```bash
python scripts/campaign/campaign_manager.py add-npc "Vex" --role ally
python scripts/campaign/campaign_manager.py add-npc "Grimbold" --role neutral --first-seen "Day 5"
python scripts/campaign/campaign_manager.py add-location "The Rusty Dragon" --type tavern
python scripts/campaign/campaign_manager.py add-location "Goblin Caves" --type dungeon --discovered "Day 5"
python scripts/campaign/campaign_manager.py add-relationship "Elara" "Grimbold" --type ally --description "Childhood friends"
python scripts/campaign/campaign_manager.py list-npcs
python scripts/campaign/campaign_manager.py list-locations
python scripts/campaign/campaign_manager.py context
python scripts/campaign/campaign_manager.py check-name "Vex"
```

---

## Optional Tools

These scripts are documented in detail in [Optional Tools](09-optional-tools.md). Summary:

| Script | Purpose |
| ------ | ------- |
| **loot_generator.py** | Generate treasure (individual, hoard, magic items) by CR or from an encounter. |
| **transcribe_session.py** | Transcribe session audio (e.g. MP3) with Whisper and create a session file + transcript. |
| **timeline_generator.py** | Generate `campaign/relationships.md` (timeline data) from sessions, NPCs, locations, and `events.md`. |
| **relationship_graph.py** | Generate `campaign/relationships.md` (Mermaid diagram + relationship list) from NPC connections. |

**Quick examples:**

```bash
python scripts/campaign/loot_generator.py hoard --cr 7
python scripts/campaign/transcribe_session.py "recording.mp3" --title "Session 5"
python scripts/campaign/timeline_generator.py
python scripts/campaign/relationship_graph.py
```

---

## Extraction (Makefile)

| Command | Description |
| ------- | ----------- |
| `make` | Initialize submodule (if needed) and run full extraction. |
| `make extract` | Run extraction only (assumes submodule is present). |
| `make clean` | Remove `books/` directory. |
| `make submodule` | Initialize/update submodule only. |
| `make help` | List make targets. |

Source selection: use `sources.yaml` (copy from `sources.yaml.example`) or:

```bash
make extract SOURCES="XPHB,XDMG,XMM"
```

See [Reference Data](07-reference-data.md) and the main [README](../README.md).
