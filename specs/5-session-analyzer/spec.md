# Feature Specification: Session Transcript Analyzer

**Feature Branch**: `5-session-analyzer`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: Cursor Command that analyzes session transcripts and populates structured session sections (Summary, Key Events, NPCs, Locations, Loot, Notes) using Cursor's AI.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Analyze Session Transcript (Priority: P1)

As a DM, I want to run a command that analyzes my session transcript so that the structured sections of my session file are automatically populated.

**Why this priority**: This is the core functionality - converting raw transcript into structured notes without manual prompting.

**Independent Test**: Can be fully tested by opening a session file with a transcript and running the `/analyze-session` command.

**Acceptance Scenarios**:

1. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the AI reads the transcript and fills in the Summary section with a 2-3 paragraph overview
2. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the Key Events section is populated with a bullet list of significant moments
3. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the NPCs Encountered section lists characters mentioned
4. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the Locations Visited section lists places explored
5. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the Loot & Rewards section lists any treasure or items mentioned
6. **Given** a session file with a Transcript section, **When** I run `/analyze-session`, **Then** the Notes for Next Session section captures plot hooks and cliffhangers

---

### User Story 2 - Link to Existing Campaign Entities (Priority: P2)

As a DM, I want the analyzer to link mentioned NPCs and locations to existing campaign files so that I can navigate between related content.

**Why this priority**: Builds on P1 by adding context-awareness. Links make the campaign data interconnected and navigable.

**Independent Test**: Can be fully tested by having existing NPCs/locations in the campaign and verifying they are linked in the analyzed output.

**Acceptance Scenarios**:

1. **Given** an NPC mentioned in the transcript that exists in `campaign/npcs/`, **When** analysis completes, **Then** the NPC name links to the existing file: `[NPC Name](../npcs/npc-name.md)`
2. **Given** a location mentioned in the transcript that exists in `campaign/locations/`, **When** analysis completes, **Then** the location name links to the existing file: `[Location](../locations/location-name.md)`
3. **Given** an NPC mentioned that does NOT exist in campaign data, **When** analysis completes, **Then** the NPC is marked: `NPC Name (NEW)`
4. **Given** a location mentioned that does NOT exist in campaign data, **When** analysis completes, **Then** the location is marked: `Location Name (NEW)`
5. **Given** party members are mentioned, **When** analysis completes, **Then** they are NOT listed as NPCs (distinguished via party index)

---

### User Story 3 - Preserve Original Content (Priority: P3)

As a DM, I want the analyzer to preserve the transcript and metadata so that I don't lose the original recording information.

**Why this priority**: Data integrity - never destroy original content during analysis.

**Independent Test**: Can be fully tested by verifying metadata and transcript sections remain unchanged after analysis.

**Acceptance Scenarios**:

1. **Given** a session file with metadata (Date, Session Number, Audio Source, Model), **When** analysis completes, **Then** the metadata section is unchanged
2. **Given** a session file with a Transcript section, **When** analysis completes, **Then** the Transcript section content is unchanged
3. **Given** a session file with footer text, **When** analysis completes, **Then** the footer is preserved

---

### Edge Cases

- What happens when the session file has no Transcript section?
  - Display message: "No transcript found. This command requires a session with an embedded transcript."
- What happens when the transcript is very short (< 100 words)?
  - Analyze anyway; some sections may be marked as "No {events/NPCs/etc.} identified"
- What happens when campaign indexes don't exist?
  - Skip entity linking; list all as plain text (no links, no NEW markers)
- What happens when a section already has content (not placeholder text)?
  - Replace with analyzed content (DM can undo if needed)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Command MUST read the current session file's Transcript section
- **FR-002**: Command MUST read campaign context (npcs/index.md, locations/index.md, party/index.md)
- **FR-003**: Command MUST populate Summary section with 2-3 paragraph narrative overview
- **FR-004**: Command MUST populate Key Events section with bullet list of significant moments
- **FR-005**: Command MUST populate NPCs Encountered section with character names
- **FR-006**: Command MUST populate Locations Visited section with place names
- **FR-007**: Command MUST populate Loot & Rewards section with items/treasure mentioned
- **FR-008**: Command MUST populate Notes for Next Session with plot hooks and cliffhangers
- **FR-009**: Command MUST link NPCs to existing files when matches are found
- **FR-010**: Command MUST link locations to existing files when matches are found
- **FR-011**: Command MUST mark new entities with "(NEW)" suffix
- **FR-012**: Command MUST preserve metadata and transcript sections unchanged
- **FR-013**: Command MUST distinguish party members from NPCs

### Key Entities

- **SessionFile**: The session markdown file being analyzed
- **Transcript**: The raw transcript text embedded in the session file
- **CampaignContext**: Existing NPCs, locations, and party members for entity linking

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `/analyze-session` fills all 6 structured sections in under 30 seconds
- **SC-002**: Existing NPCs and locations are correctly linked 90%+ of the time
- **SC-003**: New entities are correctly marked as (NEW) when not in campaign data
- **SC-004**: Original transcript and metadata are never modified
- **SC-005**: Command provides clear feedback if no transcript is found

## Assumptions

- User has a session file with an embedded Transcript section
- Campaign directory exists with npcs/, locations/, and party/ subdirectories
- User is running the command within Cursor IDE
- Cursor AI has access to read campaign files for context

## Dependencies

- Existing session file format from `transcribe_session.py`
- Existing campaign structure from `init_campaign.py`
- Cursor's built-in AI capabilities (no external API keys needed)
- Campaign index files for entity matching
