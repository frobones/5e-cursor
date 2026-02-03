# Implementation Plan: Encounter Builder and Combat Tracker

**Branch**: `009-encounter-builder` | **Date**: 2026-02-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-encounter-builder/spec.md`

## Summary

Build an interactive encounter builder and combat tracker for the Campaign Web UI. The encounter builder enables DMs to create balanced encounters by browsing creatures, configuring party settings, and seeing real-time difficulty calculations. The combat runner allows running encounters with initiative tracking, HP management, damage logging, and persistent state for resumable combat sessions.

## Technical Context

**Language/Version**: TypeScript 5.3+ (frontend), Python 3.11+ (backend)
**Primary Dependencies**: React 18, TanStack Query, TailwindCSS, FastAPI, Pydantic
**Storage**: JSON files for combat state (`campaign/encounters/combat-*.json`), Markdown for encounters
**Testing**: pytest (backend), manual testing (frontend - no test framework currently)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari), localhost only
**Project Type**: Web application (React frontend + FastAPI backend)
**Performance Goals**: Real-time difficulty calculation (<100ms), responsive UI interactions
**Constraints**: Local-only deployment, works offline after initial load
**Scale/Scope**: Single DM usage, typically <20 combatants per encounter

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
| --------- | ------ | ----- |
| I. AI-First Design | PASS | Encounter/combat data stored as JSON/Markdown, AI-parseable |
| II. Reference as Foundation | PASS | Creatures come from reference index, not modified |
| III. Campaign as Living State | PASS | Encounters/combat in `campaign/` directory, linked to reference |
| IV. DM as Final Authority | PASS | DM manually controls all combat actions, AI only calculates |
| V. Markdown as Truth | PASS | Encounters stored as Markdown, combat state as JSON |
| VI. Modular Extraction | PASS | Encounter builder works independently, combat runner optional |

**Gate Status**: PASS - No violations

## Project Structure

### Documentation (this feature)

```text
specs/009-encounter-builder/
├── plan.md              # This file
├── research.md          # Phase 0 output - technical decisions
├── data-model.md        # Phase 1 output - entity definitions
├── quickstart.md        # Phase 1 output - integration guide
├── checklists/          # Quality validation
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Frontend (React + TypeScript)
frontend/
├── src/
│   ├── components/
│   │   ├── encounter/           # NEW: Encounter builder components
│   │   │   ├── CreatureSelector.tsx
│   │   │   ├── EncounterPanel.tsx
│   │   │   └── index.ts
│   │   └── combat/              # NEW: Combat tracker components
│   │       ├── CombatTracker.tsx
│   │       ├── InitiativeList.tsx
│   │       ├── CombatantCard.tsx
│   │       ├── DamageHistory.tsx
│   │       └── index.ts
│   ├── pages/
│   │   ├── EncounterBuilder.tsx  # NEW: Build/edit encounters
│   │   └── EncounterRunner.tsx   # NEW: Run combat
│   ├── utils/
│   │   ├── encounterCalculator.ts # NEW: DMG difficulty calculations
│   │   └── combatState.ts        # NEW: Combat state management
│   ├── services/
│   │   └── api.ts               # MODIFY: Add encounter/combat endpoints
│   └── types/
│       └── index.ts             # MODIFY: Add combat types

# Backend (Python + FastAPI)
scripts/web/
├── api/
│   ├── entities.py              # MODIFY: Add POST/PUT encounters
│   └── combat.py                # NEW: Combat state endpoints
├── models/
│   ├── entities.py              # MODIFY: Add EncounterCreate
│   └── combat.py                # NEW: Combat Pydantic models
└── services/
    ├── entities.py              # MODIFY: Add encounter CRUD
    └── combat.py                # NEW: Combat state file operations

# Campaign data storage
campaign/
└── encounters/
    ├── *.md                     # Saved encounter files
    └── combat-*.json            # Active combat state files (NEW)
```

**Structure Decision**: Extends existing web application structure with new components in `frontend/src/components/encounter/` and `frontend/src/components/combat/`, new utility modules, and new backend API/service modules.

## Architecture Overview

```mermaid
flowchart TB
    subgraph frontend [Frontend - React]
        subgraph builder [Encounter Builder]
            EB[EncounterBuilder.tsx]
            CS[CreatureSelector]
            EP[EncounterPanel]
            CALC[encounterCalculator.ts]
        end
        
        subgraph runner [Combat Runner]
            ER[EncounterRunner.tsx]
            CT[CombatTracker]
            IL[InitiativeList]
            DH[DamageHistory]
        end
    end
    
    subgraph backend [Backend - FastAPI]
        ENC_API[/api/encounters]
        COMBAT_API[/api/combat]
        REF_API[/api/reference/creatures]
        PARTY_API[/api/party]
    end
    
    subgraph storage [File Storage]
        ENC_MD[campaign/encounters/*.md]
        COMBAT_JSON[campaign/encounters/combat-*.json]
    end
    
    EB --> CS
    EB --> EP
    EP --> CALC
    ER --> CT
    CT --> IL
    ER --> DH
    
    CS --> REF_API
    EP --> PARTY_API
    EB --> ENC_API
    ER --> COMBAT_API
    
    ENC_API --> ENC_MD
    COMBAT_API --> COMBAT_JSON
```

## Key Technical Decisions

### 1. Difficulty Calculation in Frontend

Port DMG encounter difficulty tables to TypeScript for real-time calculations without API round-trips. The calculation logic is stateless and deterministic, making frontend implementation ideal.

### 2. Combat State as JSON

Store combat state in JSON files (`campaign/encounters/combat-{slug}.json`) rather than extending Markdown encounters. This allows:
- Structured data for complex state (HP, conditions, damage log)
- Easy resume without parsing Markdown
- Clean separation of encounter definition vs. runtime state

### 3. Individual Combatant Instances

Expand creature quantities into individual instances (e.g., "3 Goblins" → "Goblin 1", "Goblin 2", "Goblin 3") when starting combat. Each instance tracks its own HP, conditions, and damage events.

### 4. Auto-save on State Changes

Combat state auto-saves after each action (damage, turn advance, etc.) to ensure resume capability. Uses debounced writes to avoid excessive file I/O.

## Complexity Tracking

No constitution violations to justify.
