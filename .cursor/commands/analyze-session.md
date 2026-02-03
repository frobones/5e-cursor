---
description: Analyze session transcript and populate structured session sections (Summary, Key Events, NPCs, Locations, Loot, Notes)
---

## Context

You are analyzing a D&D session file that contains an audio transcript. Your task is to extract structured information from the transcript and populate the session's sections.

## Required Files

Read the following files to understand the campaign context:

1. **Current file** - The session file (session-NNN.md) containing the transcript
2. **campaign/npcs/index.md** - Existing NPCs for entity linking
3. **campaign/locations/index.md** - Existing locations for entity linking
4. **campaign/party/index.md** - Party members (to distinguish from NPCs)

If any campaign index files don't exist, proceed without entity linking (list names as plain text).

## Instructions

### Step 1: Extract the Transcript

Locate the `## Transcript` section in the current session file. This contains the raw audio transcription.

If no Transcript section exists, STOP and inform the user: "No transcript found in this session file. Run `/analyze-session` on a session created by `transcribe_session.py`."

### Step 2: Analyze the Transcript

Read through the transcript and identify:

1. **Narrative arc** - What happened from start to finish
2. **Key moments** - Combat, discoveries, role-play scenes, decisions
3. **Characters mentioned** - NPCs the party interacted with (not party members)
4. **Places visited** - Locations explored or referenced
5. **Rewards received** - Loot, gold, items, information gained
6. **Unresolved threads** - Cliffhangers, plot hooks, things to remember

### Step 3: Check Entity Matches

For each NPC and location mentioned:

1. Check if a matching name exists in `campaign/npcs/index.md` or `campaign/locations/index.md`
2. Matching is **case-insensitive** (e.g., "grimbold" matches "Grimbold")
3. If match found, format as link: `[Entity Name](../npcs/entity-name.md)`
4. If no match found, format as: `Entity Name (NEW)`

**Important**: Names appearing in `campaign/party/index.md` are party members, NOT NPCs. Do not list them in NPCs Encountered.

### Step 4: Populate Each Section

Replace the placeholder text in each section with analyzed content:

#### Summary
Write 2-3 paragraphs that tell the story of the session. Include:
- How the session started
- Major events and turning points
- How the session ended

#### Key Events
Create a bullet list of 5-10 significant moments:
- Combat encounters
- Important discoveries
- Meaningful NPC interactions
- Player decisions with consequences
- Plot revelations

#### NPCs Encountered
List each NPC with:
- Link to existing file OR (NEW) marker
- Brief note about their role in the session

Example:
```markdown
- [Grimbold the Blacksmith](../npcs/grimbold-the-blacksmith.md) - Repaired party's armor
- Cultist Leader Vex (NEW) - Escaped through secret passage
```

#### Locations Visited
List each location with:
- Link to existing file OR (NEW) marker
- Brief note about what happened there

Example:
```markdown
- [Millbrook](../locations/millbrook.md) - Village center, met with blacksmith
- Cult Hideout (NEW) - Underground chamber beneath the tavern
```

#### Loot & Rewards
List any items, gold, or rewards mentioned:
- Gold pieces or other currency
- Magic items or equipment
- Information or secrets learned
- Favors or alliances gained

If no loot was mentioned, write: "*No loot or rewards identified in this session.*"

#### Notes for Next Session
Capture things the DM should remember:
- Unresolved plot threads
- Cliffhangers or immediate dangers
- NPC motivations revealed
- Questions left unanswered
- Player goals or intentions mentioned

### Step 5: Preserve Original Content

**DO NOT MODIFY** the following sections:
- The metadata header (Date, Session Number, Audio Source, Transcription Model)
- The `## Transcript` section and its contents
- The footer with creation date and transcript path

### Step 6: Apply Changes

Edit the session file to replace placeholder text with your analyzed content. Make the changes directly to the file.

## Output Format

After completing the analysis, summarize what you did:

1. Sections populated
2. Number of NPCs identified (X existing, Y new)
3. Number of locations identified (X existing, Y new)
4. Any sections that couldn't be populated (and why)

## Example Transformation

**Before:**
```markdown
## NPCs Encountered

*Ask Cursor AI to identify NPCs mentioned*
```

**After:**
```markdown
## NPCs Encountered

- [Grimbold the Blacksmith](../npcs/grimbold-the-blacksmith.md) - Repaired armor, warned about bandits
- [Innkeeper Martha](../npcs/innkeeper-martha.md) - Seemed nervous, hid something
- The Hooded Stranger (NEW) - Watched party from corner, left quickly
- Bandit Leader Kira (NEW) - Ambushed party on road, escaped
```
