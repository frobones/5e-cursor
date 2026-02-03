# Feature Specification: Encounter Builder and Combat Tracker

**Feature Branch**: `009-encounter-builder`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: User description: "Create an encounter builder and combat tracker for the web UI. The encounter builder allows users to browse creatures, add them to an encounter, configure party settings, see real-time difficulty calculations, save encounters, and load existing encounters for editing. The combat runner allows users to run encounters with initiative tracking, party members from campaign data, HP/temp HP management, damage/healing input, condition tracking, and a damage history log. Combat state persists to JSON files for resume capability."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build New Encounter (Priority: P1)

As a DM, I want to build balanced encounters by browsing creatures and adding them to an encounter list, so that I can prepare combat scenarios with appropriate difficulty for my party.

**Why this priority**: This is the core functionality that enables all other features. Without the ability to build encounters, the combat runner has nothing to run.

**Independent Test**: Can be fully tested by opening the encounter builder, searching for creatures, adding them with quantities, viewing difficulty calculations, and saving the encounter. Delivers immediate value for encounter preparation.

**Acceptance Scenarios**:

1. **Given** I am on the encounters page, **When** I click "Build New Encounter", **Then** I see the encounter builder with creature search and party configuration
2. **Given** I am in the encounter builder, **When** I search for "goblin" and click a result, **Then** that creature is added to my encounter list with quantity 1
3. **Given** I have creatures in my encounter, **When** I adjust quantities with +/- controls, **Then** the difficulty recalculates in real-time
4. **Given** I have a valid encounter, **When** I enter a name and click Save, **Then** the encounter is saved and I am redirected to the encounter detail page

---

### User Story 2 - Load and Edit Existing Encounter (Priority: P2)

As a DM, I want to load a previously saved encounter into the builder, so that I can modify it for reuse or adjustment.

**Why this priority**: Editing encounters is essential for iterative preparation and reusing encounter templates, but requires P1 to create encounters first.

**Independent Test**: Can be tested by navigating to an existing encounter, clicking "Edit", modifying creatures, and saving. Delivers value by enabling encounter iteration.

**Acceptance Scenarios**:

1. **Given** I am viewing an encounter detail, **When** I click "Edit", **Then** the encounter opens in the builder with all creatures pre-populated
2. **Given** I am in the builder with a loaded encounter, **When** I add or remove creatures and save, **Then** the existing encounter file is updated

---

### User Story 3 - Start Combat from Encounter (Priority: P3)

As a DM, I want to start a combat session from a saved encounter, so that I can run the encounter with my party during a game session.

**Why this priority**: This bridges encounter building with combat tracking. Requires encounters to exist first.

**Independent Test**: Can be tested by opening an encounter, clicking "Start Combat", entering initiative values, and seeing the combat tracker display. Delivers the core combat running capability.

**Acceptance Scenarios**:

1. **Given** I am viewing an encounter detail, **When** I click "Start Combat", **Then** I am taken to the combat runner with all creatures and party members ready
2. **Given** I am starting combat, **When** monsters roll initiative and I enter player initiatives, **Then** all combatants are sorted by initiative order

---

### User Story 4 - Track Combat with HP and Damage (Priority: P3)

As a DM, I want to track HP, apply damage/healing, and advance turns during combat, so that I can run the encounter smoothly without manual bookkeeping.

**Why this priority**: Core combat tracking functionality that makes the runner useful. Same priority as starting combat since they work together.

**Independent Test**: Can be tested by running a combat, selecting a combatant, applying damage, seeing HP update, and advancing turns. Delivers the primary combat management value.

**Acceptance Scenarios**:

1. **Given** combat is active, **When** I select a combatant and enter damage, **Then** their current HP decreases and the damage is logged
2. **Given** combat is active, **When** I apply healing to a combatant, **Then** their HP increases (not exceeding max HP)
3. **Given** combat is active, **When** I click "Next Turn", **Then** the next combatant in initiative order is highlighted
4. **Given** a combatant reaches 0 HP, **When** viewing the initiative list, **Then** they are visually marked as defeated

---

### User Story 5 - View Damage History (Priority: P4)

As a DM, I want to see a history of all damage and healing during combat, so that I can review what happened and catch any mistakes.

**Why this priority**: Nice-to-have that enhances the combat experience but is not strictly required for basic combat tracking.

**Independent Test**: Can be tested by running combat, applying several damage/healing events, and viewing the damage history log grouped by round.

**Acceptance Scenarios**:

1. **Given** combat has damage events, **When** I view the damage history, **Then** I see events grouped by round with combatant name, amount, and optional source
2. **Given** multiple rounds of combat, **When** I scroll through history, **Then** I can see the full progression of the battle

