# Campaign Management

This document covers managing party members, NPCs, locations, sessions, and encounters—both via the AI (natural language) and via the CLI. For a quick list of all commands, see [CLI Reference](08-cli-reference.md).

## Party and Characters

### Import from D&D Beyond

Characters must be set to **Public** in D&D Beyond for the import to work.

```bash
# Import one character by URL
python scripts/campaign/import_character.py import "https://www.dndbeyond.com/characters/12345"

# List imported characters
python scripts/campaign/import_character.py list

# Update one character by name
python scripts/campaign/import_character.py update "Meilin Starwell"

# Update all imported characters
python scripts/campaign/import_character.py update --all
```

Import creates a markdown file in `campaign/party/characters/` with the character’s stats, features, spells, and equipment. Features and spells are linked to reference markdown when possible (using the project’s reference index). The party index (`campaign/party/index.md`) is updated automatically.

### Character File Structure

Each character file includes:

- Name, class, level, race, background
- Ability scores and modifiers
- HP, AC, proficiencies
- Features and traits (with links to reference where applicable)
- Spells (prepared/known) with reference links
- Equipment with reference links where possible

You can edit these markdown files by hand; the AI and Web UI will read the updated content. Re-running `import_character.py update` will overwrite with fresh D&D Beyond data.

## NPCs

### Add an NPC (CLI)

```bash
# Basic: name and role (ally | neutral | enemy)
python scripts/campaign/campaign_manager.py add-npc "Vex" --role ally

# With first appearance (for timeline)
python scripts/campaign/campaign_manager.py add-npc "Grimbold" --role neutral --first-seen "Day 5"
```

This creates `campaign/npcs/<slug>.md` and updates `campaign/npcs/index.md`. The file has placeholders for description, connections, and notes. You or the AI can fill these in.

### Edit NPCs

- Edit the markdown file directly, or ask the AI to add description, personality, connections, or secrets.
- **Connections** use the format: `- [Other NPC Name](other-npc-slug.md) | type | description`. See [Optional Tools – Relationship Graph](09-optional-tools.md#npc-relationship-graph) for relationship types and the graph generator.

### List NPCs

```bash
python scripts/campaign/campaign_manager.py list-npcs
```

The Web UI also lists all NPCs with role filters and links to the relationship graph.

## Locations

### Add a Location (CLI)

```bash
# Basic: name and type (e.g. tavern, dungeon, city)
python scripts/campaign/campaign_manager.py add-location "The Rusty Dragon" --type tavern

# With discovery date (for timeline)
python scripts/campaign/campaign_manager.py add-location "Goblin Caves" --type dungeon --discovered "Day 5"

# With region
python scripts/campaign/campaign_manager.py add-location "Market Square" --type district --region "Port Nyanzaru"
```

This creates `campaign/locations/<slug>.md` and updates the location index. Add description, notable features, and connections to NPCs or other locations by editing the file or asking the AI.

### List Locations

```bash
python scripts/campaign/campaign_manager.py list-locations
```

## Sessions

### Create a Session

```bash
# Basic
python scripts/campaign/session_manager.py new "Into the Caves"

# With in-game date (for timeline)
python scripts/campaign/session_manager.py new "Into the Caves" --in-game-date "Day 5"
```

This creates `campaign/sessions/session-NNN.md` and updates the session index. The file includes session number, title, date, and optional in-game date. Fill in the summary yourself or use the [session transcription](09-optional-tools.md#session-transcription) tool to generate a draft from audio.

### List and Show Sessions

```bash
python scripts/campaign/session_manager.py list
python scripts/campaign/session_manager.py show 3
```

The Web UI shows all sessions with full markdown rendering and links to timeline events.

## Encounters

### Build an Encounter (CLI)

The encounter builder reads party level and size from your campaign (or you can override).

```bash
# Auto: use party from campaign, target difficulty
python scripts/campaign/encounter_builder.py --auto --difficulty hard

# Manual: level, party size, difficulty
python scripts/campaign/encounter_builder.py --level 5 --size 4 --difficulty medium

# Restrict by creature type (e.g. undead)
python scripts/campaign/encounter_builder.py --auto --difficulty medium --type undead
```

By default the builder prints the encounter to stdout. To save it:

```bash
python scripts/campaign/encounter_builder.py --auto --difficulty hard --output campaign/encounters/asteroid-ambush.md
```

Or ask the AI to “build a hard encounter and save it as asteroid-ambush”; it will run the builder and write the file, then update the encounter index.

### Encounter File Contents

Saved encounters include:

- Difficulty (target and actual), party level/size, total XP
- List of creatures with counts, CR, and XP
- Stat block summaries or references
- Optional tactical notes

You can edit the markdown afterward; the Web UI and AI will use the updated file.

## Campaign Context (for AI)

These commands are intended for AI or scripting use:

```bash
# Print a campaign summary (names, counts, recent sessions)
python scripts/campaign/campaign_manager.py context

# Check if a name is already used (NPC/location)
python scripts/campaign/campaign_manager.py check-name "Vex"
```

## Relationships Between NPCs

To add a relationship between two NPCs (for the relationship graph and Web UI):

```bash
# Bidirectional
python scripts/campaign/campaign_manager.py add-relationship "Elara" "Grimbold" --type ally --description "Childhood friends"

# One-way only
python scripts/campaign/campaign_manager.py add-relationship "Spy" "Target" --type enemy --one-way
```

Relationship types include: ally, enemy, family, employer, employee, rival, neutral, romantic, mentor, student. See [Optional Tools – Relationship Graph](09-optional-tools.md#npc-relationship-graph) for generating the graph and viewing it in the Web UI.

## Summary Table

| Task | CLI (example) | AI (example) |
| -----|---------------|--------------|
| Import character | `import_character.py import <url>` | "Import my character from D&D Beyond: [url]" |
| Add NPC | `campaign_manager.py add-npc "Name" --role ally` | "Add an NPC named Vex, tavern owner, ally" |
| Add location | `campaign_manager.py add-location "Place" --type tavern` | "Add a tavern called The Rusty Dragon" |
| New session | `session_manager.py new "Title"` | "Create a session called Into the Caves" |
| Build encounter | `encounter_builder.py --auto --difficulty hard` | "Build a hard encounter for my party" |
| Rules lookup | `rules_engine.py "prone condition"` | "How does the prone condition work?" |

For full CLI options, see [CLI Reference](08-cli-reference.md).
