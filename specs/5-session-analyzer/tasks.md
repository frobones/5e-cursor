# Tasks: Session Transcript Analyzer

**Feature**: Session Transcript Analyzer  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Setup

**Purpose**: Create spec documentation

- [X] T001 Create `specs/5-session-analyzer/` directory structure
- [X] T002 Create spec.md with feature specification
- [X] T003 Create plan.md with implementation plan
- [X] T004 Create data-model.md with entity definitions
- [X] T005 Create tasks.md (this file)

---

## Phase 2: Core Command

**Purpose**: Create the Cursor command

- [X] T006 Create `.cursor/commands/analyze-session.md` with command structure
- [X] T007 Add context file instructions for campaign data
- [X] T008 Add analysis instructions for each section
- [X] T009 Add entity linking instructions with examples
- [X] T010 Add preservation rules for transcript and metadata

**Checkpoint**: Command file exists with complete instructions.

---

## Phase 3: Integration

**Purpose**: Integrate with transcription workflow

- [X] T011 Update `transcribe_session.py` output to prompt for `/analyze-session`
- [X] T012 Update `.cursor/rules/campaign-lookup.mdc` with analyze command documentation

**Checkpoint**: Transcription workflow prompts for analysis command.

---

## Phase 4: Validation

**Purpose**: Test and verify the command works

- [X] T013 Create sample session file with test transcript
- [ ] T014 Test `/analyze-session` command on sample session
- [ ] T015 Verify entity linking works with existing campaign data
- [ ] T016 Verify transcript and metadata preservation

**Checkpoint**: Command successfully analyzes transcripts and populates sections.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - start immediately
- **Phase 2 (Core Command)**: Depends on Phase 1
- **Phase 3 (Integration)**: Depends on Phase 2
- **Phase 4 (Validation)**: Depends on Phases 2 & 3

### Parallel Opportunities

- T006-T010 are sequential (building the same file)
- T011, T012 can run in parallel (different files)
- T013-T016 are sequential (testing workflow)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 5 | Setup and spec creation |
| 2 | 5 | Core Cursor command |
| 3 | 2 | Integration with transcription |
| 4 | 4 | Validation and testing |
| **Total** | **16** | |