---

### User Story 6 - Resume Combat After Interruption (Priority: P4)

As a DM, I want combat state to persist so I can close the browser and resume later, so that I can handle interruptions without losing progress.

**Why this priority**: Important for real-world use but combat can function without it for single-session encounters.

**Independent Test**: Can be tested by running combat, closing the browser, reopening, and verifying all combatant HP and turn state is preserved.

**Acceptance Scenarios**:

1. **Given** I am in active combat, **When** I close and reopen the browser, **Then** the combat resumes at the exact state I left
2. **Given** an encounter has active combat, **When** I view the encounters list, **Then** I see a "Resume Combat" indicator on that encounter

---

### Edge Cases

- What happens when all monsters are defeated? Combat should be marked complete and prompt to end.
- What happens if party data is unavailable? Allow manual entry of player combatants.
- How does the system handle ties in initiative? Maintain stable sort order, allow manual reordering.
- What happens if a creature has 0 max HP in reference data? Use a sensible default (10 HP) and warn the user.
- Can users undo damage? Not in initial version - damage history serves as audit trail for manual correction.

## Requirements *(mandatory)*

### Functional Requirements

**Encounter Builder**

- **FR-001**: System MUST display a searchable, filterable list of creatures from reference data
- **FR-002**: System MUST allow filtering creatures by Challenge Rating range
- **FR-003**: System MUST allow adding creatures to an encounter with quantity controls
- **FR-004**: System MUST calculate encounter difficulty (Easy/Medium/Hard/Deadly) in real-time using DMG rules
- **FR-005**: System MUST display XP totals (base XP, multiplier, adjusted XP) and party thresholds
- **FR-006**: System MUST allow configuring party level and size (auto-populated from campaign if available)
- **FR-007**: System MUST allow saving encounters with a user-provided name
- **FR-008**: System MUST allow loading existing encounters into the builder for editing

**Combat Runner**

- **FR-009**: System MUST expand encounter creatures into individual combatant instances (e.g., "3 Goblins" becomes "Goblin 1", "Goblin 2", "Goblin 3")
- **FR-010**: System MUST load party members from campaign data with their HP values
- **FR-011**: System MUST track initiative for all combatants and sort by initiative order
- **FR-012**: System MUST allow rolling initiative for monsters (random) and entering initiative for players (manual)
- **FR-013**: System MUST track current HP, max HP, and temporary HP for each combatant
- **FR-014**: System MUST allow applying damage (reduces HP) and healing (increases HP, capped at max)
- **FR-015**: System MUST allow adding temporary HP
- **FR-016**: System MUST track and display common conditions (Stunned, Poisoned, Prone, etc.)
- **FR-017**: System MUST advance turns through the initiative order with Next/Previous controls
- **FR-018**: System MUST display round count and current turn indicator
- **FR-019**: System MUST log all damage and healing events with round, turn, target, amount, and optional source
- **FR-020**: System MUST display damage history grouped by round
- **FR-021**: System MUST persist combat state to a file for resume capability
- **FR-022**: System MUST allow ending/completing combat and archiving the log

### Key Entities

- **Encounter**: A saved encounter configuration with name, party info, difficulty, and list of creature entries (creature + quantity)
- **Combatant**: An individual participant in combat (monster instance or player character) with initiative, HP tracking, and conditions
- **CombatState**: The full state of an active combat including round, turn index, all combatants, and damage log
- **DamageEvent**: A single damage or healing event with round, turn, target, amount, type, and optional source

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: DMs can build a new encounter and calculate difficulty in under 2 minutes
- **SC-002**: DMs can start combat from an encounter in under 30 seconds
- **SC-003**: Applying damage and advancing turns takes under 5 seconds per action
- **SC-004**: Combat state persists correctly across browser sessions (100% state fidelity)
- **SC-005**: The system correctly calculates difficulty using DMG encounter multiplier rules
- **SC-006**: All combatants display accurate HP throughout combat (no calculation errors)
- **SC-007**: Damage history accurately reflects all events that occurred during combat

## Assumptions

- The existing web UI infrastructure (React frontend, FastAPI backend) is stable and available
- Creature reference data includes CR values in the reference index
- Party character data includes HP values when imported from D&D Beyond
- Users have a modern browser with JavaScript enabled
- Combat runs locally (no multiplayer/network sync required)

## Dependencies

- Spec 8 (Campaign Web UI) must be substantially complete - provides the base infrastructure
- Reference data extraction must include creature CR values
- Party character import must include HP values
