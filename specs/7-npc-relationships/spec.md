# Feature Specification: NPC Relationship Graph

**Feature Branch**: `7-npc-relationships`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: Track typed relationships between NPCs with descriptions and generate a visual Mermaid diagram showing all connections.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Define NPC Relationships (Priority: P1)

As a DM, I want to define relationships between NPCs so that I can track how characters are connected in my campaign.

**Why this priority**: Foundation for the feature - without relationship data, there's nothing to visualize.

**Independent Test**: Can be fully tested by adding relationships to NPC files and verifying they parse correctly.

**Acceptance Scenarios**:

1. **Given** an NPC file, **When** I add a relationship in the structured format, **Then** the relationship is parseable
2. **Given** a relationship with type and description, **When** parsed, **Then** both type and description are extracted
3. **Given** a relationship with a link to another NPC file, **When** parsed, **Then** the target NPC is identified

---

### User Story 2 - Add Relationships via CLI (Priority: P2)

As a DM, I want to add relationships between NPCs via command line so that relationships are created bidirectionally and consistently.

**Why this priority**: Convenience feature that builds on P1.

**Independent Test**: Can be tested by running the command and verifying both NPC files are updated.

**Acceptance Scenarios**:

1. **Given** two existing NPCs, **When** I run `add-relationship`, **Then** both NPC files have the relationship added
2. **Given** a relationship type, **When** added, **Then** the inverse type is used for the reverse relationship
3. **Given** a non-existent NPC name, **When** I run the command, **Then** an error is displayed

---

### User Story 3 - Generate Relationship Graph (Priority: P1)

As a DM, I want to generate a visual graph of NPC relationships so that I can see how all characters are connected at a glance.

**Why this priority**: Core deliverable - produces the visualization.

**Independent Test**: Can be tested by running the generator and verifying the output Mermaid diagram.

**Acceptance Scenarios**:

1. **Given** NPCs with relationships, **When** I run the graph generator, **Then** `campaign/relationships.md` is created
2. **Given** typed relationships, **When** generated, **Then** edge labels show the relationship type
3. **Given** bidirectional relationships, **When** generated, **Then** both directions appear in the graph
4. **Given** no relationships, **When** generated, **Then** a message indicates no relationships found

---

### Edge Cases

- What happens when an NPC references a non-existent NPC?
  - Show the name without a link in the graph, log a warning
- What happens when relationships are not bidirectional?
  - Show only the defined direction
- What happens when relationship type is invalid?
  - Accept any type, show warning for non-standard types

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define a structured format for relationships in NPC files
- **FR-002**: Relationship format MUST include: target name, type, and optional description
- **FR-003**: System MUST support both linked `[Name](file.md)` and plain `Name` formats
- **FR-004**: System MUST support relationship types: ally, enemy, family, employer, employee, rival, neutral, romantic, mentor
- **FR-005**: System MUST parse relationships from `## Connections` section in NPC files
- **FR-006**: System MUST provide `add-relationship` command to create bidirectional relationships
- **FR-007**: Add-relationship MUST update both source and target NPC files
- **FR-008**: System MUST generate Mermaid flowchart diagram of all relationships
- **FR-009**: System MUST output graph to `campaign/relationships.md`
- **FR-010**: Graph MUST show relationship types as edge labels
- **FR-011**: Graph MUST link to NPC files where possible

### Key Entities

- **Relationship**: Connection between two NPCs with type and description
- **RelationshipType**: Enumeration of valid relationship types
- **NPCGraph**: Collection of all NPCs and their relationships

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Graph generation completes in under 2 seconds for 50+ NPCs
- **SC-002**: All relationship types are correctly parsed and displayed
- **SC-003**: Mermaid diagram renders correctly in markdown viewers
- **SC-004**: Bidirectional relationships are correctly created by add-relationship command

## Assumptions

- NPCs are stored in `campaign/npcs/*.md`
- NPC files have a `## Connections` section
- Mermaid diagrams are supported in the markdown viewer (GitHub, Cursor, etc.)

## Dependencies

- Existing `campaign_manager.py` for NPC file management
- Existing NPC file structure with `## Connections` section
- Existing `markdown_writer.py` for markdown utilities
