# Implementation Plan: Session Transcript Analyzer

**Branch**: `5-session-analyzer` | **Date**: 2026-02-02 | **Spec**: [spec.md](spec.md)

## Summary

Implement a Cursor Command (`/analyze-session`) that analyzes session transcripts and populates structured session sections, with integration into the transcription workflow.

## Technical Context

**Implementation**: Cursor Command (markdown file with AI instructions)  
**Storage**: `.cursor/commands/analyze-session.md`  
**Integration**: Update to `transcribe_session.py` for workflow prompt  
**Testing**: Manual testing with sample session files  
**Dependencies**: Cursor IDE, existing campaign structure

## Architecture

```mermaid
flowchart TD
    subgraph transcription [Transcription Flow]
        Audio[Audio File] --> Transcribe[transcribe_session.py]
        Transcribe --> SessionFile[Session File with Transcript]
        Transcribe --> Prompt[Print: Run /analyze-session]
    end

    subgraph analysis [Analysis Flow]
        SessionFile --> Command[/analyze-session Command]
        Command --> ReadTranscript[Read Transcript Section]
        Command --> ReadCampaign[Read Campaign Context]
        ReadCampaign --> ExistingNPCs[NPCs Index]
        ReadCampaign --> ExistingLocs[Locations Index]
        ReadCampaign --> PartyIndex[Party Index]
        ReadTranscript --> AIAnalysis[Cursor AI Analysis]
        AIAnalysis --> FillSections[Fill Session Sections]
        FillSections --> LinkEntities[Link to Existing Entities]
        FillSections --> MarkNew[Mark New Entities]
    end
```

## Components

### 1. Cursor Command: `/analyze-session`

**File**: `.cursor/commands/analyze-session.md`

The command will:
- Read the current session file (must have a Transcript section)
- Read campaign context (existing NPCs, locations, party from indexes)
- Instruct AI to analyze transcript and fill sections
- Link mentioned entities to existing campaign data
- Mark new entities that should be created

### 2. Integration with transcribe_session.py

Update the final output to prompt the user to run the analyze command:

```python
print("Next steps:")
print(f"  1. Open {session_path} in Cursor")
print("  2. Run /analyze-session to auto-fill session sections")
```

### 3. Campaign Context Reading

The command reads existing campaign data for entity linking:

- `campaign/npcs/index.md` - List of existing NPCs
- `campaign/locations/index.md` - List of existing locations
- `campaign/party/index.md` - Party members (to distinguish from NPCs)

## Session Sections to Populate

| Section | Content |
|---------|---------|
| Summary | 2-3 paragraph narrative overview |
| Key Events | Bullet list of significant moments |
| NPCs Encountered | Character names with links or (NEW) markers |
| Locations Visited | Place names with links or (NEW) markers |
| Loot & Rewards | Items, treasure, gold received |
| Notes for Next Session | Plot hooks, cliffhangers, unresolved threads |

## Entity Linking Rules

1. **Match existing entities**: Search indexes for name matches (case-insensitive)
2. **Link format**: `[Entity Name](../npcs/entity-name.md)` or `[Entity Name](../locations/entity-name.md)`
3. **New entity format**: `Entity Name (NEW)`
4. **Party exclusion**: Party members from party/index.md are not listed as NPCs

## File Changes

| File | Change |
|------|--------|
| `.cursor/commands/analyze-session.md` | NEW - Cursor command definition |
| `scripts/campaign/transcribe_session.py` | UPDATE - Add analyze prompt to output |
| `.cursor/rules/campaign-lookup.mdc` | UPDATE - Document /analyze-session command |

## Constitution Compliance

- **AI-First Design**: Command leverages Cursor AI context window
- **DM as Final Authority**: AI fills sections; DM reviews and edits
- **Markdown as Truth**: All output is markdown, git-trackable
- **Modular**: Works independently, enhances existing transcription feature
