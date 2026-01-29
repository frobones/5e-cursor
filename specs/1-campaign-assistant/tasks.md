# Tasks: Campaign Assistant

**Input**: Design documents from `/specs/1-campaign-assistant/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md

**Tests**: Tests are included as the project follows pytest conventions per user preferences.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `scripts/lib/` directory structure
- [ ] T002 Create `scripts/campaign/` directory structure
- [ ] T003 [P] Create `scripts/lib/__init__.py` with module docstring
- [ ] T004 [P] Create `scripts/campaign/__init__.py` with module docstring
- [ ] T005 [P] Create `tests/` directory structure for campaign tests
- [ ] T006 [P] Create `tests/fixtures/` directory for test data
- [ ] T007 Add `requests` to requirements.txt if not present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Implement `scripts/lib/markdown_writer.py` with functions for consistent markdown output (headings, tables, links)
- [ ] T009 Implement `scripts/lib/reference_linker.py` to load `books/reference-index.json` and resolve name-to-path lookups
- [ ] T010 [P] Create `tests/fixtures/dndbeyond_sample.json` with sample D&D Beyond API response (from Meilin character)
- [ ] T011 [P] Create `tests/fixtures/reference_index_sample.json` with subset of reference index for testing
- [ ] T012 Create campaign initialization script `scripts/campaign/init_campaign.py` to create directory structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import Character from D&D Beyond (Priority: P1) 🎯 MVP

**Goal**: Import player characters from D&D Beyond with full stats and auto-linked reference data

**Independent Test**: Provide a D&D Beyond character URL and verify a complete markdown character sheet is created with working links to reference data

### Tests for User Story 1

- [ ] T013 [P] [US1] Create `tests/test_dndbeyond_client.py` with tests for URL parsing and API fetching
- [ ] T014 [P] [US1] Create `tests/test_import_character.py` with tests for JSON-to-markdown conversion

### Implementation for User Story 1

- [ ] T015 [US1] Implement `scripts/lib/dndbeyond_client.py` with `fetch_character(url)` function
- [ ] T016 [US1] Implement character data parser in `scripts/lib/dndbeyond_client.py` to extract stats, class, features, inventory from JSON
- [ ] T017 [US1] Implement `scripts/campaign/import_character.py` CLI script with URL argument
- [ ] T018 [US1] Add character sheet template generation using `markdown_writer` (ability scores table, combat stats, proficiencies)
- [ ] T019 [US1] Add class feature extraction with reference links using `reference_linker`
- [ ] T020 [US1] Add feat extraction with reference links
- [ ] T021 [US1] Add spell extraction with reference links (if character has spells)
- [ ] T022 [US1] Add equipment extraction with reference links
- [ ] T023 [US1] Add personality traits, appearance, and notes sections
- [ ] T024 [US1] Add party index update logic in `scripts/campaign/import_character.py`
- [ ] T025 [US1] Add error handling for private characters, invalid URLs, network failures

**Checkpoint**: User Story 1 complete - can import D&D Beyond characters with linked reference data

---

## Phase 4: User Story 2 - Build Balanced Encounters (Priority: P2)

**Goal**: Generate balanced encounters using DMG XP thresholds based on party composition

**Independent Test**: Specify party level, size, and difficulty, verify generated encounter meets DMG XP thresholds

### Tests for User Story 2

- [ ] T026 [P] [US2] Create `tests/test_encounter_builder.py` with tests for XP calculation and creature selection

### Implementation for User Story 2

- [ ] T027 [US2] Implement DMG XP threshold tables in `scripts/campaign/encounter_builder.py`
- [ ] T028 [US2] Implement encounter multiplier calculation based on creature count
- [ ] T029 [US2] Implement creature loader from `books/reference/creatures/` with CR parsing
- [ ] T030 [US2] Implement creature filtering by type, environment, CR range
- [ ] T031 [US2] Implement encounter generation algorithm (select creatures to match target XP)
- [ ] T032 [US2] Implement encounter markdown output with creature links and XP breakdown
- [ ] T033 [US2] Add CLI interface with `--level`, `--size`, `--difficulty`, `--type`, `--save` options
- [ ] T034 [US2] Add encounter index update when saving encounters
- [ ] T035 [US2] Add party state reading from `campaign/party/index.md` for auto-detection of level/size

**Checkpoint**: User Story 2 complete - can generate balanced encounters with creature links

---

## Phase 5: User Story 3 - Answer Rules Questions with Citations (Priority: P3)

**Goal**: Provide rules answers with inline-quoted text and source citations

**Independent Test**: Ask a rules question and verify response includes inline quotes from extracted rules files

### Tests for User Story 3

- [ ] T036 [P] [US3] Create `tests/test_rules_engine.py` with tests for keyword extraction and rules lookup

### Implementation for User Story 3

- [ ] T037 [US3] Implement keyword extraction in `scripts/campaign/rules_engine.py` (conditions, spell names, rules terms)
- [ ] T038 [US3] Implement reference index search for matching entries
- [ ] T039 [US3] Implement markdown file section extraction (parse headings, extract relevant blocks)
- [ ] T040 [US3] Implement response formatter with inline quotes and source citations
- [ ] T041 [US3] Add CLI interface for rules queries
- [ ] T042 [US3] Add fuzzy matching for slight name variations

**Checkpoint**: User Story 3 complete - can answer rules questions with citations

---

## Phase 6: User Story 4 - Track Session History (Priority: P4)

**Goal**: Record session summaries with sequential numbering and dates

**Independent Test**: Create a session summary and verify it appears in session log with proper numbering

### Tests for User Story 4

- [ ] T043 [P] [US4] Create `tests/test_session_manager.py` with tests for session creation and indexing

### Implementation for User Story 4

- [ ] T044 [US4] Implement session number detection in `scripts/campaign/session_manager.py` (find next available number)
- [ ] T045 [US4] Implement session template generation with date, number, title, empty summary
- [ ] T046 [US4] Implement session index update with chronological listing
- [ ] T047 [US4] Add CLI interface with `new`, `list` subcommands
- [ ] T048 [US4] Add NPC/location linking in session summaries (optional enhancement)

**Checkpoint**: User Story 4 complete - can create and track session summaries

---

## Phase 7: User Story 5 - Manage Campaign State (Priority: P5)

**Goal**: Create and organize NPCs, locations, and campaign notes

**Independent Test**: Create an NPC or location and verify proper file placement and index updates

### Implementation for User Story 5

- [ ] T049 [US5] Implement NPC creation in `scripts/campaign/campaign_manager.py` with name, description, role fields
- [ ] T050 [US5] Implement location creation with name, description, type, connections fields
- [ ] T051 [US5] Implement index update logic for NPCs and locations
- [ ] T052 [US5] Add CLI interface for NPC/location management (`add-npc`, `add-location`, `list-npcs`, `list-locations`)
- [ ] T053 [US5] Implement campaign.md initialization with campaign metadata

**Checkpoint**: User Story 5 complete - can manage NPCs, locations, and campaign state

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T054 [P] Update `README.md` with Campaign Assistant feature documentation
- [ ] T055 [P] Add campaign commands to `Makefile` (e.g., `make campaign-init`, `make import-character`)
- [ ] T056 [P] Create `.cursor/rules/campaign-lookup.mdc` for Cursor AI campaign data navigation
- [ ] T057 Run all tests and fix any failures
- [ ] T058 Validate quickstart.md scenarios work end-to-end
- [ ] T059 [P] Add `campaign/` to `.gitignore` with comment explaining it's user data (optional - may want to track)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4 → P5)
- **Polish (Phase 8)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational - Uses reference_linker from Foundation
- **User Story 3 (P3)**: Can start after Foundational - Uses reference_linker from Foundation
- **User Story 4 (P4)**: Can start after Foundational - Uses markdown_writer from Foundation
- **User Story 5 (P5)**: Can start after Foundational - Uses markdown_writer from Foundation

### Within Each User Story

- Tests written first (should fail initially)
- Core logic before CLI interface
- Index updates after primary functionality

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- All test creation tasks marked [P] can run in parallel
- Once Foundational completes, all user stories can start in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch tests in parallel:
Task: "Create tests/test_dndbeyond_client.py"
Task: "Create tests/test_import_character.py"

# After tests exist, implementation is mostly sequential due to dependencies
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Import a real D&D Beyond character, verify output
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test with real character → MVP!
3. Add User Story 2 → Generate encounters for imported party
4. Add User Story 3 → Answer rules questions during play
5. Add User Story 4 → Track sessions
6. Add User Story 5 → Manage NPCs/locations

### Parallel Team Strategy

With multiple developers:
1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (character import)
   - Developer B: User Story 2 (encounters)
   - Developer C: User Story 3 (rules)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
