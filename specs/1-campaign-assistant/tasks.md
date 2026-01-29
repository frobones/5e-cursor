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

- [x] T001 Create `scripts/lib/` directory structure
- [x] T002 Create `scripts/campaign/` directory structure
- [x] T003 [P] Create `scripts/lib/__init__.py` with module docstring
- [x] T004 [P] Create `scripts/campaign/__init__.py` with module docstring
- [x] T005 [P] Create `tests/` directory structure for campaign tests
- [x] T006 [P] Create `tests/fixtures/` directory for test data
- [x] T007 Add `requests` to requirements.txt if not present

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**✅ COMPLETE**: Foundation ready - all user stories can proceed

- [x] T008 Implement `scripts/lib/markdown_writer.py` with functions for consistent markdown output (headings, tables, links)
- [x] T009 Implement `scripts/lib/reference_linker.py` to load `books/reference-index.json` and resolve name-to-path lookups
- [x] T010 [P] Create `tests/fixtures/dndbeyond_sample.json` with sample D&D Beyond API response (from Meilin character)
- [x] T011 [P] Create `tests/fixtures/reference_index_sample.json` with subset of reference index for testing
- [x] T012 Create campaign initialization script `scripts/campaign/init_campaign.py` to create directory structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Import Character from D&D Beyond (Priority: P1) 🎯 MVP

**Goal**: Import player characters from D&D Beyond with full stats and auto-linked reference data

**✅ COMPLETE**: Character import functional with all tests passing

### Tests for User Story 1

- [x] T013 [P] [US1] Create `tests/test_dndbeyond_client.py` with tests for URL parsing and API fetching
- [x] T014 [P] [US1] Create `tests/test_import_character.py` with tests for JSON-to-markdown conversion

### Implementation for User Story 1

- [x] T015 [US1] Implement `scripts/lib/dndbeyond_client.py` with `fetch_character(url)` function
- [x] T016 [US1] Implement character data parser in `scripts/lib/dndbeyond_client.py` to extract stats, class, features, inventory from JSON
- [x] T017 [US1] Implement `scripts/campaign/import_character.py` CLI script with URL argument
- [x] T018 [US1] Add character sheet template generation using `markdown_writer` (ability scores table, combat stats, proficiencies)
- [x] T019 [US1] Add class feature extraction with reference links using `reference_linker`
- [x] T020 [US1] Add feat extraction with reference links
- [x] T021 [US1] Add spell extraction with reference links (if character has spells)
- [x] T022 [US1] Add equipment extraction with reference links
- [x] T023 [US1] Add personality traits, appearance, and notes sections
- [x] T024 [US1] Add party index update logic in `scripts/campaign/import_character.py`
- [x] T025 [US1] Add error handling for private characters, invalid URLs, network failures

**Checkpoint**: User Story 1 complete - can import D&D Beyond characters with linked reference data

---

## Phase 3b: User Story 1 Extension - Character Update Command

**Goal**: Track imported characters and enable batch refresh from D&D Beyond

**Status**: ✅ COMPLETE

### Tests for Character Update

- [x] T067 [P] [US1] Add tests for `extract_dndbeyond_id_from_file()` to `tests/test_import_character.py`
- [x] T068 [P] [US1] Add tests for `list_imported_characters()` to `tests/test_import_character.py`
- [x] T069 [P] [US1] Add tests for `update_character()` to `tests/test_import_character.py`

### Implementation for Character Update

- [x] T070 [US1] Add "Last updated" metadata line to character markdown footer in `generate_character_markdown()`
- [x] T071 [US1] Implement `extract_dndbeyond_id_from_file(path)` to parse source URL from markdown
- [x] T072 [US1] Implement `list_imported_characters(party_dir)` to enumerate characters with D&D Beyond IDs
- [x] T073 [US1] Implement `update_character(path, linker)` to refetch and regenerate a single character
- [x] T074 [US1] Implement `update_all_characters(party_dir, linker)` for batch updates
- [x] T075 [US1] Refactor CLI to use subcommands: `import`, `update`, `list`
- [x] T076 [US1] Add `--all` flag to update subcommand for batch refresh
- [x] T077 [US1] Add `--dry-run` flag to preview which characters would be updated

**Checkpoint**: Character update complete - can refresh imported characters from D&D Beyond

---

## Phase 4: User Story 2 - Build Balanced Encounters (Priority: P2)

**Goal**: Generate balanced encounters using DMG XP thresholds based on party composition

**✅ COMPLETE**: Encounter builder functional with all tests passing

### Tests for User Story 2

- [x] T026 [P] [US2] Create `tests/test_encounter_builder.py` with tests for XP calculation and creature selection

### Implementation for User Story 2

- [x] T027 [US2] Implement DMG XP threshold tables in `scripts/campaign/encounter_builder.py`
- [x] T028 [US2] Implement encounter multiplier calculation based on creature count
- [x] T029 [US2] Implement creature loader from `books/reference/creatures/` with CR parsing
- [x] T030 [US2] Implement creature filtering by type, environment, CR range
- [x] T031 [US2] Implement encounter generation algorithm (select creatures to match target XP)
- [x] T032 [US2] Implement encounter markdown output with creature links and XP breakdown
- [x] T033 [US2] Add CLI interface with `--level`, `--size`, `--difficulty`, `--type`, `--save` options
- [x] T034 [US2] Add encounter index update when saving encounters
- [x] T035 [US2] Add party state reading from `campaign/party/index.md` for auto-detection of level/size

