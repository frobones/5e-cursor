# Feature Specification: Session Transcription

**Feature Branch**: `4-session-transcription`  
**Created**: 2026-02-02  
**Status**: Draft  
**Input**: User description: "Session Transcription: Process audio recordings of D&D sessions using local Whisper to generate transcripts. Create session files with embedded transcripts that Cursor AI can then analyze into structured session notes. Support hardware detection for optimal model selection (large for GPU, small for CPU-only)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Transcribe Audio Recording (Priority: P1)

As a DM, I want to transcribe an audio recording of my D&D session so that I have a text record of what happened that I can reference and search.

**Why this priority**: This is the core functionality - without transcription, nothing else works. Provides immediate value by converting hours of audio into searchable text.

**Independent Test**: Can be fully tested by providing an audio file path and verifying a transcript is generated and saved.

**Acceptance Scenarios**:

1. **Given** a valid audio file (mp3, wav, m4a), **When** I run the transcribe command, **Then** the system transcribes the audio using Whisper and displays the transcript
2. **Given** a valid audio file, **When** transcription completes, **Then** a raw transcript is saved to `campaign/sessions/transcripts/session-NNN.txt`
3. **Given** a system with GPU (CUDA or MPS), **When** I run transcribe without specifying a model, **Then** the system uses the `large` model by default
4. **Given** a system without GPU, **When** I run transcribe without specifying a model, **Then** the system uses the `small` model by default
5. **Given** a `--model` flag, **When** I specify a model (tiny/base/small/medium/large), **Then** that model is used regardless of hardware detection
6. **Given** an invalid or missing audio file, **When** I run the transcribe command, **Then** the system displays a clear error message

---

### User Story 2 - Create Session File with Transcript (Priority: P2)

As a DM, I want the transcription to create a session file with the transcript embedded so that I have a starting point for my session notes.

**Why this priority**: Builds on P1 by integrating with the existing session management workflow. The session file provides structure for the transcript.

**Independent Test**: Can be fully tested by running transcription and verifying a session file is created with the correct format and transcript content.

**Acceptance Scenarios**:

1. **Given** a successful transcription, **When** the process completes, **Then** a session file is created at `campaign/sessions/session-NNN.md` with the transcript embedded
2. **Given** a `--title` flag, **When** I provide a session title, **Then** the session file uses that title in the heading
3. **Given** no `--title` flag, **When** the session is created, **Then** the title defaults to "Untitled Session"
4. **Given** a `--number` flag, **When** I specify a session number, **Then** that number is used instead of auto-incrementing
5. **Given** existing sessions, **When** creating a new session without `--number`, **Then** the next sequential number is used
6. **Given** a created session file, **When** viewing it, **Then** the session index is updated with the new session

---

### User Story 3 - Display Hardware Detection Status (Priority: P3)

As a DM, I want to see what hardware acceleration is available so that I understand why a particular model was selected and can make informed choices.

**Why this priority**: Transparency about model selection helps users understand performance expectations and troubleshoot issues.

**Independent Test**: Can be fully tested by running the command and verifying hardware detection output is displayed.

**Acceptance Scenarios**:

1. **Given** a system with NVIDIA GPU, **When** running transcription, **Then** the system displays "NVIDIA GPU detected. Using 'large' model for best accuracy."
2. **Given** a system with Apple Silicon, **When** running transcription, **Then** the system displays "Apple Silicon detected. Using 'large' model for best accuracy."
3. **Given** a CPU-only system, **When** running transcription, **Then** the system displays "No GPU detected. Using 'small' model for reasonable speed." and suggests `--model medium` for better quality

---

### Edge Cases

- What happens when the audio file is too large (e.g., 4+ hour session)?
  - Whisper handles long files internally; may take significant time on CPU
  - Display progress/status during transcription
- What happens when Whisper model isn't downloaded yet?
  - Whisper auto-downloads on first use; warn user this may take time
- What happens when ffmpeg is not installed?
  - Display clear error message with installation instructions
- What happens when the campaign directory doesn't exist?
  - Display error suggesting to run `init_campaign.py` first
- What happens with non-English audio?
  - Whisper supports multiple languages; auto-detects by default
- What happens if transcription is interrupted?
  - Partial transcript is not saved; user must re-run

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST transcribe audio files using local Whisper (openai-whisper package)
- **FR-002**: System MUST detect hardware acceleration (CUDA, MPS, or CPU-only)
- **FR-003**: System MUST default to `large` model when GPU is available (CUDA or MPS)
- **FR-004**: System MUST default to `small` model when no GPU is available
- **FR-005**: System MUST support `--model` flag to override default model selection
- **FR-006**: System MUST save raw transcript to `campaign/sessions/transcripts/session-NNN.txt`
- **FR-007**: System MUST create session file at `campaign/sessions/session-NNN.md` with transcript embedded
- **FR-008**: System MUST support `--title` flag for session title
- **FR-009**: System MUST support `--number` flag to specify session number
- **FR-010**: System MUST auto-increment session number if not specified
- **FR-011**: System MUST update session index after creating session file
- **FR-012**: System MUST display hardware detection status before transcription
- **FR-013**: System MUST provide clear error messages for invalid input

### Key Entities

- **AudioFile**: Input audio recording (mp3, wav, m4a, etc.)
- **Transcript**: Raw text output from Whisper transcription
- **Session**: Markdown file with embedded transcript and structured sections for AI analysis

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can transcribe a 1-hour audio file in under 30 minutes on GPU, under 2 hours on CPU
- **SC-002**: Generated transcripts are accurate enough for AI to extract key events (subjective, but >80% word accuracy)
- **SC-003**: Session files follow the established format compatible with existing session_manager.py
- **SC-004**: Hardware detection correctly identifies GPU acceleration on supported systems
- **SC-005**: Users receive clear feedback about transcription progress and completion

## Assumptions

- User has `ffmpeg` installed (required by Whisper for audio processing)
- User has sufficient disk space for Whisper models (up to 1.5GB for large model)
- Audio quality is reasonable (clear speech, minimal background noise)
- Campaign directory exists (created by init_campaign.py)
- Users interact with the system through CLI; AI analysis happens via Cursor conversation

## Dependencies

- `openai-whisper` package for transcription
- `torch` for hardware detection and GPU acceleration
- `ffmpeg` system dependency for audio processing
- Existing `session_manager.py` patterns for session creation
- Existing `markdown_writer.py` utilities for consistent formatting
- `campaign/` directory structure from `init_campaign.py`
