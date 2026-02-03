# Feature Specification: Loot Generator

**Feature Branch**: `3-loot-generator`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: User description: "Loot Generator: Runtime treasure generation using DMG 2024 tables. Generate individual treasure (coins) and treasure hoards (coins, gems, art objects, magic items) by CR tier. Integrate with encounter builder for encounter-based loot. Support saving loot to session files. All generated magic items link to reference data."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Individual Treasure (Priority: P1)

As a DM, I want to generate individual treasure for defeated creatures based on their CR so that I can quickly determine coin drops without consulting physical books.

**Why this priority**: Individual treasure is the most common loot scenario - every combat encounter may require it. This provides immediate value with minimal complexity (coins only, no items).

**Independent Test**: Can be fully tested by specifying a CR and verifying the output contains appropriate coin types and amounts according to DMG CR tiers.

**Acceptance Scenarios**:

1. **Given** a CR between 0-4, **When** I request individual treasure, **Then** the system generates coins from the Individual Treasure CR 0-4 table
2. **Given** a CR between 5-10, **When** I request individual treasure, **Then** the system generates coins from the Individual Treasure CR 5-10 table
3. **Given** a CR between 11-16, **When** I request individual treasure, **Then** the system generates coins from the Individual Treasure CR 11-16 table
4. **Given** a CR of 17+, **When** I request individual treasure, **Then** the system generates coins from the Individual Treasure CR 17+ table
5. **Given** a `--count N` flag, **When** I request individual treasure, **Then** the system generates treasure for N creatures and totals the results
6. **Given** a `--seed` value, **When** I request individual treasure, **Then** the output is deterministic and reproducible

---

### User Story 2 - Generate Treasure Hoard (Priority: P2)

As a DM, I want to generate complete treasure hoards with coins, gems, art objects, and magic items so that I can quickly stock dungeons and reward major encounters.

**Why this priority**: Hoards are the primary treasure type for significant encounters and dungeon stocking. Builds on P1 by adding gems, art objects, and magic items.

**Independent Test**: Can be fully tested by specifying a CR and verifying the output contains coins, gems/art objects, and magic items according to DMG hoard tables.

**Acceptance Scenarios**:

1. **Given** a CR between 0-4, **When** I request a treasure hoard, **Then** the system generates coins, optionally gems/art, and magic items per the CR 0-4 Hoard table
2. **Given** a CR between 5-10, **When** I request a treasure hoard, **Then** the system generates appropriate treasure per the CR 5-10 Hoard table
3. **Given** a CR between 11-16, **When** I request a treasure hoard, **Then** the system generates appropriate treasure per the CR 11-16 Hoard table
4. **Given** a CR of 17+, **When** I request a treasure hoard, **Then** the system generates appropriate treasure per the CR 17+ Hoard table
5. **Given** generated magic items, **When** viewing the output, **Then** each magic item is linked to its reference file in `books/reference/items/`
6. **Given** gems or art objects in the hoard, **When** viewing the output, **Then** specific gem/art names are listed with their gp values

---

### User Story 3 - Roll on Magic Item Tables (Priority: P3)

As a DM, I want to roll directly on specific magic item tables (A through I) so that I can manually place treasure or resolve hoard table results.

**Why this priority**: Enables fine-grained control over treasure and supports DMs who want to customize rewards. Essential for resolving hoard table results that reference specific magic item tables.

**Independent Test**: Can be fully tested by specifying a table letter and verifying the output is a valid item from that table with a reference link.

**Acceptance Scenarios**:

1. **Given** a request for Magic Item Table A, **When** I roll, **Then** the system returns an item from Table A (minor consumables like potions)
2. **Given** a request for Magic Item Table F, **When** I roll, **Then** the system returns an item from Table F (uncommon/rare permanent items)
3. **Given** a request for Magic Item Table I, **When** I roll, **Then** the system returns an item from Table I (legendary items)
4. **Given** any generated magic item, **When** viewing the output, **Then** the item links to its reference file if one exists
5. **Given** a `--count N` flag, **When** I roll on a table, **Then** the system generates N items from that table

---

### User Story 4 - Encounter-Based Loot (Priority: P4)

As a DM, I want to generate loot appropriate for a saved encounter so that treasure matches the challenge I've prepared.

**Why this priority**: Integrates with the existing encounter builder workflow. Reduces manual work by automatically determining CR from encounter files.

**Independent Test**: Can be fully tested by referencing a saved encounter file and verifying generated loot matches the encounter's effective CR.

**Acceptance Scenarios**:

