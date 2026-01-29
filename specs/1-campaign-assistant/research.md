# Research: Campaign Assistant

## D&D Beyond Character API

### Endpoint

```
GET https://character-service.dndbeyond.com/character/v5/character/{id}
```

**Access**: Works for public characters without authentication.

**Limitation**: Character must have privacy set to "Public" in D&D Beyond settings.

### Response Structure

The API returns a JSON object with this top-level structure:

```json
{
  "id": 0,
  "success": true,
  "message": "Character successfully received.",
  "data": { /* character data */ }
}
```

### Character Data Fields

Key fields in `data` object:

| Field | Type | Description |
|-------|------|-------------|
| `id` | number | D&D Beyond character ID |
| `name` | string | Character name |
| `gender` | string | Character gender |
| `age` | number | Character age |
| `race` | object | Species information |
| `race.fullName` | string | Species name (e.g., "Human") |
| `classes` | array | Class information |
| `classes[].definition.name` | string | Class name (e.g., "Rogue") |
| `classes[].level` | number | Levels in this class |
| `stats` | array | Base ability scores (id: 1=STR, 2=DEX, 3=CON, 4=INT, 5=WIS, 6=CHA) |
| `bonusStats` | array | Bonus ability scores |
| `baseHitPoints` | number | Base HP from class |
| `inventory` | array | Equipment and items |
| `feats` | array | Feats with definitions |
| `spells` | object | Spells by source (race, class, feat, etc.) |
| `modifiers` | object | All modifiers by source |
| `choices` | object | Character build choices |
| `traits` | object | Personality traits, ideals, bonds, flaws, appearance |
| `notes` | object | Character notes (allies, enemies, backstory, etc.) |
| `currencies` | object | CP, SP, GP, EP, PP |

### Classes Structure

```json
{
  "id": 218660830,
  "level": 1,
  "isStartingClass": true,
  "hitDiceUsed": 0,
  "definition": {
    "name": "Rogue",
    "hitDice": 8,
    "classFeatures": [...]
  },
  "classFeatures": [
    {
      "definition": {
        "name": "Sneak Attack",
        "description": "...",
        "snippet": "..."
      }
    }
  ]
}
```

### Inventory Item Structure

```json
{
  "id": 927741913,
  "quantity": 1,
  "equipped": true,
  "definition": {
    "name": "Leather",
    "type": "Light Armor",
    "description": "...",
    "armorClass": 11,
    "weight": 10.0,
    "cost": 10.0
  }
}
```

### Feat Structure

```json
{
  "componentId": 1789152,
  "definition": {
    "name": "Healer",
    "description": "...",
    "snippet": "..."
  }
}
```

### Modifiers Structure

Modifiers are grouped by source:

```json
{
  "modifiers": {
    "race": [...],
    "class": [...],
    "background": [...],
    "feat": [...],
    "item": [],
    "condition": []
  }
}
```

Each modifier has:
- `type`: "proficiency", "expertise", "bonus", "language", etc.
- `subType`: Specific skill, weapon, tool, or stat
- `value`: Numeric value if applicable

## Character Sheet Markdown Format

Target output format for imported characters:

