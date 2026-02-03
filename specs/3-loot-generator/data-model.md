# Data Model: Loot Generator

**Feature**: Loot Generator  
**Spec**: [spec.md](spec.md)

## Entity Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Treasure                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ coins: dict[str, int]  # {"cp": 100, "gp": 50}              ││
│  │ gems: list[Gem]                                              ││
│  │ art_objects: list[ArtObject]                                 ││
│  │ magic_items: list[MagicItem]                                 ││
│  │ source_cr: float | None  # CR used for generation           ││
│  │ treasure_type: str  # "individual" | "hoard"                 ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
         │
         ├──────────────┬───────────────┬───────────────┐
         ▼              ▼               ▼               ▼
┌─────────────┐  ┌───────────┐  ┌─────────────┐  ┌─────────────┐
│    Coin     │  │    Gem    │  │  ArtObject  │  │  MagicItem  │
│ ─────────── │  │ ───────── │  │ ─────────── │  │ ─────────── │
│ type: str   │  │ value: int│  │ value: int  │  │ name: str   │
│ amount: int │  │ name: str │  │ name: str   │  │ rarity: str │
└─────────────┘  └───────────┘  └─────────────┘  │ table: str  │
                                                  │ link: str   │
                                                  └─────────────┘
```

## Core Entities

### Treasure

The top-level container for generated loot.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| coins | dict[str, int] | Yes | Coins by type (cp, sp, ep, gp, pp) |
| gems | list[Gem] | Yes | Gemstones with value and name |
| art_objects | list[ArtObject] | Yes | Art objects with value and description |
| magic_items | list[MagicItem] | Yes | Magic items with reference links |
| source_cr | float | None | No | CR used for generation (for display) |
| treasure_type | str | Yes | "individual" or "hoard" |

**Example**:

```python
Treasure(
    coins={"cp": 600, "sp": 300, "gp": 20},
    gems=[(50, "Moonstone"), (50, "Onyx")],
    art_objects=[(25, "Silver ewer")],
    magic_items=[MagicItem(name="Potion of Healing", table="A")],
    source_cr=4.0,
    treasure_type="hoard"
)
```

### Coin

Currency component of treasure.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | str | Yes | Currency type: cp, sp, ep, gp, pp |
| amount | int | Yes | Number of coins |

**Coin Types** (in ascending value):

| Type | Name | Value in GP |
|------|------|-------------|
| cp | Copper pieces | 1/100 gp |
| sp | Silver pieces | 1/10 gp |
| ep | Electrum pieces | 1/2 gp |
| gp | Gold pieces | 1 gp |
| pp | Platinum pieces | 10 gp |

### Gem

Precious stone with monetary value.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| value | int | Yes | Value in gold pieces (10, 50, 100, 500, 1000, 5000) |
| name | str | Yes | Specific gem name (e.g., "Moonstone", "Ruby") |

**Gem Value Tiers**:

| Value | Example Gems |
|-------|--------------|
| 10 gp | Azurite, Banded agate, Blue quartz, Tiger eye, Turquoise |
| 50 gp | Bloodstone, Carnelian, Moonstone, Onyx, Star rose quartz |
| 100 gp | Amber, Amethyst, Coral, Garnet, Jade, Pearl |
| 500 gp | Alexandrite, Aquamarine, Black pearl, Topaz |
| 1000 gp | Black opal, Emerald, Fire opal, Star ruby, Star sapphire |
| 5000 gp | Black sapphire, Diamond, Jacinth, Ruby |

### ArtObject

Valuable artwork, jewelry, or decorative item.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| value | int | Yes | Value in gold pieces (25, 250, 750, 2500, 7500) |
| name | str | Yes | Description of the object |

**Art Object Value Tiers**:

| Value | Example Objects |
|-------|-----------------|
| 25 gp | Silver ewer, Carved bone statuette, Small gold bracelet |
| 250 gp | Gold ring set with bloodstones, Carved ivory statuette |
| 750 gp | Silver chalice set with moonstones, Gold dragon comb |
| 2500 gp | Fine gold chain set with fire opal, Old masterpiece painting |
| 7500 gp | Jeweled gold crown, Jeweled platinum ring |

### MagicItem

Magic item reference with linking support.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | str | Yes | Item name (e.g., "Potion of Healing") |
| rarity | str | No | Rarity if known (common, uncommon, rare, very rare, legendary) |
| table | str | No | Source table (A-I) if from hoard roll |
| link | str | No | Relative path to reference file |

**Magic Item Tables**:

| Table | Contents | Typical Rarity |
|-------|----------|----------------|
| A | Minor consumables (potions, low-level scrolls) | Common |
| B | Minor consumables (potions, scrolls, ammunition) | Common-Uncommon |
| C | Minor permanent items (potions, scrolls, tokens) | Uncommon |
| D | Minor permanent items (high-level potions, scrolls) | Uncommon-Rare |
| E | Major permanent items (high-level scrolls, rare items) | Rare |
| F | Uncommon permanent items (weapons, armor, wondrous) | Uncommon |
| G | Rare permanent items (weapons, armor, wondrous) | Rare |
| H | Very rare permanent items | Very Rare |
| I | Legendary items | Legendary |

## Supporting Data Structures

### DiceRoll

Represents a dice expression for treasure generation.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| count | int | Yes | Number of dice to roll |
| sides | int | Yes | Number of sides per die |
| multiplier | int | No | Multiplier for result (default: 1) |

**Examples**:

```python
DiceRoll(5, 6)           # 5d6
DiceRoll(2, 6, 100)      # 2d6 × 100
DiceRoll(3, 6, 10)       # 3d6 × 10
```

### CRTier

Maps Challenge Rating ranges to treasure table tiers.

| Tier | CR Range | Description |
|------|----------|-------------|
| 1 | 0-4 | Low-level treasure (includes fractional CRs) |
| 2 | 5-10 | Mid-level treasure |
| 3 | 11-16 | High-level treasure |
| 4 | 17+ | Epic-level treasure |

### IndividualTreasureRow

A row in the individual treasure table.

| Field | Type | Description |
|-------|------|-------------|
| max_roll | int | d100 threshold (cumulative) |
| coins | dict[str, DiceRoll] | Coin types and dice to roll |

**Example** (CR 0-4 table):

```python
[
    IndividualTreasureRow(30, {"cp": DiceRoll(5, 6)}),
    IndividualTreasureRow(60, {"sp": DiceRoll(4, 6)}),
    IndividualTreasureRow(70, {"ep": DiceRoll(3, 6)}),
    IndividualTreasureRow(95, {"gp": DiceRoll(3, 6)}),
    IndividualTreasureRow(100, {"pp": DiceRoll(1, 6)}),
]
```

### HoardRow

A row in the hoard treasure table.

| Field | Type | Description |
|-------|------|-------------|
| max_roll | int | d100 threshold (cumulative) |
| gems_art | tuple | None | (type, value, count_dice) or None |
| magic_items | list[tuple] | None | [(table, count_dice), ...] or None |

**Example**:

```python
HoardRow(
    max_roll=44,
    gems_art=("gems", 10, DiceRoll(2, 6)),
    magic_items=[("A", DiceRoll(1, 6))]
)
```

### MagicItemTableRow

A row in a magic item table.

| Field | Type | Description |
|-------|------|-------------|
| max_roll | int | d100 threshold (cumulative) |
| item_name | str | Name of the magic item |

## Output Formats

### Console/Markdown Format

```markdown
## Treasure Hoard (CR 5-10)

