# Quickstart: Encounter Builder and Combat Tracker

**Feature**: 009-encounter-builder  
**Date**: 2026-02-02

## Prerequisites

Before using the encounter builder and combat tracker:

1. **Web UI running**: Start the backend and frontend servers
   ```bash
   make web-ui
   ```

2. **Reference data extracted**: Ensure creature data is available
   ```bash
   make extract
   ```

3. **Campaign initialized** (optional but recommended): For party integration
   ```bash
   python scripts/campaign/init_campaign.py "Your Campaign Name"
   ```

## Using the Encounter Builder

### Build a New Encounter

1. Navigate to **Encounters** in the sidebar
2. Click **"Build New Encounter"**
3. Configure party settings (or accept auto-detected values from campaign)
4. Use the creature search to find creatures by name
5. Click creatures to add them to the encounter
6. Adjust quantities with +/- buttons
7. Watch the difficulty indicator update in real-time
8. Enter a name and click **"Save"**

### Edit an Existing Encounter

1. Navigate to **Encounters** → select an encounter
2. Click **"Edit"** button
3. Modify creatures, quantities, or party settings
4. Click **"Save"** to update

### Understanding Difficulty

The difficulty indicator uses DMG 2024 encounter building guidelines:

| Difficulty | Color | Meaning |
| ---------- | ----- | ------- |
| Easy | Green | Minor threat, resources unlikely to be expended |
| Medium | Blue | Moderate threat, some resource expenditure expected |
| Hard | Orange | Dangerous, could go badly without tactics |
| Deadly | Red | Could be lethal, high resource cost |

The XP display shows:
- **Base XP**: Raw XP from all creatures
- **Multiplier**: Based on number of creatures (1.0x to 4.0x)
- **Adjusted XP**: Base × Multiplier (used for difficulty)
- **Party Thresholds**: Reference values for comparison

## Using the Combat Tracker

### Start Combat

1. Open a saved encounter
2. Click **"Start Combat"**
3. Enter initiative for each combatant:
   - **Monsters**: Click "Roll" to auto-roll, or enter manually
   - **Players**: Enter the player's rolled value
4. Click **"Begin Combat"** to start

### Running Combat

The initiative list shows all combatants sorted by initiative (highest first).

**Current Turn**: Highlighted combatant with yellow border

**Apply Damage**:
1. Click a combatant
2. Enter damage amount
3. Optionally enter source (e.g., "Fireball")
4. Click **"Apply Damage"**

**Apply Healing**:
1. Click a combatant
2. Enter healing amount
3. Click **"Heal"**

**Add Temp HP**:
1. Click a combatant
2. Enter temp HP amount
3. Click **"Add Temp HP"**

**Advance Turn**:
- Click **"Next Turn"** to move to next combatant
- Click **"Previous Turn"** to go back (for corrections)
- Round counter increments when cycling back to top

**Apply Conditions**:
1. Click a combatant
2. Toggle condition badges (Stunned, Poisoned, Prone, etc.)

### Viewing Damage History

The damage history panel shows all events grouped by round:

```
Round 1
  Turn 1: Goblin 1 took 8 damage (Longsword)
  Turn 2: Goblin 2 took 12 damage (Fireball)
Round 2
  Turn 0: Meilin healed for 8 (Cure Wounds)
```

### End Combat

1. Click **"End Combat"** when finished
2. Combat state is archived
3. Redirected to encounter detail page

### Resume Combat

If you close the browser or navigate away during combat:

1. Navigate to **Encounters**
2. Look for **"Resume Combat"** badge on the encounter
3. Click the encounter → Click **"Resume Combat"**
4. Combat continues from where you left off

## API Endpoints

### Encounter Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/encounters` | List all saved encounters |
| GET | `/api/encounters/{slug}` | Get encounter details |
| POST | `/api/encounters` | Create new encounter |
| PUT | `/api/encounters/{slug}` | Update existing encounter |

### Combat Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/api/combat/{slug}` | Get combat state (if exists) |
| POST | `/api/combat/{slug}` | Start new combat from encounter |
| PUT | `/api/combat/{slug}` | Update combat state |
| DELETE | `/api/combat/{slug}` | End combat, archive state |

### Example: Start Combat

```bash
# Start combat for an encounter
curl -X POST http://localhost:8000/api/combat/goblin-ambush \
  -H "Content-Type: application/json" \
  -d '{"include_party": true}'
```

### Example: Apply Damage

```bash
# Apply 8 damage to a combatant
curl -X PUT http://localhost:8000/api/combat/goblin-ambush \
  -H "Content-Type: application/json" \
  -d '{
    "action": "damage",
    "target_id": "goblin-1",
    "amount": 8,
    "source": "Longsword"
  }'
```

## File Locations

| File | Purpose |
| ---- | ------- |
| `campaign/encounters/{name}.md` | Saved encounter definitions |
| `campaign/encounters/combat-{name}.json` | Active combat state |
| `campaign/party/characters/*.md` | Party character sheets (for HP) |
| `books/reference-index.json` | Creature reference data |

## Troubleshooting

### "No creatures found"

- Ensure reference data is extracted: `make extract`
- Check that `books/reference-index.json` exists

### Party not loading

- Ensure campaign is initialized: `python scripts/campaign/init_campaign.py`
- Import characters: `python scripts/campaign/import_character.py <url>`

### Combat state not persisting

- Check that `campaign/encounters/` directory exists and is writable
- Look for `combat-{slug}.json` files in that directory

### Difficulty seems wrong

- Verify party level and size are correct
- Check that creature CR values are in the reference index
- Compare XP values against DMG tables manually
