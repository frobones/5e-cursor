# Feature Specification: Campaign Assistant

**Feature Branch**: `1-campaign-assistant`  
**Created**: 2026-01-28  
**Status**: Draft  
**Input**: User description: "Campaign Assistant: A single-campaign D&D management system built on extracted 5e reference data. Features: (1) Full character sheet storage with D&D Beyond import via public character API, auto-linking to reference data for class features, spells, and items, (2) Encounter builder using DMG balance guidelines based on party level and size, (3) Rules arbitration engine providing inline-quoted answers from extracted rules, (4) Session summary tracking for campaign history. All data in markdown format stored in a campaign/ directory structure."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Import Character from D&D Beyond (Priority: P1)

As a DM, I want to import player characters directly from D&D Beyond so that I have complete, accurate character sheets linked to my reference data without manual data entry.

**Why this priority**: Character data is the foundation of all other features. Without accurate party information, encounter building and rules arbitration cannot function correctly. This delivers immediate value by eliminating manual character transcription.

**Independent Test**: Can be fully tested by providing a D&D Beyond character URL and verifying a complete markdown character sheet is created with working links to reference data.

**Acceptance Scenarios**:

1. **Given** a public D&D Beyond character URL, **When** I request character import, **Then** the system creates a markdown file in `campaign/party/characters/` with all character stats, features, and equipment
2. **Given** an imported character with class features, **When** viewing the character sheet, **Then** each class feature links to the corresponding reference file in `books/reference/classes/`
3. **Given** an imported character with spells, **When** viewing the character sheet, **Then** each spell links to the corresponding reference file in `books/reference/spells/`
4. **Given** a private or invalid D&D Beyond URL, **When** I request character import, **Then** the system provides a clear error message explaining the issue

---

### User Story 2 - Build Balanced Encounters (Priority: P2)

As a DM, I want to generate balanced encounters based on my party's composition so that I can quickly prepare appropriate challenges for my sessions.

**Why this priority**: Encounter building is the most time-consuming prep task for DMs. With party data from P1, this feature enables rapid session preparation using the existing creature database.

**Independent Test**: Can be fully tested by specifying party level, size, and difficulty, then verifying the generated encounter meets DMG XP thresholds.

**Acceptance Scenarios**:

1. **Given** a party of known level and size, **When** I request an Easy/Medium/Hard/Deadly encounter, **Then** the system generates a creature list with total XP within DMG guidelines
2. **Given** an encounter request, **When** the encounter is generated, **Then** each creature links to its full stat block in `books/reference/creatures/`
3. **Given** an encounter, **When** I save it, **Then** it is stored in `campaign/encounters/` with creature details and XP breakdown
4. **Given** optional filters (creature type, environment, CR range), **When** generating an encounter, **Then** only matching creatures are included

---

### User Story 3 - Answer Rules Questions with Citations (Priority: P3)

As a DM or player, I want to ask rules questions and receive authoritative answers with inline quotes so that I can make informed rulings during gameplay.

**Why this priority**: Rules arbitration adds significant value during live play, but requires the reference data (already exists) and is most useful once a campaign is active.

**Independent Test**: Can be fully tested by asking a rules question and verifying the response includes inline quotes from the extracted rules files with source citations.

**Acceptance Scenarios**:

1. **Given** a rules question about a condition (e.g., "What does Prone do?"), **When** I ask, **Then** the system provides an answer with inline-quoted text from the relevant rules file
2. **Given** a rules question about a spell or ability, **When** I ask, **Then** the system cites the specific source file and includes the relevant text
3. **Given** an ambiguous or unclear question, **When** I ask, **Then** the system requests clarification or provides multiple relevant rules sections

---

### User Story 4 - Track Session History (Priority: P4)

As a DM, I want to record session summaries so that I have a persistent campaign history for reference and continuity.

**Why this priority**: Session tracking is valuable for long-term campaign management but is the least technically complex and can be simple text files. It enhances other features but isn't required for them to function.

**Independent Test**: Can be fully tested by creating a session summary and verifying it appears in the session log with proper date and session number.

**Acceptance Scenarios**:

1. **Given** a new session, **When** I create a session summary, **Then** it is saved as `campaign/sessions/session-NNN.md` with date and summary content
2. **Given** multiple sessions, **When** viewing the session index, **Then** all sessions are listed chronologically with dates and titles
3. **Given** session content mentioning NPCs or locations, **When** reviewing sessions, **Then** mentioned entities can be linked to their respective files

---

### User Story 5 - Manage Campaign State (Priority: P5)

As a DM, I want to create and organize NPCs, locations, and campaign notes so that all my campaign information is in one place.

**Why this priority**: Campaign state management provides organizational value but is the most flexible feature - DMs can create markdown files manually if needed. This formalizes the structure.

**Independent Test**: Can be fully tested by creating an NPC, location, or campaign note and verifying proper file placement and index updates.

**Acceptance Scenarios**:

1. **Given** a new NPC, **When** I create it, **Then** it is saved in `campaign/npcs/` with name, description, and relationship fields
2. **Given** a new location, **When** I create it, **Then** it is saved in `campaign/locations/` with name, description, and connection fields
3. **Given** existing campaign entities, **When** viewing any index file, **Then** all entities of that type are listed with links

---

### User Story 6 - AI-Assisted NPC & Location Generation (Priority: P6)

As a DM, I want AI assistance when creating NPCs and locations so that I can provide partial details and have them expanded into rich, campaign-consistent entities without extensive manual writing.

