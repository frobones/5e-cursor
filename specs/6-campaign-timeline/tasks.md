# Tasks: Campaign Timeline

**Feature**: Campaign Timeline  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Setup

**Purpose**: Create spec documentation and core utilities

- [X] T001 Create `specs/6-campaign-timeline/` directory structure
- [X] T002 Create spec.md with feature specification
- [X] T003 Create plan.md with implementation plan
- [X] T004 Create data-model.md with entity definitions
- [X] T005 Create tasks.md (this file)

---

## Phase 2: In-Game Date Utilities

**Purpose**: Core date parsing and formatting

- [X] T006 Create `scripts/lib/campaign_calendar.py` with InGameDate dataclass
- [X] T007 Implement `parse_in_game_date()` function
- [X] T008 Implement `format_in_game_date()` function
- [X] T009 Add unit tests for date parsing

**Checkpoint**: Can parse "Day 15" into InGameDate and format back.

---

## Phase 3: Session Manager Update

**Purpose**: Add in-game date tracking to sessions

- [X] T010 Add `--in-game-date` argument to session_manager.py
- [X] T011 Update session template to include In-Game Date field
- [X] T012 Add tests for session creation with in-game date

**Checkpoint**: Sessions can be created with in-game dates.

---

## Phase 4: Campaign Manager Update

**Purpose**: Add first appearance tracking to entities

- [X] T013 Add `--first-seen` argument to add-npc command
- [X] T014 Update NPC template to include First Appearance field
- [X] T015 Add `--discovered` argument to add-location command
- [X] T016 Update location template to include Discovered field
- [X] T017 Add tests for NPC/location creation with dates

**Checkpoint**: NPCs and locations can track first appearance.

---

## Phase 5: Events File

**Purpose**: Support custom campaign events

- [X] T018 Create events.md template content
- [X] T019 Update init_campaign.py to create events.md
- [X] T020 Implement events table parser
- [X] T021 Add tests for events parsing

**Checkpoint**: Custom events can be added and parsed.

---

## Phase 6: Timeline Generator

**Purpose**: Core timeline generation

- [X] T022 Create `scripts/campaign/timeline_generator.py` with structure
- [X] T023 Implement `collect_session_events()` function
- [X] T024 Implement `collect_npc_events()` function
- [X] T025 Implement `collect_location_events()` function
- [X] T026 Implement `collect_custom_events()` function
- [X] T027 Implement event sorting by in-game date
- [X] T028 Implement timeline markdown generation
- [X] T029 Implement CLI with argparse
- [X] T030 Add comprehensive tests

**Checkpoint**: Timeline can be generated from all sources.

---

## Phase 7: Documentation & Polish

**Purpose**: Final integration and documentation

- [X] T031 Update `.cursor/rules/campaign-lookup.mdc` with timeline commands
- [X] T032 Create quickstart.md for timeline feature
- [X] T033 Add timeline_generator to `scripts/campaign/__init__.py`
- [X] T034 Run all tests and verify passing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Date Utilities)**: Depends on Phase 1
- **Phase 3 (Session Manager)**: Depends on Phase 2
- **Phase 4 (Campaign Manager)**: Depends on Phase 2
- **Phase 5 (Events File)**: Depends on Phase 2
- **Phase 6 (Timeline Generator)**: Depends on Phases 3, 4, 5
- **Phase 7 (Documentation)**: Depends on Phase 6

### Parallel Opportunities

- Phase 3, 4, 5 can run in parallel (different files, same dependency on Phase 2)
- T023, T024, T025, T026 can run in parallel (different collection functions)
- T031, T032, T033 can run in parallel (different files)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 5 | Setup and spec creation |
| 2 | 4 | In-game date utilities |
| 3 | 3 | Session manager update |
| 4 | 5 | Campaign manager update |
| 5 | 4 | Events file support |
| 6 | 9 | Timeline generator |
| 7 | 4 | Documentation & polish |
| **Total** | **34** | |
