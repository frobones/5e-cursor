# Data Model: Campaign Assistant

**Source**: [spec.md](spec.md) Key Entities section  
**Date**: 2026-01-28

## Overview

All entities are stored as markdown files. This document defines the structure and relationships between campaign entities.

## Entity Definitions

### Character

**Description**: Player character imported from D&D Beyond or created manually.

**File Location**: `campaign/party/characters/{slug}.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Character name |
| player | string | No | Player name (from D&D Beyond username) |
| species | string | Yes | Species/race name |
| class | string | Yes | Class and level (e.g., "Rogue 5 / Wizard 2") |
| level | integer | Yes | Total character level |
| background | string | No | Character background |
| alignment | string | No | Alignment |
| stats | object | Yes | STR, DEX, CON, INT, WIS, CHA scores and modifiers |
| hp | object | Yes | Current and maximum hit points |
| ac | integer | Yes | Armor class |
| speed | string | Yes | Movement speed |
| proficiency_bonus | integer | Yes | Proficiency bonus |
| skills | array | Yes | Skill proficiencies with modifiers |
| languages | array | Yes | Known languages |
| tools | array | No | Tool proficiencies |
| features | array | Yes | Class/species features with reference links |
| feats | array | No | Feats with reference links |
| spells | object | No | Known/prepared spells by level with reference links |
| equipment | array | Yes | Inventory items with reference links |
| currency | object | Yes | CP, SP, GP, EP, PP |
| traits | object | No | Personality traits, ideals, bonds, flaws |
| appearance | string | No | Physical description |
| notes | object | No | Allies, enemies, backstory, other notes |
| source_url | string | No | D&D Beyond character URL |
| imported_date | string | No | ISO date of import |

**Relationships**:
- Links to class features in `books/reference/classes/`
- Links to species in `books/reference/species/`
- Links to feats in `books/reference/feats/`
- Links to spells in `books/reference/spells/`
- Links to equipment in `books/reference/equipment/` and `books/reference/items/`

**State Transitions**: None (character data is point-in-time snapshot; re-import for updates)

---

### Encounter

**Description**: Collection of creatures with difficulty rating and XP breakdown.

**File Location**: `campaign/encounters/{slug}.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Encounter name |
| difficulty | enum | Yes | Easy, Medium, Hard, Deadly |
| party_level | integer | Yes | Average party level at creation |
| party_size | integer | Yes | Number of party members |
| creatures | array | Yes | List of creatures with quantity and reference links |
| base_xp | integer | Yes | Sum of creature XP before multiplier |
| adjusted_xp | integer | Yes | XP after encounter multiplier |
| threshold | object | Yes | Party XP thresholds (easy, medium, hard, deadly) |
| environment | string | No | Encounter setting |
| notes | string | No | DM notes |
| created_date | string | Yes | ISO date of creation |

**Creature Entry**:

| Field | Type | Description |
|-------|------|-------------|
| name | string | Creature name |
| quantity | integer | Number of this creature |
| cr | string | Challenge rating |
| xp | integer | XP per creature |
| reference | string | Link to creature stat block |

**Relationships**:
- Links to creatures in `books/reference/creatures/`

**State Transitions**: None (encounters are saved snapshots)

---

### Session

**Description**: Summary of a play session with date and narrative content.

**File Location**: `campaign/sessions/session-{NNN}.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| session_number | integer | Yes | Sequential session number |
| date | string | Yes | ISO date of session |
| title | string | No | Session title/name |
| summary | string | Yes | Free-form session summary |
| npcs_mentioned | array | No | NPCs appearing in session with links |
| locations_mentioned | array | No | Locations visited with links |
| notable_events | array | No | Key events bullet list |
| loot | array | No | Items acquired with reference links |
| xp_awarded | integer | No | XP awarded this session |

**Relationships**:
- Links to NPCs in `campaign/npcs/`
- Links to locations in `campaign/locations/`
- Links to items in `books/reference/items/`

**State Transitions**: None (sessions are append-only historical records)

---

### NPC

**Description**: Non-player character with description and campaign role.

**File Location**: `campaign/npcs/{slug}.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | NPC name |
| description | string | Yes | Physical and personality description |
| role | string | No | Role in campaign (ally, enemy, neutral, etc.) |
| location | string | No | Where they're typically found, with link |
| relationships | array | No | Connections to other NPCs/characters |
| stat_block | string | No | Link to creature stat block if applicable |
| notes | string | No | DM notes |
| first_appearance | string | No | Session number or description |

**Relationships**:
- Links to locations in `campaign/locations/`
- Links to sessions in `campaign/sessions/`
- Links to creatures in `books/reference/creatures/` (if stat block provided)

---

### Location

**Description**: Place in the campaign world.

**File Location**: `campaign/locations/{slug}.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Location name |
| description | string | Yes | Description of the place |
| type | string | No | Type (city, dungeon, tavern, etc.) |
| parent_location | string | No | Containing location with link |
| connections | array | No | Connected locations with links |
| notable_npcs | array | No | NPCs found here with links |
| notes | string | No | DM notes |

**Relationships**:
- Links to parent/connected locations in `campaign/locations/`
- Links to NPCs in `campaign/npcs/`

---

### Campaign

**Description**: Top-level campaign metadata and overview.

**File Location**: `campaign/campaign.md`

**Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Campaign name |
| setting | string | No | Campaign setting/world |
| start_date | string | No | Real-world start date |
| themes | array | No | Campaign themes |
| summary | string | No | Campaign overview |
| current_session | integer | No | Latest session number |
| party_level | integer | No | Average party level |

**Relationships**:
- References party index in `campaign/party/index.md`
- References session index in `campaign/sessions/index.md`

## Index Files

### Party Index

**File Location**: `campaign/party/index.md`

**Content**:
- Party name/summary
- Average party level
- List of characters with links and key stats (class, level, HP)
- Party composition notes

### NPC Index

**File Location**: `campaign/npcs/index.md`

**Content**:
- List of NPCs grouped by role (allies, enemies, neutral)
- Each entry: name, brief description, link

### Location Index

**File Location**: `campaign/locations/index.md`

**Content**:
- List of locations grouped by type or region
- Each entry: name, brief description, link

### Session Index

**File Location**: `campaign/sessions/index.md`

**Content**:
- Chronological list of sessions
- Each entry: session number, date, title, link

### Encounter Index

**File Location**: `campaign/encounters/index.md`

**Content**:
- List of saved encounters
- Each entry: name, difficulty, party level, link

## Validation Rules

### Character Validation
- Name must be non-empty
- Level must be 1-20
- Stats must be 1-30 for each ability
- HP maximum must be positive
- AC must be positive

### Encounter Validation
- Must have at least one creature
- Party level must be 1-20
- Party size must be 1-10
- Difficulty must be one of: Easy, Medium, Hard, Deadly

### Session Validation
- Session number must be positive and sequential
- Date must be valid ISO format
- Summary must be non-empty

## File Naming Conventions

All entity files use URL-safe slugs:
- Lowercase
- Hyphens instead of spaces
- No special characters
- Example: "Meilin Starwell" → `meilin-starwell.md`

Session files use zero-padded numbers:
- Example: Session 1 → `session-001.md`
- Example: Session 42 → `session-042.md`
