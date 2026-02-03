# Quickstart: Session Transcript Analyzer

Automatically analyze session transcripts and populate structured session notes.

## Prerequisites

- A session file with an embedded transcript (from `transcribe_session.py`)
- Campaign initialized with NPCs and locations directories
- Cursor IDE

## Basic Usage

### 1. Transcribe Your Session

First, transcribe your audio recording:

```bash
python scripts/campaign/transcribe_session.py "recording.mp3" --title "The Dragon's Lair"
```

### 2. Open the Session File

Open the created session file in Cursor:

```
campaign/sessions/session-NNN.md
```

### 3. Run the Analyze Command

With the session file open, invoke the Cursor command:

```
/analyze-session
```

The AI will:
1. Read the transcript section
2. Check existing NPCs and locations for linking
3. Fill in all structured sections:
   - Summary
   - Key Events
   - NPCs Encountered
   - Locations Visited
   - Loot & Rewards
   - Notes for Next Session

## Example Output

Before analysis:

```markdown
## Summary

*Ask Cursor AI to summarize the transcript below*

## NPCs Encountered

*Ask Cursor AI to identify NPCs mentioned*
```

After analysis:

```markdown
## Summary

The party returned to Millbrook after escaping the goblin caves. They sought out Grimbold the Blacksmith to repair their damaged equipment and learned troubling news about disappearances in the village...

## NPCs Encountered

- [Grimbold the Blacksmith](../npcs/grimbold-the-blacksmith.md) - Repaired armor, shared rumors
- [Innkeeper Martha](../npcs/innkeeper-martha.md) - Acted suspiciously when questioned
- Cultist Leader Vex (NEW) - Escaped through secret passage
```

## Entity Linking

The analyzer automatically links to existing campaign data:

- **Existing NPCs**: `[Name](../npcs/name.md)`
- **Existing Locations**: `[Name](../locations/name.md)`
- **New entities**: `Name (NEW)` - Create these with `campaign_manager.py`

## After Analysis

1. **Review the sections** - Edit any AI-generated content as needed
2. **Create new entities** - For items marked (NEW):

   ```bash
   # Add new NPC
   python scripts/campaign/campaign_manager.py add-npc "Cultist Leader Vex" --role enemy

   # Add new location
   python scripts/campaign/campaign_manager.py add-location "Cult Hideout" --type dungeon
   ```

3. **Commit changes** - Save your session notes to git

## Tips

- The analyzer preserves your original transcript - it's never modified
- Party members are automatically excluded from the NPC list
- Run the command again if you want to re-analyze (will overwrite sections)
- For best results, ensure your NPC and location indexes are up to date

## Troubleshooting

### "No transcript found"

The session file must have a `## Transcript` section with content. Run `transcribe_session.py` first.

### NPCs not being linked

Check that the NPC exists in `campaign/npcs/index.md`. The matching is case-insensitive.

### Missing campaign directories

Initialize your campaign first:

```bash
python scripts/campaign/init_campaign.py "Campaign Name"
```
