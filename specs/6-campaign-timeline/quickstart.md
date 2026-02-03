# Quickstart: Campaign Timeline

Track the passage of in-game time and generate a chronological timeline of your campaign.

## Prerequisites

- Campaign initialized (`python scripts/campaign/init_campaign.py "Campaign Name"`)
- Python 3.11+

## Basic Usage

### 1. Add In-Game Dates to Sessions

When creating sessions, add the in-game date:

```bash
python scripts/campaign/session_manager.py new "Into the Caves" --in-game-date "Day 5"
```

This creates a session file with:

```markdown
**Date**: 2026-02-02  
**In-Game Date**: Day 5  
**Session Number**: 3
```

### 2. Track NPC First Appearances

When adding NPCs, record when they first appear:

```bash
python scripts/campaign/campaign_manager.py add-npc "Grimbold the Blacksmith" --role neutral --first-seen "Day 5"
```

This adds to the NPC file:

```markdown
**Role**: Neutral  
**First Appearance**: Day 5  
```

### 3. Track Location Discoveries

When adding locations, record when the party discovers them:

```bash
python scripts/campaign/campaign_manager.py add-location "Goblin Caves" --type dungeon --discovered "Day 5"
```

This adds to the location file:

```markdown
**Type**: Dungeon  
**Discovered**: Day 5  
```

### 4. Add Custom Events

Edit `campaign/events.md` to add major campaign events:

```markdown
| In-Game Date | Event | Session | Category |
| ------------ | ----- | ------- | -------- |
| Day 1 | Campaign begins | 1 | start |
| Day 5 | Defeated goblin chief | 2 | battle |
| Day 10 | Found the ancient artifact | 3 | discovery |
```

**Categories**:
- `start` - Campaign or arc beginning
- `battle` - Major combat
- `plot` - Story development
- `discovery` - Important find
- `custom` - Other events

### 5. Generate the Timeline

```bash
python scripts/campaign/timeline_generator.py
```

This creates `campaign/timeline.md` with all events sorted chronologically:

```markdown
# My Campaign Timeline

**Current Day**: Day 10  
**Sessions**: 3  

---

## Day 1

### Session 1: The Beginning

The adventure begins...

- 🎬 Campaign begins

---

## Day 5

### Session 2: Into the Caves

- 👤 Grimbold the Blacksmith first appears
- 📍 Goblin Caves discovered
- ⚔️ Defeated goblin chief

---

## Day 10

### Session 3: The Artifact

- 🔍 Found the ancient artifact
```

## Date Format

Dates use simple day counting from campaign start:
- `Day 1` - First day of campaign
- `Day 15` - Fifteenth day
- `Day 100` - One hundredth day

Parsing is flexible:
- Case-insensitive: `day 5`, `Day 5`, `DAY 5` all work
- Whitespace flexible: `Day5`, `Day 5`, `Day  5` all work

## Event Sources

The timeline generator collects events from:

| Source | What's Collected | Trigger |
|--------|-----------------|---------|
| Sessions | Session summaries | `--in-game-date` on creation |
| NPCs | First appearances | `--first-seen` on creation |
| Locations | Discoveries | `--discovered` on creation |
| events.md | Custom events | Manual table entries |

## Tips

- Add in-game dates consistently to track campaign progression
- Use custom events for major plot points not tied to specific sessions
- Regenerate the timeline after adding new events
- The timeline links to existing entity files for easy navigation

## Troubleshooting

### No events in timeline

Check that you've added in-game dates:
- Sessions need `--in-game-date`
- NPCs need `--first-seen`
- Locations need `--discovered`
- Or add rows to `campaign/events.md`

### Invalid date format

Use "Day N" format:
- Valid: `Day 1`, `Day 15`, `day 100`
- Invalid: `1`, `Day One`, `2026-01-15`

### Missing campaign directory

Initialize your campaign first:

```bash
python scripts/campaign/init_campaign.py "Campaign Name"
```