```markdown
# [Character Name]

**Player**: [Player Name]  
**Species**: [Species]  
**Class**: [Class(es)] [Level]  
**Background**: [Background]  
**Alignment**: [Alignment]

## Ability Scores

| STR | DEX | CON | INT | WIS | CHA |
|-----|-----|-----|-----|-----|-----|
| 8 (-1) | 17 (+3) | 12 (+1) | 14 (+2) | 14 (+2) | 10 (+0) |

## Combat

- **Armor Class**: 13 (Leather Armor)
- **Hit Points**: 9 / 9
- **Speed**: 30 ft.
- **Proficiency Bonus**: +2

## Proficiencies

### Skills
- Deception (+2)
- History (+4)
- Insight (+4)
- **Investigation (+6)** *(Expertise)*
- **Medicine (+6)** *(Expertise)*
- Nature (+4)
- Perception (+4)
- Persuasion (+2)
- Sleight of Hand (+5)
- Stealth (+5)

### Languages
Common, Common Sign Language, Halfling, Thieves' Cant, Undercommon

### Tools
[Herbalism Kit](../../books/reference/equipment/gear/herbalism-kit.md), 
[Thieves' Tools](../../books/reference/equipment/gear/thieves-tools.md)

## Features & Traits

### Species: Human
- [Resourceful](../../books/reference/species/human.md#resourceful)
- [Skillful](../../books/reference/species/human.md#skillful)
- [Versatile](../../books/reference/species/human.md#versatile)

### Class: Rogue
- [Sneak Attack](../../books/reference/classes/rogue/sneak-attack.md) (1d6)
- [Expertise](../../books/reference/classes/rogue/expertise.md)
- [Thieves' Cant](../../books/reference/classes/rogue/thieves-cant.md)
- [Weapon Mastery](../../books/reference/classes/rogue/weapon-mastery.md)

### Feats
- [Healer](../../books/reference/feats/healer.md)
- [Skilled](../../books/reference/feats/skilled.md)

## Equipment

### Weapons
| Weapon | Attack | Damage | Properties |
|--------|--------|--------|------------|
| [Dagger](../../books/reference/equipment/weapons/dagger.md) | +5 | 1d4+3 piercing | Finesse, Light, Thrown (20/60), Nick |
| [Hand Crossbow](../../books/reference/equipment/weapons/hand-crossbow.md) | +5 | 1d6+3 piercing | Ammunition (30/120), Light, Loading, Vex |

### Armor
- [Leather Armor](../../books/reference/equipment/armor/leather.md) (AC 11 + Dex)

### Gear
- [Backpack](../../books/reference/equipment/gear/backpack.md)
- [Book](../../books/reference/equipment/gear/book.md)
- [Healer's Kit](../../books/reference/equipment/gear/healers-kit.md)
- [Herbalism Kit](../../books/reference/equipment/gear/herbalism-kit.md)
- [Thieves' Tools](../../books/reference/equipment/gear/thieves-tools.md)
- [Tinderbox](../../books/reference/equipment/gear/tinderbox.md)
- Torch (10)
- [Waterskin](../../books/reference/equipment/gear/waterskin.md)

### Currency
0 CP, 0 SP, 0 GP, 0 EP, 0 PP

## Personality

**Traits**: Writes everything down; hates missing data. Dry, clinical humor when tension spikes.

**Ideals**: Crew safety over reputation.

**Bonds**: The ledger page / mindersand trail: the proof she carries.

**Flaws**: Curiosity overrides comfort: If something doesn't make sense, I can't let it go—even when I should rest or keep quiet.

## Appearance

Meilin is compact and practical, reading as non-martial but capable—grounded stance, guarded shoulders, built for workspaces more than battle lines...

## Notes

### Allies
- Kaito Starwell (father; dockside apothecary anchor)
- Meredin Sandyfoot (fixer/patron; pragmatic protection)
...

### Organizations
- Meredin Sandyfoot's network (Burrows "coverage," off-books)
- Smith's Coster (trade/cargo power; paperwork weapon)
...

---

*Imported from D&D Beyond on 2026-01-28*  
*Source: https://www.dndbeyond.com/characters/157884334*
```

## DMG Encounter Building Guidelines

### XP Thresholds by Character Level

| Level | Easy | Medium | Hard | Deadly |
|-------|------|--------|------|--------|
| 1 | 25 | 50 | 75 | 100 |
| 2 | 50 | 100 | 150 | 200 |
| 3 | 75 | 150 | 225 | 400 |
| 4 | 125 | 250 | 375 | 500 |
| 5 | 250 | 500 | 750 | 1,100 |
| 6 | 300 | 600 | 900 | 1,400 |
| 7 | 350 | 750 | 1,100 | 1,700 |
| 8 | 450 | 900 | 1,400 | 2,100 |
| 9 | 550 | 1,100 | 1,600 | 2,400 |
| 10 | 600 | 1,200 | 1,900 | 2,800 |
| 11 | 800 | 1,600 | 2,400 | 3,600 |
| 12 | 1,000 | 2,000 | 3,000 | 4,500 |
| 13 | 1,100 | 2,200 | 3,400 | 5,100 |
| 14 | 1,250 | 2,500 | 3,800 | 5,700 |
| 15 | 1,400 | 2,800 | 4,300 | 6,400 |
| 16 | 1,600 | 3,200 | 4,800 | 7,200 |
| 17 | 2,000 | 3,900 | 5,900 | 8,800 |
| 18 | 2,100 | 4,200 | 6,300 | 9,500 |
| 19 | 2,400 | 4,900 | 7,300 | 10,900 |
| 20 | 2,800 | 5,700 | 8,500 | 12,700 |

### Encounter Multipliers

For multiple monsters, multiply total XP by:

| Number of Monsters | Multiplier |
|-------------------|------------|
| 1 | x1 |
| 2 | x1.5 |
| 3-6 | x2 |
| 7-10 | x2.5 |
| 11-14 | x3 |
| 15+ | x4 |

### Calculation Steps

1. Determine party XP threshold: Sum individual thresholds for each party member
2. Calculate adjusted encounter XP: (Sum of monster XP) × Multiplier
3. Compare adjusted XP to party thresholds to determine difficulty

## Reference Data Linking

### Name-to-Path Resolution

Use `books/reference-index.json` for lookups:

```json
{
  "name": "Fireball",
  "type": "spell",
  "path": "reference/spells/3rd-level/fireball.md"
}
```

### Link Format

Links should be relative from character sheet location:

- Character at: `campaign/party/characters/meilin-starwell.md`
- Reference at: `books/reference/spells/3rd-level/fireball.md`
- Link: `../../books/reference/spells/3rd-level/fireball.md`
