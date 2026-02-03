# Research: Encounter Builder and Combat Tracker

**Feature**: 009-encounter-builder  
**Date**: 2026-02-02

## DMG Encounter Difficulty Calculations

### Decision: Port existing Python logic to TypeScript

**Rationale**: The encounter difficulty calculation logic already exists in `scripts/campaign/encounter_builder.py` and is well-tested. Porting to TypeScript enables real-time frontend calculations without API latency.

**Alternatives Considered**:
- Backend API for calculations: Rejected due to unnecessary latency for simple math
- Shared WASM module: Overkill for ~100 lines of calculation logic

### Key Tables to Port

From `encounter_builder.py`:

1. **XP_THRESHOLDS** (lines 31-52): XP thresholds by character level for Easy/Medium/Hard/Deadly
2. **CR_XP** (lines 55-90): XP values by Challenge Rating (0 through 30)
3. **ENCOUNTER_MULTIPLIERS** (lines 94-101): Multipliers based on number of creatures

### Calculation Functions

- `getPartyThresholds(level, size)`: Calculate XP thresholds for a party
- `getEncounterMultiplier(numCreatures)`: Get multiplier for creature count
- `calculateDifficulty(baseXP, numCreatures, partyLevel, partySize)`: Determine difficulty tier

## Combat State Persistence

### Decision: JSON files in `campaign/encounters/combat-{slug}.json`

**Rationale**: 
- Combat state is complex (nested combatants, damage history) - JSON handles this naturally
- Separate from encounter Markdown keeps definition and runtime state independent
- Easy to load/save without Markdown parsing

**Alternatives Considered**:
- Extend encounter Markdown with YAML frontmatter: Complex to parse/update, mixing concerns
- Browser localStorage: Doesn't persist across devices/browsers, not git-trackable
- SQLite: Overkill, breaks "Markdown as Truth" principle for simple use case

### File Format

```json
{
  "encounterId": "goblin-ambush",
  "encounterName": "Goblin Ambush",
  "round": 3,
  "turn": 2,
  "status": "active",
  "startedAt": "2026-02-02T14:30:00Z",
  "combatants": [
    {
      "id": "goblin-1",
      "name": "Goblin 1",
      "type": "monster",
      "creatureSlug": "goblin",
      "initiative": 15,
      "maxHP": 7,
      "currentHP": 7,
      "tempHP": 0,
      "conditions": [],
      "isActive": false
    }
  ],
  "damageLog": [
    {
      "id": "evt-1",
      "round": 1,
      "turn": 0,
      "targetId": "goblin-1",
      "targetName": "Goblin 1",
      "amount": 8,
      "type": "damage",
      "source": "Longsword",
      "timestamp": "2026-02-02T14:35:00Z"
    }
  ]
}
```

## Initiative Tracking

### Decision: Auto-roll for monsters, manual entry for players

**Rationale**: 
- Monsters: DM typically rolls for groups anyway; auto-rolling saves time
- Players: Roll their own dice; DM enters values manually

**Implementation**:
- Monster initiative: `Math.floor(Math.random() * 20) + 1 + dexModifier`
- Player initiative: Input field, DM enters rolled value
- Sort combatants by initiative (descending), stable sort for ties

## Party Character HP Source

### Decision: Use HP from imported character data

**Rationale**: Characters imported from D&D Beyond include current/max HP. Use these values as starting point for combat.

**Fallback**: If HP not available in character data, prompt DM to enter manually.

**Source**: `GET /api/party/characters` returns `CharacterDetail` with HP fields parsed from character Markdown.

## Creature HP Source

### Decision: Parse HP from creature reference data

**Rationale**: Creature Markdown files include HP in stat block format (e.g., "**Hit Points** 7 (2d6)").

**Implementation**: 
- Reference index already includes creature metadata
- Add HP parsing to creature extractor if not present
- For combat, use HP value from reference (or allow DM override)

**Fallback**: If HP not parseable, prompt DM to enter manually (default 10).

## Real-time Difficulty Display

### Decision: Color-coded badge with threshold context

**Rationale**: Quick visual feedback helps DMs balance encounters while building.

**Implementation**:
- Easy: Green badge
- Medium: Blue badge  
- Hard: Orange badge
- Deadly: Red badge
- Display party thresholds below for reference

## Open Items

*None - all technical decisions resolved.*
