# Quickstart: Loot Generator

Generate D&D 5e treasure using DMG 2024 tables.

## Prerequisites

- Reference data extracted (`make` if not already done)
- Python 3.11+

## Basic Usage

### Individual Treasure (Coins Only)

Generate coins for defeated creatures:

```bash
# Single CR 3 creature
python scripts/campaign/loot_generator.py individual --cr 3

# Four CR 5 creatures
python scripts/campaign/loot_generator.py individual --cr 5 --count 4
```

### Treasure Hoard (Full Treasure)

Generate coins, gems, art objects, and magic items:

```bash
# CR 7 hoard
python scripts/campaign/loot_generator.py hoard --cr 7

# CR 15 hoard
python scripts/campaign/loot_generator.py hoard --cr 15
```

### Magic Item Tables

Roll directly on magic item tables A-I:

```bash
# Roll once on Table C
python scripts/campaign/loot_generator.py magic-item --table C

# Roll 3 times on Table F
python scripts/campaign/loot_generator.py magic-item --table F --count 3
```

### Encounter-Based Loot

Generate loot based on a saved encounter (default is per-creature individual treasure):

```bash
# Per-creature individual treasure (default)
python scripts/campaign/loot_generator.py for-encounter "goblin-ambush"

# Single hoard instead
python scripts/campaign/loot_generator.py for-encounter "goblin-ambush" --hoard
```

## Session Integration

Append generated loot to a session's "Loot & Rewards" section:

```bash
# Generate hoard and add to session 3
python scripts/campaign/loot_generator.py hoard --cr 5 --add-to-session 3

# From encounter, add to session 5
python scripts/campaign/loot_generator.py for-encounter "dragon-lair" --add-to-session 5
```

## Reproducible Output

Use `--seed` for deterministic output (useful for testing or sharing):

```bash
python scripts/campaign/loot_generator.py hoard --cr 10 --seed 42
```

## CR Tiers

The generator uses DMG 2024 treasure tiers:

| CR Range | Tier | Treasure Level |
|----------|------|----------------|
| 0-4 | 1 | Low-level |
| 5-10 | 2 | Mid-level |
| 11-16 | 3 | High-level |
| 17+ | 4 | Epic-level |

Fractional CRs (1/8, 1/4, 1/2) are treated as Tier 1.

## Magic Item Tables

| Table | Contents | Typical Rarity |
|-------|----------|----------------|
| A | Potions, cantrip scrolls | Common |
| B | Potions, low-level scrolls | Common-Uncommon |
| C | Superior potions, mid-level scrolls | Uncommon |
| D | Supreme potions, high-level scrolls | Uncommon-Rare |
| E | Rare consumables | Rare |
| F | Uncommon permanent items | Uncommon |
| G | Rare permanent items | Rare |
| H | Very rare permanent items | Very Rare |
| I | Legendary items | Legendary |

## Example Output

```markdown
## Treasure Hoard (CR 5-10)

**Coins:** 170 pp, 1,600 gp, 7,000 sp, 700 cp

**Gems (10x 50 gp):**
- Bloodstone
- Carnelian
- Moonstone

**Magic Items:**
- [Potion of Healing](../../books/reference/items/potion-of-healing.md)
```

## Integration with Cursor AI

Ask the AI to generate loot naturally:

- *"Generate a hoard for the dragon encounter"*
- *"Roll on Magic Item Table F three times"*
- *"What treasure would CR 7 creatures have?"*
- *"Add this loot to session 5"*
