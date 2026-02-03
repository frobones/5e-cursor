# Tasks: Encounter Builder and Combat Tracker

**Input**: Design documents from `/specs/009-encounter-builder/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests not explicitly requested in the specification. Backend tests added for critical combat state logic.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Frontend**: `frontend/src/`
- **Backend**: `scripts/web/`
- Paths follow existing web application structure from Spec 8

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new directories and foundational files for encounter/combat features

- [ ] T001 Create encounter components directory at frontend/src/components/encounter/index.ts
- [ ] T002 [P] Create combat components directory at frontend/src/components/combat/index.ts
- [ ] T003 [P] Create utils directory structure at frontend/src/utils/ (if not exists)
- [ ] T004 Add TypeScript types for Encounter, Combatant, CombatState, DamageEvent in frontend/src/types/index.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities and backend models that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create encounterCalculator.ts with XP_THRESHOLDS, CR_XP, ENCOUNTER_MULTIPLIERS tables in frontend/src/utils/encounterCalculator.ts
- [ ] T006 Implement getPartyThresholds(), getEncounterMultiplier(), calculateDifficulty() functions in frontend/src/utils/encounterCalculator.ts
- [ ] T007 [P] Create Pydantic models for EncounterCreate, EncounterUpdate in scripts/web/models/entities.py
- [ ] T008 [P] Create Pydantic models for Combatant, DamageEvent, CombatState, CombatCreate, CombatAction in scripts/web/models/combat.py
- [ ] T009 Add encounter create/update methods to EntityService in scripts/web/services/entities.py
- [ ] T010 [P] Create CombatService with load/save/update methods in scripts/web/services/combat.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Build New Encounter (Priority: P1) MVP

**Goal**: DMs can browse creatures, add them to an encounter, see difficulty calculations, and save the encounter

**Independent Test**: Open encounter builder, search "goblin", add creatures, adjust quantities, see difficulty update, enter name, save - encounter appears in list

### Implementation for User Story 1

- [ ] T011 [US1] Create CreatureSelector component with search input and CR filter in frontend/src/components/encounter/CreatureSelector.tsx
- [ ] T012 [P] [US1] Create EncounterPanel component showing creature list with quantity controls in frontend/src/components/encounter/EncounterPanel.tsx
- [ ] T013 [US1] Create DifficultyDisplay component showing difficulty badge and XP breakdown in frontend/src/components/encounter/DifficultyDisplay.tsx
- [ ] T014 [US1] Create EncounterBuilder page integrating CreatureSelector, EncounterPanel, DifficultyDisplay in frontend/src/pages/EncounterBuilder.tsx
- [ ] T015 [US1] Add party configuration inputs (level, size) with campaign auto-population in frontend/src/pages/EncounterBuilder.tsx
- [ ] T016 [US1] Add encounter name input and Save button with validation in frontend/src/pages/EncounterBuilder.tsx
- [ ] T017 [US1] Add POST /api/encounters endpoint for creating new encounters in scripts/web/api/entities.py
- [ ] T018 [US1] Add createEncounter(), updateEncounter() API functions in frontend/src/services/api.ts
- [ ] T019 [US1] Add route for /encounters/new pointing to EncounterBuilder in frontend/src/App.tsx
- [ ] T020 [US1] Add "Build New Encounter" button to Encounters list page in frontend/src/pages/Encounters.tsx
- [ ] T021 [US1] Update encounter components barrel export in frontend/src/components/encounter/index.ts
- [ ] T022 [US1] Add EncounterBuilder to pages barrel export in frontend/src/pages/index.ts

**Checkpoint**: User Story 1 complete - DMs can build and save new encounters with difficulty calculation

---

## Phase 4: User Story 2 - Load and Edit Existing Encounter (Priority: P2)

**Goal**: DMs can open an existing encounter in the builder, modify it, and save changes

**Independent Test**: Navigate to existing encounter, click "Edit", see creatures pre-populated, add/remove creatures, save - changes persist

### Implementation for User Story 2

- [ ] T023 [US2] Add PUT /api/encounters/{slug} endpoint for updating encounters in scripts/web/api/entities.py
- [ ] T024 [US2] Add "Edit" button to EncounterDetail page linking to builder with slug param in frontend/src/pages/EncounterDetail.tsx
- [ ] T025 [US2] Add route for /encounters/:slug/edit pointing to EncounterBuilder in frontend/src/App.tsx
- [ ] T026 [US2] Add useEffect to load existing encounter data when slug param present in frontend/src/pages/EncounterBuilder.tsx
- [ ] T027 [US2] Modify save logic to use PUT when editing vs POST when creating in frontend/src/pages/EncounterBuilder.tsx

**Checkpoint**: User Story 2 complete - DMs can edit existing encounters

---

## Phase 5: User Story 3 - Start Combat from Encounter (Priority: P3)

**Goal**: DMs can start combat from a saved encounter with initiative tracking

**Independent Test**: Open encounter, click "Start Combat", see combatants listed, enter initiative values, see sorted initiative order

### Implementation for User Story 3

- [ ] T028 [US3] Create combatState.ts utility with expandCreatures(), rollInitiative(), sortByInitiative() in frontend/src/utils/combatState.ts
- [ ] T029 [US3] Create InitiativeList component showing sorted combatants with initiative in frontend/src/components/combat/InitiativeList.tsx
- [ ] T030 [P] [US3] Create CombatantCard component with name, initiative, HP display in frontend/src/components/combat/CombatantCard.tsx
- [ ] T031 [US3] Create InitiativeSetup component for entering/rolling initiative values in frontend/src/components/combat/InitiativeSetup.tsx
- [ ] T032 [US3] Create EncounterRunner page with combat initialization flow in frontend/src/pages/EncounterRunner.tsx
- [ ] T033 [US3] Add POST /api/combat/{slug} endpoint to start combat from encounter in scripts/web/api/combat.py
- [ ] T034 [US3] Register combat router in FastAPI main app in scripts/web/main.py
- [ ] T035 [US3] Add startCombat(), getCombat() API functions in frontend/src/services/api.ts
- [ ] T036 [US3] Add "Start Combat" button to EncounterDetail page in frontend/src/pages/EncounterDetail.tsx
- [ ] T037 [US3] Add route for /encounters/:slug/combat pointing to EncounterRunner in frontend/src/App.tsx
- [ ] T038 [US3] Add EncounterRunner to pages barrel export in frontend/src/pages/index.ts
- [ ] T039 [US3] Update combat components barrel export in frontend/src/components/combat/index.ts

**Checkpoint**: User Story 3 complete - DMs can start combat and set initiative

---

## Phase 6: User Story 4 - Track Combat with HP and Damage (Priority: P3)

**Goal**: DMs can apply damage/healing, track HP, and advance turns through initiative order

**Independent Test**: Run combat, click combatant, apply damage, see HP decrease, click "Next Turn", see turn indicator advance

### Implementation for User Story 4

- [ ] T040 [US4] Create CombatTracker component with damage/healing/temp HP input controls in frontend/src/components/combat/CombatTracker.tsx
- [ ] T041 [US4] Add HP tracking display (current/max/temp) to CombatantCard in frontend/src/components/combat/CombatantCard.tsx
- [ ] T042 [US4] Add condition toggle badges (Stunned, Poisoned, Prone, etc.) to CombatantCard in frontend/src/components/combat/CombatantCard.tsx
- [ ] T043 [US4] Add applyDamage(), applyHealing(), addTempHP() functions to combatState.ts in frontend/src/utils/combatState.ts
- [ ] T044 [US4] Add nextTurn(), previousTurn(), getCurrentCombatant() functions to combatState.ts in frontend/src/utils/combatState.ts
- [ ] T045 [US4] Add round counter and current turn indicator to EncounterRunner in frontend/src/pages/EncounterRunner.tsx
- [ ] T046 [US4] Add Next Turn / Previous Turn buttons to EncounterRunner in frontend/src/pages/EncounterRunner.tsx
- [ ] T047 [US4] Add defeated visual state (0 HP) styling to CombatantCard in frontend/src/components/combat/CombatantCard.tsx
- [ ] T048 [US4] Add PUT /api/combat/{slug} endpoint to update combat state in scripts/web/api/combat.py
- [ ] T049 [US4] Add updateCombat() API function in frontend/src/services/api.ts
- [ ] T050 [US4] Implement auto-save on state changes with debounce in frontend/src/pages/EncounterRunner.tsx

**Checkpoint**: User Story 4 complete - DMs can track HP, apply damage, and run through combat turns

---

## Phase 7: User Story 5 - View Damage History (Priority: P4)

**Goal**: DMs can see a chronological log of all damage and healing events grouped by round

**Independent Test**: Run combat, apply damage/healing to multiple combatants, view damage history panel showing events grouped by round

### Implementation for User Story 5

- [ ] T051 [US5] Create DamageHistory component showing events grouped by round in frontend/src/components/combat/DamageHistory.tsx
- [ ] T052 [US5] Add logDamageEvent() function to combatState.ts to record events in frontend/src/utils/combatState.ts
- [ ] T053 [US5] Integrate DamageHistory panel into EncounterRunner layout in frontend/src/pages/EncounterRunner.tsx
- [ ] T054 [US5] Add damage source input field to CombatTracker component in frontend/src/components/combat/CombatTracker.tsx

**Checkpoint**: User Story 5 complete - DMs can review damage history during/after combat

---

## Phase 8: User Story 6 - Resume Combat After Interruption (Priority: P4)

**Goal**: Combat state persists to file and can be resumed after browser close/reopen

**Independent Test**: Run combat, apply some damage, close browser, reopen, navigate to encounter, click "Resume Combat", verify state preserved

### Implementation for User Story 6

- [ ] T055 [US6] Add GET /api/combat/{slug} endpoint to retrieve existing combat state in scripts/web/api/combat.py
- [ ] T056 [US6] Add DELETE /api/combat/{slug} endpoint to end/archive combat in scripts/web/api/combat.py
- [ ] T057 [US6] Add combat state check to EncounterDetail to show "Resume Combat" vs "Start Combat" in frontend/src/pages/EncounterDetail.tsx
- [ ] T058 [US6] Add combat resume logic to EncounterRunner (load existing state if present) in frontend/src/pages/EncounterRunner.tsx
- [ ] T059 [US6] Add "Resume Combat" indicator badge to Encounters list for active combats in frontend/src/pages/Encounters.tsx
- [ ] T060 [US6] Add "End Combat" button and confirmation to EncounterRunner in frontend/src/pages/EncounterRunner.tsx
- [ ] T061 [US6] Add endCombat() API function in frontend/src/services/api.ts

**Checkpoint**: User Story 6 complete - Combat can be resumed across browser sessions

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T062 [P] Add loading states and error handling to EncounterBuilder in frontend/src/pages/EncounterBuilder.tsx
- [ ] T063 [P] Add loading states and error handling to EncounterRunner in frontend/src/pages/EncounterRunner.tsx
- [ ] T064 [P] Add keyboard shortcuts for common combat actions (damage, next turn) in frontend/src/pages/EncounterRunner.tsx
- [ ] T065 Add pytest tests for CombatService file operations in tests/test_combat_service.py
- [ ] T066 Run quickstart.md validation - verify all documented workflows work

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories (MVP)
- **User Story 2 (P2)**: Soft dependency on US1 (needs encounters to exist to edit)
- **User Story 3 (P3)**: Soft dependency on US1 (needs encounters to exist to start combat)
- **User Story 4 (P3)**: Depends on US3 (combat must be started before tracking)
- **User Story 5 (P4)**: Depends on US4 (damage events must be applied to have history)
- **User Story 6 (P4)**: Depends on US3+US4 (combat infrastructure must exist)

### Within Each User Story

- Frontend components before pages
- Backend models before services before API routes
- Utility functions before components that use them

### Parallel Opportunities

- T001-T003: All setup directories can be created in parallel
- T007-T010: Backend models and services can be built in parallel
- T011-T012: CreatureSelector and EncounterPanel components can be built in parallel
- T029-T030: InitiativeList and CombatantCard can be built in parallel
- T062-T064: All polish tasks can run in parallel

---

## Parallel Example: Phase 2 Foundational

```text
# These can run in parallel:
Task: T007 - Create Pydantic models for EncounterCreate in scripts/web/models/entities.py
Task: T008 - Create Pydantic models for Combatant, CombatState in scripts/web/models/combat.py
Task: T010 - Create CombatService in scripts/web/services/combat.py

# Then sequentially:
Task: T009 - Add methods to EntityService (depends on T007)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Build encounter, save, verify in list
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → MVP! DMs can build/save encounters
3. Add User Story 2 → DMs can edit encounters
4. Add User Stories 3+4 → DMs can run combat (major milestone)
5. Add User Story 5 → Damage history for review
6. Add User Story 6 → Full resume capability

### Task Summary

| Phase | Tasks | Description |
| ----- | ----- | ----------- |
| Phase 1 | T001-T004 | Setup (4 tasks) |
| Phase 2 | T005-T010 | Foundational (6 tasks) |
| Phase 3 | T011-T022 | US1 - Build Encounter (12 tasks) |
| Phase 4 | T023-T027 | US2 - Edit Encounter (5 tasks) |
| Phase 5 | T028-T039 | US3 - Start Combat (12 tasks) |
| Phase 6 | T040-T050 | US4 - Track Combat (11 tasks) |
| Phase 7 | T051-T054 | US5 - Damage History (4 tasks) |
| Phase 8 | T055-T061 | US6 - Resume Combat (7 tasks) |
| Phase 9 | T062-T066 | Polish (5 tasks) |

**Total**: 66 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- US3 and US4 are both P3 and work together - implement them sequentially
