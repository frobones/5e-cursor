# Feature Specification: Source Book Selection

**Feature Branch**: `2-source-book-selection`
**Created**: 2026-01-28
**Status**: Draft
**Input**: User description: "Add source book selection that lets users specify which D&D source books to include during extraction. Configuration stored in a YAML config file. Should support the 2024 core rulebooks (XPHB, XDMG, XMM), legacy books (PHB, DMG, MM), and supplements (AAG, BAM, EFA, etc.)."

## User Scenarios & Testing

### User Story 1 - Default 2024 Core Extraction (Priority: P1)

As a user setting up the project for the first time, I want the extraction to use sensible defaults (2024 core rulebooks) so that I don't need to configure anything to get started.

**Why this priority**: Most users will want the 2024 core rules. A working default experience is essential for onboarding.

**Independent Test**: Run `make extract` with no config file present; verify only XPHB, XDMG, XMM content is extracted.

**Acceptance Scenarios**:

1. **Given** no `sources.yaml` exists, **When** user runs `make extract`, **Then** extraction uses default sources (XPHB, XDMG, XMM) and completes successfully
2. **Given** no `sources.yaml` exists, **When** extraction completes, **Then** the `books/` directory contains only content from default sources

---

### User Story 2 - Custom Source Selection via Config (Priority: P1)

As a DM running a specific campaign, I want to specify which source books to include so that my reference data matches my campaign's allowed sources.

**Why this priority**: This is the core feature - allowing customization of source books.

**Independent Test**: Create `sources.yaml` with specific sources, run extraction, verify only those sources are extracted.

**Acceptance Scenarios**:

1. **Given** `sources.yaml` contains `sources: [XPHB, AAG, BAM]`, **When** user runs `make extract`, **Then** only content from XPHB, AAG, and BAM is extracted
2. **Given** `sources.yaml` specifies an invalid source code, **When** user runs `make extract`, **Then** system warns about unrecognized source but continues with valid sources
3. **Given** `sources.yaml` exists with custom sources, **When** extraction completes, **Then** `books/reference-index.json` only contains entries from specified sources

---

### User Story 3 - Makefile Override (Priority: P2)

As a power user, I want to override the config file sources via command line so that I can quickly test different source combinations without editing config.

**Why this priority**: Useful for experimentation but not essential for core functionality.

**Independent Test**: Run `make extract SOURCES="XPHB,XMM"` and verify only those sources are used regardless of config file.

**Acceptance Scenarios**:

1. **Given** `sources.yaml` contains `sources: [XPHB, XDMG, XMM]`, **When** user runs `make extract SOURCES="XPHB"`, **Then** only XPHB content is extracted
2. **Given** no `sources.yaml` exists, **When** user runs `make extract SOURCES="PHB,DMG,MM"`, **Then** 2014 legacy content is extracted

---

### User Story 4 - Source Presets (Priority: P3)

As a user, I want to use preset source groups (e.g., "2024-core", "2014-core", "spelljammer") so that I don't have to know individual source codes.

**Why this priority**: Nice to have for user convenience, but users can manually list sources.

**Independent Test**: Use `preset: 2024-core` in config and verify it expands to XPHB, XDMG, XMM.

**Acceptance Scenarios**:

1. **Given** `sources.yaml` contains `preset: 2024-core`, **When** user runs `make extract`, **Then** XPHB, XDMG, XMM are extracted
2. **Given** `sources.yaml` contains `preset: spelljammer`, **When** user runs `make extract`, **Then** AAG, BAM, and relevant sources are extracted

---

### Edge Cases

- What happens when sources.yaml is malformed YAML? → Show clear error message and exit
- What happens when all specified sources have no data? → Warn user, create empty books/ structure
- What happens when a source is valid but has no matching files in 5etools-src? → Skip silently or warn
- How do cross-source references work (e.g., creature references spell from different book)? → Extract the reference as-is; links may be broken if target source not included

## Requirements

### Functional Requirements

- **FR-001**: System MUST support a `sources.yaml` configuration file in the repository root
- **FR-002**: System MUST use default sources (XPHB, XDMG, XMM) when no config file exists
- **FR-003**: System MUST validate source codes against known valid sources
- **FR-004**: System MUST support Makefile override via `SOURCES` variable
- **FR-005**: System SHOULD support source presets for common configurations
- **FR-006**: System MUST filter all extractors (spells, creatures, items, classes, etc.) by selected sources
- **FR-007**: System MUST regenerate `books/reference-index.json` with only selected sources
- **FR-008**: System SHOULD warn when a specified source has no matching data

### Key Entities

- **SourceConfig**: Configuration specifying which sources to include
  - `sources`: List of source codes (e.g., ["XPHB", "XDMG", "XMM"])
  - `preset`: Optional preset name that expands to a list of sources
- **SourcePreset**: Named collection of sources (e.g., "2024-core" = XPHB, XDMG, XMM)

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can extract only 2024 content with zero configuration
- **SC-002**: Users can customize sources by editing a single YAML file
- **SC-003**: Extraction with fewer sources completes faster than full extraction
- **SC-004**: Reference index only contains entries from selected sources
