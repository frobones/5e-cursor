# Tasks: NPC Relationship Graph

**Feature**: NPC Relationship Graph  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Setup

**Purpose**: Create spec documentation

- [X] T001 Create `specs/7-npc-relationships/` directory structure
- [X] T002 Create spec.md with feature specification
- [X] T003 Create plan.md with implementation plan
- [X] T004 Create data-model.md with entity definitions
- [X] T005 Create tasks.md (this file)

---

## Phase 2: Relationship Parser

**Purpose**: Core parsing functionality

- [X] T006 Create `scripts/lib/relationship_parser.py` with dataclasses
- [X] T007 Implement `parse_relationship_line()` function
- [X] T008 Implement `parse_connections_section()` function
- [X] T009 Implement `extract_connections_from_file()` function
- [X] T010 Add relationship type validation with warnings
- [X] T011 Add unit tests for relationship parsing

**Checkpoint**: Can parse relationship lines from NPC files.

---

## Phase 3: NPC Template Update

**Purpose**: Update NPC template with structured format

- [X] T012 Update `create_npc()` in campaign_manager.py with new Connections format
- [X] T013 Add example relationship in Connections section placeholder

**Checkpoint**: New NPCs have structured Connections section.

---

## Phase 4: Add Relationship Command

**Purpose**: CLI command to add relationships

- [X] T014 Add `add-relationship` subcommand to campaign_manager.py
- [X] T015 Implement bidirectional relationship adding
- [X] T016 Implement inverse type mapping
- [X] T017 Add validation for NPC existence
- [X] T018 Add tests for add-relationship command

**Checkpoint**: Can add relationships between NPCs via CLI.

---

## Phase 5: Graph Generator

**Purpose**: Generate Mermaid diagram

- [X] T019 Create `scripts/campaign/relationship_graph.py` structure
- [X] T020 Implement `collect_all_relationships()` function
- [X] T021 Implement `build_graph()` function
- [X] T022 Implement `generate_mermaid()` function
- [X] T023 Implement `write_relationships_file()` function
- [X] T024 Implement CLI with argparse
- [X] T025 Add comprehensive tests

**Checkpoint**: Can generate relationship graph from NPC files.

---

## Phase 6: Documentation & Polish

**Purpose**: Final integration and documentation

- [X] T026 Update init_campaign.py to create relationships.md placeholder
- [X] T027 Update campaign-lookup.mdc with relationship commands
- [X] T028 Create quickstart.md for relationship feature
- [X] T029 Add relationship_graph to scripts/campaign/__init__.py
- [X] T030 Run all tests and verify passing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Parser)**: Depends on Phase 1
- **Phase 3 (Template)**: Depends on Phase 2
- **Phase 4 (Add Command)**: Depends on Phases 2 & 3
- **Phase 5 (Generator)**: Depends on Phase 2
- **Phase 6 (Documentation)**: Depends on Phases 4 & 5

### Parallel Opportunities

- Phase 3, 4, 5 can partially run in parallel (different aspects of the feature)
- T019-T025 are mostly sequential (building the same tool)
- T026, T027, T028, T029 can run in parallel (different files)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 5 | Setup and spec creation |
| 2 | 6 | Relationship parser |
| 3 | 2 | NPC template update |
| 4 | 5 | Add relationship command |
| 5 | 7 | Graph generator |
| 6 | 5 | Documentation & polish |
| **Total** | **30** | |