**Checkpoint**: User Story 2 complete - can generate balanced encounters with creature links

---

## Phase 5: User Story 3 - Answer Rules Questions with Citations (Priority: P3)

**Goal**: Provide rules answers with inline-quoted text and source citations

**✅ COMPLETE**: Rules engine functional with all tests passing

### Tests for User Story 3

- [x] T036 [P] [US3] Create `tests/test_rules_engine.py` with tests for keyword extraction and rules lookup

### Implementation for User Story 3

- [x] T037 [US3] Implement keyword extraction in `scripts/campaign/rules_engine.py` (conditions, spell names, rules terms)
- [x] T038 [US3] Implement reference index search for matching entries
- [x] T039 [US3] Implement markdown file section extraction (parse headings, extract relevant blocks)
- [x] T040 [US3] Implement response formatter with inline quotes and source citations
- [x] T041 [US3] Add CLI interface for rules queries
- [x] T042 [US3] Add fuzzy matching for slight name variations

**Checkpoint**: User Story 3 complete - can answer rules questions with citations

---

## Phase 6: User Story 4 - Track Session History (Priority: P4)

**Goal**: Record session summaries with sequential numbering and dates

**✅ COMPLETE**: Session manager functional with all tests passing

### Tests for User Story 4

- [x] T043 [P] [US4] Create `tests/test_session_manager.py` with tests for session creation and indexing

### Implementation for User Story 4

- [x] T044 [US4] Implement session number detection in `scripts/campaign/session_manager.py` (find next available number)
- [x] T045 [US4] Implement session template generation with date, number, title, empty summary
- [x] T046 [US4] Implement session index update with chronological listing
- [x] T047 [US4] Add CLI interface with `new`, `list` subcommands
- [x] T048 [US4] Add NPC/location linking in session summaries (optional enhancement)

**Checkpoint**: User Story 4 complete - can create and track session summaries

---

## Phase 7: User Story 5 - Manage Campaign State (Priority: P5)

**Goal**: Create and organize NPCs, locations, and campaign notes

**✅ COMPLETE**: Campaign manager functional with NPC/location CRUD operations

### Implementation for User Story 5

- [x] T049 [US5] Implement NPC creation in `scripts/campaign/campaign_manager.py` with name, description, role fields
- [x] T050 [US5] Implement location creation with name, description, type, connections fields
- [x] T051 [US5] Implement index update logic for NPCs and locations
- [x] T052 [US5] Add CLI interface for NPC/location management (`add-npc`, `add-location`, `list-npcs`, `list-locations`)
- [x] T053 [US5] Implement campaign.md initialization with campaign metadata

**Checkpoint**: User Story 5 complete - can manage NPCs, locations, and campaign state

---

## Phase 7b: User Story 6 - AI-Assisted NPC & Location Generation (Priority: P6)

**Goal**: Enable AI-assisted generation of rich, campaign-consistent NPCs and locations from partial user input

**Independent Test**: Provide minimal NPC or location details and verify AI generates complete, thematically appropriate content that connects to existing campaign elements

**Dependency**: Requires User Story 5 (campaign state management) to be functional

### Implementation for User Story 6

- [x] T060 [US6] Create `.cursor/rules/npc-location-generation.mdc` with trigger conditions and context gathering instructions
- [x] T061 [US6] Enhance NPC template in `campaign_manager.py` to include: secrets, voice/mannerisms, combat role fields
- [x] T062 [US6] Enhance location template in `campaign_manager.py` to include: sensory details, potential encounters, secrets fields
- [x] T063 [P] [US6] Update `.cursor/rules/dnd-reference-lookup.mdc` to document species/class lookup patterns for NPC generation
- [x] T064 [P] [US6] Add campaign context summary function to `campaign_manager.py` for AI consumption (list NPCs, locations, recent sessions)
- [x] T065 [US6] Create validation function to check for entity name conflicts before creation
- [x] T066 [US6] Document AI-assisted generation workflow in `specs/1-campaign-assistant/quickstart.md`

**✅ COMPLETE**: User Story 6 complete - AI can assist in generating rich NPCs and locations from partial input

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T054 [P] Update `README.md` with Campaign Assistant feature documentation
- [x] T055 [P] Add campaign commands to `Makefile` (e.g., `make campaign-init`, `make import-character`)
- [x] T056 [P] Create `.cursor/rules/campaign-lookup.mdc` for Cursor AI campaign data navigation
- [x] T057 Run all tests and fix any failures (71/71 tests passing)
- [x] T058 Validate quickstart.md scenarios work end-to-end
- [x] T059 [P] Add `campaign/` to `.gitignore` with comment explaining it's user data (optional - may want to track)

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
- **User Story 6 (P6)**: Can start after User Story 5 - Depends on campaign_manager.py and existing campaign state

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
7. Add User Story 6 → AI-assisted NPC/location generation with rich expansions

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
