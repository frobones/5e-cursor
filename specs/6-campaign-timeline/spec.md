# Feature Specification: Campaign Timeline

**Feature Branch**: `6-campaign-timeline`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: Track both real-world and in-game dates, aggregate events from sessions/NPCs/locations, support custom events, and generate a chronological timeline markdown file.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Track In-Game Dates for Sessions (Priority: P1)

As a DM, I want to record when sessions occur in the game world so that I can track the passage of in-game time across my campaign.

**Why this priority**: Foundation for timeline - without in-game dates, events cannot be chronologically ordered in the game world.

**Independent Test**: Can be fully tested by creating a session with an in-game date and verifying it appears in the session file.

**Acceptance Scenarios**:

1. **Given** a new session, **When** I provide `--in-game-date "Day 15"`, **Then** the session file includes `**In-Game Date**: Day 15`
2. **Given** a session without `--in-game-date`, **When** created, **Then** the session file has no In-Game Date field (optional field)
3. **Given** an in-game date, **When** viewing the session, **Then** the format is human-readable (e.g., "Day 15")

---

### User Story 2 - Track Entity First Appearances (Priority: P2)

As a DM, I want to record when NPCs first appeared and when locations were discovered so that I can see the campaign's progression.

**Why this priority**: Extends P1 by adding timeline data to other entities.

**Independent Test**: Can be fully tested by creating NPCs/locations with first appearance dates.

**Acceptance Scenarios**:

1. **Given** a new NPC, **When** I provide `--first-seen "Day 12"`, **Then** the NPC file includes `**First Appearance**: Day 12`
2. **Given** a new location, **When** I provide `--discovered "Day 10"`, **Then** the location file includes `**Discovered**: Day 10`
3. **Given** an entity without appearance date, **When** created, **Then** no appearance field is added (optional)

---

### User Story 3 - Add Custom Campaign Events (Priority: P2)

As a DM, I want to record major campaign events (battles, plot points) so that I have a complete record of what happened.

**Why this priority**: Enables full event tracking beyond sessions.

**Independent Test**: Can be fully tested by editing events.md and verifying events appear in timeline.

**Acceptance Scenarios**:

1. **Given** a campaign, **When** initialized, **Then** an `events.md` template file exists
2. **Given** an event in `events.md` table, **When** timeline is generated, **Then** the event appears in chronological order
3. **Given** an event with session reference, **When** displayed, **Then** it links to the session

---

### User Story 4 - Generate Campaign Timeline (Priority: P1)

As a DM, I want to generate a chronological timeline of my campaign so that I can see the full history at a glance.

**Why this priority**: Core deliverable - produces the timeline.md output.

**Independent Test**: Can be fully tested by running timeline generator and verifying output.

**Acceptance Scenarios**:

1. **Given** sessions with in-game dates, **When** I run timeline generator, **Then** `campaign/timeline.md` is created
2. **Given** events from multiple sources, **When** generated, **Then** all events appear sorted by in-game date
3. **Given** NPCs with first appearances, **When** generated, **Then** NPC appearances show in timeline
4. **Given** custom events in `events.md`, **When** generated, **Then** they appear in the timeline
5. **Given** an entity that exists, **When** shown in timeline, **Then** it links to the entity file

---

### Edge Cases

- What happens when no in-game dates exist?
  - Timeline shows only real-world dates with a warning
- What happens when in-game date format is invalid?
  - Display error message with expected format
- What happens when events.md doesn't exist?
  - Skip custom events, continue with other sources
- What happens when timeline.md already exists?
  - Overwrite with regenerated content

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support in-game dates in format "Day N" (simple sequential days)
- **FR-002**: System MUST add `--in-game-date` option to session creation
- **FR-003**: System MUST add `--first-seen` option to NPC creation
- **FR-004**: System MUST add `--discovered` option to location creation
- **FR-005**: System MUST create `events.md` template during campaign initialization
- **FR-006**: System MUST parse events from events.md table format
- **FR-007**: System MUST collect events from sessions (with in-game dates)
- **FR-008**: System MUST collect events from NPCs (first appearances)
- **FR-009**: System MUST collect events from locations (discoveries)
- **FR-010**: System MUST sort all events by in-game date
- **FR-011**: System MUST generate `campaign/timeline.md` with chronological events
- **FR-012**: System MUST link to existing entity files in timeline
- **FR-013**: System MUST show both real-world and in-game dates when available

### Key Entities

- **InGameDate**: Simple day counter (Day 1, Day 2, etc.)
- **TimelineEvent**: Event with in-game date, title, category, and optional session/entity links
- **Timeline**: Aggregated, sorted collection of all events

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Timeline generation completes in under 5 seconds for 50+ sessions
- **SC-002**: All event sources (sessions, NPCs, locations, custom) appear in timeline
- **SC-003**: Events are correctly sorted by in-game date
- **SC-004**: Entity links are valid and point to existing files
- **SC-005**: Timeline is regenerable without data loss

## Assumptions

- Users track in-game time using simple day counting (Day 1, Day 2, etc.)
- Campaign has a linear timeline (no time travel or parallel timelines)
- Events.md is manually edited by the DM
- Timeline regeneration is acceptable (not incremental updates)

## Dependencies

- Existing `session_manager.py` for session creation
- Existing `campaign_manager.py` for NPC/location creation
- Existing `init_campaign.py` for campaign initialization
- Existing `markdown_writer.py` for markdown utilities
