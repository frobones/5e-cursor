# Tasks: Campaign Web UI

**Feature**: Campaign Web UI  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Foundation

**Purpose**: Set up project scaffolding

- [X] T001 Create `specs/8-campaign-web-ui/` directory structure
- [X] T002 Create spec.md with feature specification
- [X] T003 Create plan.md with implementation plan
- [X] T004 Create data-model.md with entity definitions
- [X] T005 Create tasks.md (this file)
- [X] T006 Create `scripts/web/` directory structure
- [X] T007 Create FastAPI `main.py` with CORS and static files
- [X] T008 Create campaign endpoint (`GET /api/campaign`)
- [X] T009 Add FastAPI dependencies to requirements.txt
- [X] T010 Create `frontend/` with Vite + React + TypeScript
- [X] T011 Configure TailwindCSS and PostCSS
- [X] T012 Set up React Router with basic routes
- [X] T013 Create global styles (variables.css, globals.css)
- [X] T014 Create Dashboard page with campaign overview

**Checkpoint**: Backend serves API, frontend renders dashboard.

---

## Phase 2: Entity Navigation

**Purpose**: Implement entity list and detail views

- [X] T015 Create Pydantic models for NPC, Location, Session
- [X] T016 Implement NPC endpoints (list, detail)
- [X] T017 Implement Location endpoints (list, detail)
- [X] T018 Implement Session endpoints (list, detail)
- [X] T019 Create entity service layer (parse markdown, extract metadata)
- [X] T020 Create NPCs list page with filtering
- [X] T021 Create NPC detail page
- [X] T022 Create Locations list page with filtering
- [X] T023 Create Location detail page
- [X] T024 Create Sessions list page
- [X] T025 Create Session detail page
- [X] T026 Create MarkdownViewer component with react-markdown
- [X] T027 Add CSS styling for markdown content

**Checkpoint**: Can browse all NPCs, locations, and sessions.

---

## Phase 3: Cross-References

**Purpose**: Enable navigation between entities

- [X] T028 Implement Party/Characters endpoints
- [X] T029 Implement Encounters endpoints
- [X] T030 Create Party overview page
- [X] T031 Create Character detail page
- [X] T032 Create Encounters list page
- [X] T033 Create Encounter detail page
- [X] T034 Create custom link renderer for internal links
- [X] T035 Convert markdown links to React Router links
- [X] T036 Add breadcrumb navigation component

**Checkpoint**: All entity links navigate correctly.

---

## Phase 4: Reference Browser

**Purpose**: Browse spells, creatures, items

- [X] T037 Create reference index endpoint
- [X] T038 Implement reference search endpoint
- [X] T039 Implement reference list by type endpoint
- [X] T040 Implement reference detail endpoint
- [X] T041 Create Reference browser page with tabs
- [X] T042 Create Spells tab with level filtering
- [X] T043 Create Creatures tab with CR filtering
- [X] T044 Create Items tab with rarity filtering
- [X] T045 Create Reference detail page
- [X] T046 Create RefTooltip component for hover previews

**Checkpoint**: Can browse and search all reference data.

---

## Phase 5: Visualizations

**Purpose**: Timeline and relationship visualizations

- [X] T047 Create timeline endpoint (reuse timeline_generator.py)
- [X] T048 Create relationships endpoint (reuse relationship_graph.py)
- [X] T049 Create Timeline page with day grouping
- [X] T050 Add timeline event icons by category
- [X] T051 Create Relationships page
- [X] T052 Integrate Mermaid for relationship diagram
- [X] T053 Add click-to-navigate on graph nodes

**Checkpoint**: Timeline and relationship graph fully functional.

---

## Phase 6: Search and Polish

**Purpose**: Global search and UX improvements

- [X] T054 Implement full-text search endpoint
- [X] T055 Create search modal with cmdk
- [X] T056 Add Cmd+K keyboard shortcut
- [X] T057 Implement file watcher with watchdog
- [X] T058 Create WebSocket endpoint for changes
- [X] T059 Add auto-refresh on file changes
- [X] T060 Implement dark mode toggle
- [X] T061 Add theme persistence to localStorage
- [X] T062 Create responsive sidebar for mobile
- [X] T063 Add loading states and error boundaries
- [X] T064 Performance optimization (React Query caching)

**Checkpoint**: Full feature complete.

---

## Phase 7: Documentation

**Purpose**: Finalize documentation and testing

- [X] T065 Create quickstart.md for web UI
- [X] T066 Add development workflow to README
- [X] T067 Add web UI to campaign-lookup.mdc
- [X] T068 Write API documentation
- [X] T069 Manual testing and bug fixes
- [X] T070 Mark all tasks complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies - start immediately
- **Phase 2 (Entities)**: Depends on Phase 1
- **Phase 3 (Cross-References)**: Depends on Phase 2
- **Phase 4 (Reference)**: Depends on Phase 1
- **Phase 5 (Visualizations)**: Depends on Phase 2
- **Phase 6 (Polish)**: Depends on Phases 2-5
- **Phase 7 (Documentation)**: Depends on Phase 6

### Parallel Opportunities

- Phase 4 can run in parallel with Phases 2-3
- T020-T027 can be split between frontend devs
- T037-T046 can run independently

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 14 | Foundation and scaffolding |
| 2 | 13 | Entity navigation |
| 3 | 9 | Cross-references |
| 4 | 10 | Reference browser |
| 5 | 7 | Visualizations |
| 6 | 11 | Search and polish |
| 7 | 6 | Documentation |
| **Total** | **70** | |
