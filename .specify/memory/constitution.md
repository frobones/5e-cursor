<!--
Sync Impact Report
- Version change: 0.0.0 → 1.0.0
- Modified principles: None (initial creation)
- Added sections: All (6 principles, Additional Constraints, Development Workflow, Governance)
- Removed sections: Template placeholders
- Templates requiring updates: ✅ constitution.md updated
- Follow-up TODOs: None
-->

# 5e-cursor Constitution

## Core Principles

### I. AI-First Design

All data structures and formats MUST be optimized for AI context windows and reasoning.

- Markdown files MUST be self-contained with sufficient context for AI understanding
- JSON indexes MUST support fast name-to-path lookups without loading full files
- Cross-references MUST enable discovery of related content
- File sizes SHOULD stay within typical AI context limits (<50KB per file preferred)
- Content MUST be formatted for AI parsing (consistent headings, structured data)

**Rationale**: This project exists to enhance AI-assisted D&D gameplay. Every design decision prioritizes AI consumability over human convenience when they conflict.

### II. Reference as Foundation

Authoritative 5e reference data MUST underlie all campaign management features.

- Extracted reference data in `books/` is the canonical source of D&D rules, spells, creatures, items, and classes
- Campaign entities (characters, encounters) MUST link to reference data when applicable
- Reference data MUST NOT be modified by campaign features
- All reference data MUST be regenerable from source via `make extract`

**Rationale**: The reference layer provides the authoritative foundation that makes other features valuable. Campaign features depend on it; they do not modify it.

### III. Campaign as Living State

Campaign state evolves over time, linked to reference data.

- Campaign data MUST be stored separately from reference data (in `campaign/` directory)
- Campaign entities MUST use relative links to reference files
- Campaign history MUST be append-only (session summaries, not destructive edits)
- Character sheets MUST preserve import source metadata (D&D Beyond URL, import date)

**Rationale**: Campaigns are dynamic while references are static. Separation ensures reference updates don't corrupt campaign state and campaign changes don't pollute reference data.

### IV. DM as Final Authority

AI assists and suggests; the DM decides.

- AI-generated content (encounters, answers) MUST be presented as suggestions
- AI MUST NOT make permanent changes without explicit DM confirmation
- AI MUST provide source citations so DMs can verify and override
- AI recommendations MUST explain reasoning when non-obvious

**Rationale**: D&D is a creative, social game. AI enhances the DM's capabilities but never replaces their judgment or agency.

### V. Markdown as Truth

Human-readable, AI-parseable, git-trackable formats are mandatory.

- All persistent data MUST be stored as Markdown or JSON
- Binary formats are PROHIBITED for campaign or reference data
- Files MUST be diffable with clean git history
- File names MUST be URL-safe slugs (lowercase, hyphens, no spaces)

**Rationale**: Markdown satisfies all three constraints (human, AI, git) without compromise. It enables text-based workflows that integrate with existing tools.

### VI. Modular Extraction

Each capability MUST be independently useful.

- Reference extraction MUST work without campaign features
- Character import MUST work without encounter building
- Encounter building MUST work without session tracking
- Each extractor script MUST be independently runnable

**Rationale**: Modularity enables incremental adoption, easier testing, and allows users to use only the features they need.

## Additional Constraints

### Data Integrity

- D&D Beyond imports MUST preserve all source data without loss
- Reference data MUST accurately reflect 5etools source material
- Calculations (XP thresholds, encounter difficulty) MUST follow DMG guidelines exactly

### External Dependencies

- D&D Beyond API access requires characters set to "Public" privacy
- 5etools submodule MUST be excluded from Cursor context via `.cursorignore`
- Network failures during import MUST provide clear, actionable error messages

### Security & Privacy

- No authentication tokens or credentials stored in repository
- User campaign data stays local (no cloud sync or external transmission)
- D&D Beyond character IDs are public information; no PII beyond what users choose to import

## Development Workflow

### Testing Standards

- Extraction scripts MUST be tested against known 5etools source files
- Character import MUST be tested with sample D&D Beyond API responses
- Encounter calculations MUST be validated against DMG tables

### Documentation Requirements

- All user-facing features MUST be documented in README or docs/
- Scripts MUST include usage comments or help flags
- Cursor rules MUST explain lookup strategies for AI context

### Code Quality

- Python code MUST follow PEP standards (120 char line limit)
- One class per file unless tightly coupled
- No duplicate code; extract shared utilities

## Governance

This constitution supersedes all other practices. Changes require:

1. Documented rationale for the change
2. Impact analysis on existing features
3. Version increment following semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle or significant expansion
   - PATCH: Clarification or wording refinement

All code reviews MUST verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-01-28 | **Last Amended**: 2026-01-28
