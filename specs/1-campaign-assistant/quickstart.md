# Quickstart: Campaign Assistant

**Feature**: Campaign Assistant  
**Date**: 2026-01-28

## Prerequisites

1. **Reference data extracted**: Run `make` to extract 5etools reference data

   ```bash
   make
   ```

   Verify `books/reference-index.json` exists before using campaign features.

2. **Python 3.11+** installed

3. **Dependencies**: The `requests` library (typically pre-installed)

   ```bash
   pip install requests
   ```

## Initialize a Campaign

Create the campaign directory structure:

```bash
python scripts/campaign/init_campaign.py "My Campaign Name"
```

Or manually create the structure:

```
campaign/
├── campaign.md
├── party/
│   ├── index.md
│   └── characters/
├── npcs/
│   └── index.md
├── locations/
│   └── index.md
├── sessions/
│   └── index.md
└── encounters/
    └── index.md
```

## Import a Character from D&D Beyond

1. **Set character to Public** in D&D Beyond:
   - Go to your character on D&D Beyond
   - Click "Manage" → Character Settings
   - Set Privacy to "Public"

2. **Import the character**:

   ```bash
   python scripts/campaign/import_character.py https://www.dndbeyond.com/characters/157884334
   ```

   This creates `campaign/party/characters/character-name.md` with:
   - Full stats and abilities
   - Class features linked to `books/reference/classes/`
   - Spells linked to `books/reference/spells/`
   - Equipment linked to `books/reference/equipment/`

3. **Verify the import** by viewing the generated markdown file.

## Build an Encounter

Generate a balanced encounter for your party:

```bash
# Medium difficulty for a level 3 party of 4
python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium

# Hard encounter with beast creatures only
python scripts/campaign/encounter_builder.py --level 5 --size 4 --difficulty hard --type beast

# Save the encounter
python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium --save "goblin-ambush"
```

Saved encounters appear in `campaign/encounters/` with:
- Creature list with links to stat blocks
- XP breakdown and difficulty calculation
- Party threshold comparison

## Look Up Rules

Ask rules questions with citation support:

```bash
python scripts/campaign/rules_engine.py "What does the Prone condition do?"
```

Response includes:
- Inline-quoted text from the rules
- Source file path for verification

## Record a Session

Create a session summary:

```bash
python scripts/campaign/session_manager.py new "The Goblin Cave"
```

This creates `campaign/sessions/session-001.md` (or next number) with:
- Date and session number
- Title
- Empty summary section to fill in

Edit the file to add your session notes.

## Using with Cursor AI

The campaign data is optimized for Cursor AI assistance:

### Character Lookup
"Look up Meilin's stats" → AI reads `campaign/party/characters/meilin-starwell.md`

### Encounter Building
"Build a hard encounter for the party" → AI uses party index + encounter builder

### Rules Questions
"Can I sneak attack with a hand crossbow?" → AI searches rules and character features

### Session Prep
"What happened in the last session?" → AI reads latest session summary

## Directory Reference

| Path | Purpose |
|------|---------|
| `books/reference/` | Extracted D&D reference data (read-only) |
| `books/reference-index.json` | Name-to-path lookup for all references |
| `campaign/` | Your campaign data (editable) |
| `campaign/party/` | Party members and characters |
| `campaign/npcs/` | Non-player characters |
| `campaign/locations/` | Campaign locations |
| `campaign/sessions/` | Session summaries |
| `campaign/encounters/` | Saved encounters |
| `scripts/campaign/` | Campaign management scripts |

## Troubleshooting

### "Reference data not found"

Run `make` to extract reference data:

```bash
make
```

### "Character not accessible"

Ensure the D&D Beyond character is set to "Public" privacy:
1. Go to your character on D&D Beyond
2. Click the gear icon → Character Settings
3. Set Privacy to "Public"

### "No creatures found for encounter"

Check your filter criteria. Try without filters first:

```bash
python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium
```

### Links not working

Ensure you're viewing markdown in a renderer that supports relative links (Cursor, VS Code preview, etc.).