1. **Given** a saved encounter file in `campaign/encounters/`, **When** I request loot for that encounter, **Then** the system reads the encounter CR and generates a hoard
2. **Given** an encounter with multiple creatures, **When** determining CR, **Then** the system uses the highest individual CR or calculates effective CR from XP
3. **Given** a `--individual` flag, **When** generating encounter loot, **Then** the system generates individual treasure for each creature instead of a hoard
4. **Given** a non-existent encounter file, **When** I request loot, **Then** the system displays a clear error message

---

### User Story 5 - Save Loot to Session (Priority: P5)

As a DM, I want to append generated loot to a session's "Loot & Rewards" section so that I can track what treasure the party has acquired.

**Why this priority**: Integrates with session tracking for campaign continuity. Lower priority as it's an enhancement to existing session workflow.

**Independent Test**: Can be fully tested by generating loot with a session flag and verifying the session file is updated with the treasure.

**Acceptance Scenarios**:

1. **Given** a valid session number, **When** I generate loot with `--add-to-session N`, **Then** the loot is appended to session-NNN.md's "Loot & Rewards" section
2. **Given** a session file without a "Loot & Rewards" section, **When** appending loot, **Then** the section is created before the loot is added
3. **Given** a non-existent session number, **When** I attempt to add loot, **Then** the system displays a clear error message
4. **Given** previously appended loot in a session, **When** I add more loot, **Then** the new loot is appended below existing loot entries

---

### Edge Cases

- What happens when a magic item from the table doesn't exist in reference data?
  - System outputs the item name without a link and notes "[No Reference]"
- What happens when the user specifies an invalid CR (negative or non-numeric)?
  - System displays an error message explaining valid CR formats (0-30, or fractions like 1/2, 1/4, 1/8)
- What happens when an encounter file has no CR information?
  - System calculates CR from total XP using the standard CR/XP mapping, or prompts user to specify CR
- What happens when gems/art objects are rolled but specific item names aren't available?
  - System outputs generic descriptions (e.g., "10 gp gem" or "25 gp art object") with a note to choose specific items
- How are fractional CRs handled?
  - CR 1/8, 1/4, and 1/2 are treated as CR 0-4 tier for treasure purposes
- What happens when `--seed` is used with multiple dice rolls?
  - The seed initializes the random state once, ensuring all subsequent rolls are deterministic

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate individual treasure based on DMG 2024 CR-based tables
- **FR-002**: System MUST generate treasure hoards with coins, gems, art objects, and magic items based on DMG 2024 CR-based tables
- **FR-003**: System MUST support rolling on specific magic item tables (A through I)
- **FR-004**: System MUST link generated magic items to reference files in `books/reference/items/` when available
- **FR-005**: System MUST support a `--seed` flag for deterministic, reproducible output
- **FR-006**: System MUST support a `--count N` flag for generating multiple treasure rolls
- **FR-007**: System MUST read saved encounter files and determine appropriate CR for loot generation
- **FR-008**: System MUST append generated loot to session files in the "Loot & Rewards" section
- **FR-009**: System MUST output treasure in a consistent, readable markdown format
- **FR-010**: System MUST support all four CR tiers: 0-4, 5-10, 11-16, 17+
- **FR-011**: System MUST handle fractional CRs (1/8, 1/4, 1/2) as CR 0-4 tier
- **FR-012**: System MUST provide clear error messages for invalid inputs

### Key Entities

- **Treasure**: Generated loot containing coins, gems, art objects, and/or magic items
- **Coin**: Currency in cp, sp, ep, gp, or pp with amount
- **Gem**: Precious stone with gp value and optional specific name
- **ArtObject**: Valuable artwork or jewelry with gp value and optional description
- **MagicItem**: Reference to an item in the magic item database with rarity and type

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate individual treasure in under 1 second
- **SC-002**: Users can generate a complete treasure hoard in under 2 seconds
- **SC-003**: Generated hoards match DMG 2024 table distributions when sampled over 1000+ rolls
- **SC-004**: 90% of generated magic items successfully link to reference files
- **SC-005**: All generated markdown is human-readable and properly formatted
- **SC-006**: Deterministic mode produces identical output for the same seed value
- **SC-007**: Encounter-based loot correctly determines CR tier from encounter files

## Assumptions

- DMG 2024 treasure tables are embedded in the code (not loaded from external files)
- Reference item data exists in `books/reference/items/` from prior extraction
- Users interact with the system through command-line interface
- Session files follow the established format from session_manager.py
- Encounter files follow the established format from encounter_builder.py

## Dependencies

- `books/reference/items/` directory with extracted magic item files
- `books/reference-index.json` for item name-to-path lookups
- `scripts/lib/reference_linker.py` for linking items to references
- `scripts/lib/markdown_writer.py` for consistent markdown formatting
- `campaign/` directory structure (for session integration)