**Why this priority**: Builds on the foundation of User Story 5 (campaign state management) by adding intelligent expansion capabilities. Requires existing campaign context to function effectively, making it a natural extension rather than a foundational feature.

**Independent Test**: Can be tested by providing minimal NPC or location details (e.g., "a blacksmith") and verifying the AI generates a complete, thematically appropriate entity that connects to existing campaign elements.

**Acceptance Scenarios**:

1. **Given** a partial NPC description (e.g., "tavern keeper named Mira"), **When** I request AI-assisted generation, **Then** the system expands it with physical description, personality traits, connections, and secrets that fit the campaign setting
2. **Given** a partial location description (e.g., "an old temple in the woods"), **When** I request AI-assisted generation, **Then** the system expands it with sensory details, notable features, potential encounters, and hooks
3. **Given** existing NPCs and locations in the campaign, **When** generating a new entity, **Then** the AI suggests logical connections to existing campaign elements
4. **Given** the campaign's established setting and themes, **When** generating content, **Then** the AI maintains consistency with the campaign's tone and world-building
5. **Given** generated content, **When** presented to the user, **Then** the user can approve, modify, or regenerate before the file is created

---

### Edge Cases

- What happens when D&D Beyond character has homebrew content not in our reference data?
  - System imports the character but marks unlinked items with "[No Reference]" notation
- What happens when party composition changes mid-campaign?
  - Encounter builder always uses current party state; historical encounters retain their original values
- How does the system handle multiclass characters?
  - All class levels are imported with features from each class linked appropriately
- What happens when a creature doesn't have a CR (e.g., CR 0 or variable CR)?
  - CR 0 creatures are treated as minimal XP; variable CR creatures use their average or specified CR
- What happens when AI-generated content conflicts with existing campaign elements?
  - AI checks for name conflicts before generation; user is warned and asked to choose a different name
- What happens when the campaign has no existing context (fresh campaign)?
  - AI uses D&D reference data and general fantasy tropes; encourages user to establish setting in campaign.md first
- How does the AI handle requests for content that doesn't fit the campaign setting?
  - AI flags potential inconsistencies and asks user to confirm before proceeding (e.g., sci-fi elements in fantasy setting)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST import characters from D&D Beyond public character URLs via the character API
- **FR-002**: System MUST convert D&D Beyond JSON to markdown character sheets in standardized format
- **FR-003**: System MUST auto-link character features, spells, and items to extracted reference files
- **FR-004**: System MUST calculate encounter difficulty using DMG XP thresholds for Easy/Medium/Hard/Deadly
- **FR-005**: System MUST filter creatures by CR, type, and environment when generating encounters
- **FR-006**: System MUST provide rules answers with inline-quoted text from extracted rules files
- **FR-007**: System MUST store session summaries with sequential numbering and dates
- **FR-008**: System MUST maintain index files for party, NPCs, locations, sessions, and encounters
- **FR-009**: System MUST store all campaign data in markdown format in the `campaign/` directory structure
- **FR-010**: System MUST calculate party level as average of all character levels for encounter building
- **FR-011**: AI-assisted generation MUST read campaign context (campaign.md, existing NPCs, locations) before generating content
- **FR-012**: AI-assisted generation MUST present expanded content for user approval before creating files
- **FR-013**: AI-assisted generation MUST check for name conflicts with existing entities before creating new ones
- **FR-014**: AI-assisted generation MUST maintain setting consistency with established campaign themes and tone

### Key Entities

- **Character**: Player character with stats, class, level, equipment, features, spells; imported from D&D Beyond or created manually; links to class/feat/spell/item references
- **Encounter**: Collection of creatures with total XP and difficulty rating; links to creature stat blocks; may be saved for reuse
- **Session**: Summary of a play session with date, number, and narrative content; may reference NPCs/locations
- **NPC**: Non-player character with name, description, relationships, and role in campaign
- **Location**: Place in the campaign world with name, description, and connections to other locations
- **Campaign**: Top-level entity containing settings, themes, and references to all other entities

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can import a D&D Beyond character and have a complete, linked character sheet in under 30 seconds
- **SC-002**: Generated encounters match DMG difficulty guidelines within 10% of target XP thresholds
- **SC-003**: 90% of common rules questions receive accurate answers with source citations on first attempt
- **SC-004**: Users can create a session summary in under 2 minutes
- **SC-005**: All generated markdown files are human-readable and editable in any text editor
- **SC-006**: Campaign data remains git-trackable with clean diffs for version control
- **SC-007**: Character sheets display all D&D Beyond data without loss of information
- **SC-008**: AI-generated NPCs include at minimum: name, physical description, personality, and one connection to existing campaign elements
- **SC-009**: AI-generated locations include at minimum: name, sensory description, notable features, and potential encounters
- **SC-010**: 80% of AI-generated content requires no major revisions before user approval

## Assumptions

- D&D Beyond characters must be set to "Public" privacy for API access
- The extracted 5etools reference data exists in `books/` directory before using campaign features
- Users interact with the system through Cursor AI rather than a standalone application
- Single campaign per repository (multi-campaign support deferred to future versions)
- Session summaries are free-form text; structured session data (combat logs, etc.) deferred

## Dependencies

- Extracted reference data from `books/` directory (spells, creatures, classes, items, rules, etc.)
- `books/reference-index.json` for name-to-path lookups when auto-linking
- Network access to D&D Beyond API for character imports