**Coins:** 70 pp, 700 gp, 1,400 sp, 2,800 cp

**Gems (3x 50 gp):**
- Moonstone
- Onyx
- Star rose quartz

**Magic Items:**
- [Potion of Healing](../../books/reference/items/potion-of-healing.md)
```

### Session Integration Format

When appended to session files, the format includes a divider:

```markdown
## Loot & Rewards

*List any treasure, items, or rewards gained*

---

### Treasure (Goblin Ambush)

**Coins:** 15 gp, 30 sp

**Magic Items:**
- [Potion of Healing](../../books/reference/items/potion-of-healing.md)
```

## Relationship to Existing Entities

### Character (from Spec 1)

Characters may reference magic items from their equipment that were generated as loot.

### Session (from Spec 1)

Sessions contain a "Loot & Rewards" section where generated treasure can be recorded.

### Encounter (from Spec 1)

Encounters provide CR context for loot generation. The loot generator reads encounter files to determine appropriate treasure tier.

## Data Validation Rules

| Entity | Rule |
|--------|------|
| Treasure | coins must contain only valid types (cp, sp, ep, gp, pp) |
| Treasure | coin amounts must be >= 0 |
| Gem | value must be in [10, 50, 100, 500, 1000, 5000] |
| ArtObject | value must be in [25, 250, 750, 2500, 7500] |
| MagicItem | table must be A-I if specified |
| CRTier | CR must be >= 0 |

## No Persistent Storage

Unlike Characters, Sessions, NPCs, and Locations from Spec 1, **Treasure is ephemeral by default**. Generated treasure is:

1. Displayed to console
2. Optionally appended to a session file
3. Not stored as a separate entity

This matches the DM workflow: treasure is generated, awarded to players, and tracked in session notes or on character sheets - not as a standalone campaign entity.
