# Optional Tools

This document covers four optional campaign tools: the loot generator, session transcription, campaign timeline generator, and NPC relationship graph. Each can be used independently; the Web UI and AI can consume their outputs.

## Loot Generator

Generate D&D 5e treasure using DMG 2024 tables: individual treasure (coins), hoards (coins + gems/art + magic items), or rolls on magic item tables.

### Prerequisites

- Reference data extracted (`make`)
- Python 3.11+

### Commands

**Individual treasure (coins only)** – e.g. for defeated creatures:

```bash
python scripts/campaign/loot_generator.py individual --cr 3
python scripts/campaign/loot_generator.py individual --cr 5 --count 4
```

**Treasure hoard** – full hoard for a CR band:

```bash
python scripts/campaign/loot_generator.py hoard --cr 7
python scripts/campaign/loot_generator.py hoard --cr 15
```

**Magic item tables** – roll on DMG tables A–I:

```bash
python scripts/campaign/loot_generator.py magic-item --table C
python scripts/campaign/loot_generator.py magic-item --table F --count 3
```

**Encounter-based loot** – generate loot from a saved encounter file (by encounter slug):

```bash
# Per-creature individual treasure (default)
python scripts/campaign/loot_generator.py for-encounter "goblin-ambush"

# One hoard for the encounter instead
python scripts/campaign/loot_generator.py for-encounter "goblin-ambush" --hoard
```

Output is printed to stdout. You can paste it into session notes or an encounter file, or ask the AI to run the command and insert the result into a specific file.

---

## Session Transcription

Transcribe session audio (e.g. MP3) using OpenAI Whisper and create a session file plus a raw transcript. Useful for turning recordings into session notes.

### Prerequisites

- **ffmpeg** – required by Whisper (install via system package manager or Homebrew)
- **Python dependencies** – `pip install -r requirements.txt` (includes `openai-whisper`)
- Campaign initialized

### Basic usage

```bash
python scripts/campaign/transcribe_session.py "path/to/recording.mp3" --title "Into the Dragon's Lair"
```

This will:

1. Detect hardware (GPU if available, else CPU) and load the Whisper model
2. Transcribe the audio
3. Save the transcript to `campaign/sessions/transcripts/session-NNN.txt`
4. Create `campaign/sessions/session-NNN.md` with session number and title
5. Update the session index

### Options

- `--title "..."` – Session title (recommended).
- `--model small|medium|large` – Whisper model size (default: auto by hardware; larger = more accurate, slower).
- `--language LANG` – Language code (e.g. `en`); default is auto-detect.

After transcription, edit the session markdown file to turn the transcript into a summary, or keep the transcript for reference and add a short summary at the top.

---

## Campaign Timeline

The **timeline generator** builds a chronological view of campaign events from sessions, NPC first appearances, location discoveries, and optional custom events. The Web UI Timeline page reads this data from the same sources the generator uses.

### Prerequisites

- Campaign initialized
- Sessions, NPCs, and/or locations with in-game dates where desired

### How events get dates

1. **Sessions** – Set `--in-game-date "Day 5"` when creating a session with `session_manager.py new "Title" --in-game-date "Day 5"`. The session file stores this and the generator includes it.
2. **NPCs** – Set `--first-seen "Day 5"` when adding an NPC (or edit the NPC file and add **First Appearance**: Day 5).
3. **Locations** – Set `--discovered "Day 5"` when adding a location (or add **Discovered**: Day 5 in the file).
4. **Custom events** – Create or edit `campaign/events.md` and add events with a date and description (see spec or quickstart for the exact format).

### Generate timeline data

```bash
python scripts/campaign/timeline_generator.py
```

By default this writes to `campaign/timeline.md`. Use `--output filename.md` to write a different filename under `campaign/`. The Web UI’s Timeline page gets event data from the API (sessions, NPCs, locations, events), so the Web UI does not require running the generator; the generator is for producing a standalone markdown timeline you can read or share.

### Viewing the timeline

- **Web UI** – Open the Timeline page to see events in order with links to sessions and entities.
- **Markdown** – If the generator writes `campaign/timeline.md`, open that file for a human-readable list.

---

## NPC Relationship Graph

Track connections between NPCs (ally, enemy, employer, family, etc.) and generate a Mermaid diagram plus a relationship list. The Web UI Relationships page shows this data.

### Prerequisites

- Campaign initialized
- At least two NPCs
- Relationships added via CLI or by editing NPC `## Connections` sections

### Adding relationships

**CLI:**

```bash
# Bidirectional
python scripts/campaign/campaign_manager.py add-relationship "Elara" "Grimbold" --type ally --description "Childhood friends"

# One-way
python scripts/campaign/campaign_manager.py add-relationship "Spy" "Target" --type enemy --one-way
```

**Manual:** Edit an NPC’s markdown file and add a `## Connections` section:

```markdown
## Connections

- [Grimbold the Blacksmith](grimbold-the-blacksmith.md) | ally | Childhood friend
- [Mayor Thorne](mayor-thorne.md) | employer | Works as enforcer
```

Format: `- [Display Name](filename.md) | type | description`

### Relationship types

Common types (with inverse where applicable): ally, enemy, family, employer, employee, rival, neutral, romantic, mentor, student.

### Generate the graph

```bash
python scripts/campaign/relationship_graph.py
```

This creates or updates `campaign/relationships.md` with:

- A Mermaid flowchart of NPCs and their connections
- A list of relationships by NPC with links to NPC files

The Web UI’s Relationships page reads NPC and relationship data from the campaign API (same data the graph is built from), so after you add or edit relationships and regenerate, refresh the Web UI to see the updated diagram and lists.

---

## Summary

| Tool | Main command | Output / use |
| ---- | ------------- | ------------ |
| **Loot generator** | `loot_generator.py individual \| hoard \| magic-item \| for-encounter ...` | Printed treasure; paste into notes or encounters |
| **Session transcription** | `transcribe_session.py "audio.mp3" --title "Session 5"` | Session file + transcript in `sessions/` and `sessions/transcripts/` |
| **Timeline generator** | `timeline_generator.py` | Optional `campaign/timeline.md`; Web UI timeline uses API from sessions/NPCs/locations/events |
| **Relationship graph** | `relationship_graph.py` | `campaign/relationships.md` (Mermaid + list); Web UI reads same data via API |

For full CLI options, run each script with `--help` or see [CLI Reference](08-cli-reference.md).
