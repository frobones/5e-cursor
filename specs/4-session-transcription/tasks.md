# Tasks: Session Transcription

**Feature**: Session Transcription  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Setup

**Purpose**: Project initialization and dependencies

- [X] T001 Add `openai-whisper>=20231117` to requirements.txt
- [X] T002 Create `scripts/campaign/transcribe_session.py` with module structure and imports
- [X] T003 Add transcribe_session to `scripts/campaign/__init__.py` exports

---

## Phase 2: Core Infrastructure

**Purpose**: Hardware detection and model selection

- [X] T004 [P] Implement `detect_device()` function - check CUDA, MPS, CPU
- [X] T005 [P] Implement `get_default_model(device)` function - large for GPU, small for CPU
- [X] T006 Implement device/model status messages for user feedback

**Checkpoint**: Hardware detection works and selects appropriate defaults.

---

## Phase 3: User Story 1 - Transcribe Audio Recording (Priority: P1)

**Goal**: Transcribe audio files using local Whisper

### Tests for User Story 1

- [X] T007 [P] [US1] Create `tests/test_transcribe_session.py` with test structure
- [X] T008 [P] [US1] Add tests for `detect_device()` with mocked torch
- [X] T009 [P] [US1] Add tests for `get_default_model()` with various devices
- [X] T010 [P] [US1] Add tests for `transcribe_audio()` with mocked whisper

### Implementation for User Story 1

- [X] T011 [US1] Implement `validate_audio_path(path)` - check file exists and is readable
- [X] T012 [US1] Implement `transcribe_audio(audio_path, model_name, device)` - run Whisper
- [X] T013 [US1] Add progress/status output during transcription
- [X] T014 [US1] Implement error handling for missing ffmpeg, invalid audio

**Checkpoint**: Can transcribe audio file and display transcript.

---

## Phase 4: User Story 2 - Create Session File with Transcript (Priority: P2)

**Goal**: Create session files with embedded transcripts

### Tests for User Story 2

- [X] T015 [P] [US2] Add tests for `save_transcript()` function
- [X] T016 [P] [US2] Add tests for `create_session_with_transcript()` function
- [X] T017 [P] [US2] Add tests for session index update integration

### Implementation for User Story 2

- [X] T018 [US2] Create `campaign/sessions/transcripts/` directory handling
- [X] T019 [US2] Implement `save_transcript(transcript, session_number, sessions_dir)` - save .txt file
- [X] T020 [US2] Implement session file template with transcript section
- [X] T021 [US2] Implement `create_session_with_transcript(sessions_dir, title, number, transcript, metadata)`
- [X] T022 [US2] Integrate with existing `get_next_session_number()` from session_manager
- [X] T023 [US2] Integrate with existing `update_session_index()` from session_manager

**Checkpoint**: Transcription creates session file with proper format and updates index.

---

## Phase 5: User Story 3 - CLI Interface (Priority: P3)

**Goal**: Complete CLI with all options

### Implementation for User Story 3

- [X] T024 [US3] Implement argparse with audio_path positional argument
- [X] T025 [US3] Add `--title` option for session title
- [X] T026 [US3] Add `--model` option to override default model
- [X] T027 [US3] Add `--number` option to specify session number
- [X] T028 [US3] Implement `main()` function orchestrating full workflow
- [X] T029 [US3] Add `--help` with usage examples in epilog

### Tests for User Story 3

- [X] T030 [P] [US3] Add CLI argument parsing tests
- [X] T031 [P] [US3] Add end-to-end workflow test with mocked Whisper

**Checkpoint**: Full CLI works with all options.

---

## Phase 6: Polish & Documentation

**Purpose**: Final cleanup and documentation updates

- [X] T032 [P] Add module docstring with comprehensive usage examples
- [X] T033 [P] Update `.cursor/rules/campaign-lookup.mdc` with transcription commands
- [X] T034 Run all tests and verify passing
- [X] T035 Validate quickstart.md scenarios work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Core Infrastructure (Phase 2)**: Depends on Setup
- **User Story 1 (Phase 3)**: Depends on Core Infrastructure
- **User Story 2 (Phase 4)**: Depends on User Story 1 (needs transcript)
- **User Story 3 (Phase 5)**: Depends on User Stories 1 & 2
- **Polish (Phase 6)**: Depends on all User Stories

### Parallel Opportunities

- T004, T005 can run in parallel (different functions)
- T007, T008, T009, T010 can run in parallel (different test files/functions)
- T015, T016, T017 can run in parallel (different test functions)
- T030, T031 can run in parallel (different test functions)
- T032, T033 can run in parallel (different files)

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 3 | Setup and dependencies |
| 2 | 3 | Hardware detection |
| 3 | 8 | Audio transcription (P1) |
| 4 | 9 | Session file creation (P2) |
| 5 | 8 | CLI interface (P3) |
| 6 | 4 | Polish and docs |
| **Total** | **35** | |
