# Implementation Plan: Loot Generator

**Feature**: Loot Generator  
**Spec**: [spec.md](spec.md)  
**Research**: [research.md](research.md)  
**Data Model**: [data-model.md](data-model.md)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     loot_generator.py                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ CLI Parser  │  │ Dice Roller │  │ Treasure Tables (embed) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                │                      │               │
│         ▼                ▼                      ▼               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    LootGenerator Class                      ││
│  │  - generate_individual(cr, count, seed)                     ││
│  │  - generate_hoard(cr, seed)                                 ││
│  │  - roll_magic_item_table(table, count)                      ││
│  │  - generate_for_encounter(encounter_file)                   ││
│  └─────────────────────────────────────────────────────────────┘│
│         │                │                      │               │
│         ▼                ▼                      ▼               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Formatter  │  │   Linker    │  │    Session Writer       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                │                      │
         ▼                ▼                      ▼
   Console Output   reference/items/     campaign/sessions/
```

## Component Design

### 1. CLI Interface (argparse)

Command structure following existing patterns:

```bash
# Subcommands
python scripts/campaign/loot_generator.py individual --cr 3 [--count 5] [--seed 42]
python scripts/campaign/loot_generator.py hoard --cr 7 [--seed 42]
python scripts/campaign/loot_generator.py magic-item --table C [--count 3]
python scripts/campaign/loot_generator.py for-encounter "goblin-ambush" [--individual]
python scripts/campaign/loot_generator.py hoard --cr 5 --add-to-session 3
```

### 2. Dice Roller Module

```python
@dataclass
class DiceRoll:
    count: int
    sides: int
    multiplier: int = 1

def roll_dice(dice: DiceRoll, rng: random.Random) -> int:
    """Roll dice and return total."""
    total = sum(rng.randint(1, dice.sides) for _ in range(dice.count))
    return total * dice.multiplier

def roll_d100(rng: random.Random) -> int:
    """Roll d100 (01-00 = 1-100)."""
    return rng.randint(1, 100)
```

### 3. Embedded Treasure Tables

Data structures for tables (embedded, not loaded from files):

```python
# CR tier boundaries
CR_TIERS = {
    (0, 4): 1,
    (5, 10): 2,
    (11, 16): 3,
    (17, 30): 4,
}

# Individual treasure tables by tier
INDIVIDUAL_TREASURE = {
    1: [  # CR 0-4
        (30, {"cp": DiceRoll(5, 6)}),
        (60, {"sp": DiceRoll(4, 6)}),
        (70, {"ep": DiceRoll(3, 6)}),
        (95, {"gp": DiceRoll(3, 6)}),
        (100, {"pp": DiceRoll(1, 6)}),
    ],
    # ... tiers 2-4
}

# Hoard base coins by tier
HOARD_COINS = {
    1: {"cp": DiceRoll(6, 6, 100), "sp": DiceRoll(3, 6, 100), "gp": DiceRoll(2, 6, 10)},
    # ... tiers 2-4
}

# Hoard additional table by tier (d100 ranges -> gems/art + magic items)
HOARD_TABLES = {
    1: [
        (6, None, None),  # Nothing extra
        (16, ("gems", 10, DiceRoll(2, 6)), None),
        (26, ("art", 25, DiceRoll(2, 4)), None),
        # ... etc
    ],
    # ... tiers 2-4
}

# Gem lists by value
GEMS = {
    10: ["Azurite", "Banded agate", "Blue quartz", ...],
    50: ["Bloodstone", "Carnelian", "Chalcedony", ...],
    # ... etc
}

# Art object lists by value
ART_OBJECTS = {
    25: ["Silver ewer", "Carved bone statuette", ...],
    250: ["Gold ring set with bloodstones", ...],
    # ... etc
}

# Magic item tables A-I
MAGIC_ITEM_TABLES = {
    "A": [
        (50, "Potion of Healing"),
        (60, "Spell Scroll (Cantrip)"),
        # ...
    ],
    # ... tables B-I
}
```

### 4. LootGenerator Class

```python
@dataclass
class Treasure:
    coins: dict[str, int]  # {"cp": 100, "sp": 50, "gp": 25}
    gems: list[tuple[int, str]]  # [(50, "Moonstone"), (50, "Onyx")]
    art_objects: list[tuple[int, str]]  # [(250, "Gold ring")]
    magic_items: list[str]  # ["Potion of Healing", "+1 Weapon"]

class LootGenerator:
    def __init__(self, reference_index_path: str | None = None, seed: int | None = None):
        self.rng = random.Random(seed)
        self.linker = ReferenceLinker(reference_index_path) if reference_index_path else None
    
    def get_cr_tier(self, cr: float) -> int:
        """Convert CR to tier (1-4)."""
        for (min_cr, max_cr), tier in CR_TIERS.items():
            if min_cr <= cr <= max_cr:
                return tier
        return 4  # Default to highest tier for CR > 30
    
    def generate_individual(self, cr: float, count: int = 1) -> Treasure:
        """Generate individual treasure for count creatures."""
        tier = self.get_cr_tier(cr)
        coins = {"cp": 0, "sp": 0, "ep": 0, "gp": 0, "pp": 0}
        
        for _ in range(count):
            roll = self.rng.randint(1, 100)
            for threshold, coin_dice in INDIVIDUAL_TREASURE[tier]:
                if roll <= threshold:
                    for coin_type, dice in coin_dice.items():
                        coins[coin_type] += roll_dice(dice, self.rng)
                    break
        
        return Treasure(coins=coins, gems=[], art_objects=[], magic_items=[])
    
    def generate_hoard(self, cr: float) -> Treasure:
        """Generate a treasure hoard."""
        tier = self.get_cr_tier(cr)
        
        # Roll base coins
        coins = {}
        for coin_type, dice in HOARD_COINS[tier].items():
            coins[coin_type] = roll_dice(dice, self.rng)
        
        # Roll for gems/art and magic items
        roll = self.rng.randint(1, 100)
        gems = []
        art_objects = []
        magic_items = []
        
        for threshold, gem_art_info, magic_info in HOARD_TABLES[tier]:
            if roll <= threshold:
                # Handle gems/art
                if gem_art_info:
                    item_type, value, count_dice = gem_art_info
                    count = roll_dice(count_dice, self.rng)
                    items = self._select_gems_or_art(item_type, value, count)
                    if item_type == "gems":
                        gems = items
                    else:
                        art_objects = items
                
                # Handle magic items
                if magic_info:
                    table, count_dice = magic_info
                    count = roll_dice(count_dice, self.rng) if count_dice else 1
                    magic_items = self.roll_magic_item_table(table, count)
                
                break
        
        return Treasure(coins=coins, gems=gems, art_objects=art_objects, magic_items=magic_items)
    
    def roll_magic_item_table(self, table: str, count: int = 1) -> list[str]:
        """Roll on a specific magic item table."""
        items = []
        for _ in range(count):
            roll = self.rng.randint(1, 100)
            for threshold, item_name in MAGIC_ITEM_TABLES[table.upper()]:
                if roll <= threshold:
                    items.append(item_name)
                    break
        return items
    
    def _select_gems_or_art(self, item_type: str, value: int, count: int) -> list[tuple[int, str]]:
        """Select random gems or art objects."""
        pool = GEMS[value] if item_type == "gems" else ART_OBJECTS[value]
        return [(value, self.rng.choice(pool)) for _ in range(count)]
```

### 5. Output Formatter

```python
class TreasureFormatter:
    def __init__(self, linker: ReferenceLinker | None = None):
        self.linker = linker
    
    def format_console(self, treasure: Treasure, title: str = "Treasure") -> str:
        """Format treasure for console output."""
        lines = [f"## {title}", ""]
        
        # Coins
        coin_parts = []
        for coin_type in ["pp", "gp", "ep", "sp", "cp"]:
            if treasure.coins.get(coin_type, 0) > 0:
                coin_parts.append(f"{treasure.coins[coin_type]:,} {coin_type}")
        if coin_parts:
            lines.append(f"**Coins:** {', '.join(coin_parts)}")
            lines.append("")
        
        # Gems
        if treasure.gems:
            by_value = {}
            for value, name in treasure.gems:
                by_value.setdefault(value, []).append(name)
            for value, names in sorted(by_value.items()):
                lines.append(f"**Gems ({len(names)}x {value} gp):**")
                for name in names:
                    lines.append(f"- {name}")
            lines.append("")
        
        # Art Objects
        if treasure.art_objects:
            by_value = {}
            for value, name in treasure.art_objects:
                by_value.setdefault(value, []).append(name)
            for value, names in sorted(by_value.items()):
                lines.append(f"**Art Objects ({len(names)}x {value} gp):**")
                for name in names:
                    lines.append(f"- {name}")
            lines.append("")
        
        # Magic Items
        if treasure.magic_items:
            lines.append("**Magic Items:**")
            for item in treasure.magic_items:
                if self.linker:
                    link = self.linker.link_item(item)
                    lines.append(f"- {link if link else item}")
                else:
                    lines.append(f"- {item}")
            lines.append("")
        
        return "\n".join(lines)
    
    def format_markdown(self, treasure: Treasure, title: str = "Treasure") -> str:
        """Format treasure for markdown file output (same as console for now)."""
        return self.format_console(treasure, title)
```

### 6. Session Integration

```python
def append_to_session(session_number: int, treasure_md: str, campaign_dir: Path) -> None:
    """Append treasure to a session's Loot & Rewards section."""
    session_file = campaign_dir / "sessions" / f"session-{session_number:03d}.md"
    
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    
    content = session_file.read_text()
    
    # Find the "Loot & Rewards" section
    loot_header = "## Loot & Rewards"
    if loot_header in content:
        # Insert after the header and any existing content before next section
        insert_pos = content.find(loot_header) + len(loot_header)
        # Find next section or end
        next_section = content.find("\n## ", insert_pos)
        if next_section == -1:
            next_section = len(content)
        
        # Insert treasure before next section
        new_content = (
            content[:next_section].rstrip() + 
            "\n\n" + treasure_md.strip() + "\n\n" + 
            content[next_section:].lstrip()
        )
    else:
        # Add the section at the end
        new_content = content.rstrip() + f"\n\n{loot_header}\n\n{treasure_md.strip()}\n"
    
    session_file.write_text(new_content)
```

### 7. Encounter Integration

```python
def load_encounter_cr(encounter_name: str, campaign_dir: Path) -> float:
    """Load CR from an encounter file."""
    encounter_file = campaign_dir / "encounters" / f"{slugify(encounter_name)}.md"
    
    if not encounter_file.exists():
        raise FileNotFoundError(f"Encounter not found: {encounter_file}")
    
    content = encounter_file.read_text()
    
    # Parse CR from encounter file
    # Look for highest CR creature or use total XP to estimate
    cr_pattern = r"\| .*? \| CR (\d+(?:/\d+)?) \|"
    matches = re.findall(cr_pattern, content)
    
    if matches:
        # Return highest CR found
        return max(parse_cr(cr) for cr in matches)
    
    # Fallback: estimate from XP
    xp_pattern = r"Total XP[:\s]+(\d+)"
    xp_match = re.search(xp_pattern, content)
    if xp_match:
        return xp_to_cr(int(xp_match.group(1)))
    
    raise ValueError(f"Could not determine CR from encounter: {encounter_name}")

def parse_cr(cr_str: str) -> float:
    """Parse CR string to float (e.g., '1/2' -> 0.5)."""
    if "/" in cr_str:
        num, den = cr_str.split("/")
        return int(num) / int(den)
    return float(cr_str)
```

## File Structure

```
scripts/
├── campaign/
│   ├── loot_generator.py      # NEW: Main module
│   └── ... (existing files)
├── lib/
│   ├── reference_linker.py    # EXISTING: Used for item linking
│   └── markdown_writer.py     # EXISTING: Used for formatting
tests/
└── test_loot_generator.py     # NEW: Unit tests
```

## Integration Points

### Reference Linker

Use existing `ReferenceLinker` from `scripts/lib/reference_linker.py`:

```python
from lib.reference_linker import ReferenceLinker

linker = ReferenceLinker("books/reference-index.json")
link = linker.link("Potion of Healing", "item")
# Returns: "[Potion of Healing](../../books/reference/items/potion-of-healing.md)"
```

### Markdown Writer

Use existing utilities from `scripts/lib/markdown_writer.py`:

```python
from lib.markdown_writer import heading, bold, slugify
```

### Session Manager

Follow patterns from `scripts/campaign/session_manager.py` for session file handling.

### Encounter Builder

Follow patterns from `scripts/campaign/encounter_builder.py` for:
- CR parsing
- Encounter file format
- CLI argument structure

## Error Handling

| Error Condition | Response |
|-----------------|----------|
| Invalid CR format | "Error: Invalid CR. Use 0-30 or fractions (1/8, 1/4, 1/2)" |
| Invalid table letter | "Error: Invalid magic item table. Use A-I" |
| Encounter not found | "Error: Encounter file not found: {path}" |
| Session not found | "Error: Session file not found: {path}" |
| No reference index | Warning only; output items without links |

## Testing Strategy

### Unit Tests

```python
def test_individual_treasure_cr_0_4():
    """Individual treasure for low CR uses correct table."""
    gen = LootGenerator(seed=42)
    treasure = gen.generate_individual(cr=2)
    assert any(treasure.coins.values())

def test_hoard_deterministic():
    """Same seed produces same hoard."""
    gen1 = LootGenerator(seed=123)
    gen2 = LootGenerator(seed=123)
    assert gen1.generate_hoard(5) == gen2.generate_hoard(5)

def test_magic_item_table_a():
    """Table A contains expected items."""
    gen = LootGenerator(seed=50)
    items = gen.roll_magic_item_table("A", count=1)
    assert items[0] in ["Potion of Healing", "Spell Scroll (Cantrip)", ...]

def test_cr_tier_mapping():
    """CR values map to correct tiers."""
    gen = LootGenerator()
    assert gen.get_cr_tier(0.125) == 1  # CR 1/8
    assert gen.get_cr_tier(3) == 1
    assert gen.get_cr_tier(7) == 2
    assert gen.get_cr_tier(14) == 3
    assert gen.get_cr_tier(20) == 4
```

### Integration Tests

```python
def test_encounter_loot_integration():
    """Generate loot from saved encounter file."""
    # Create mock encounter file
    # Generate loot
    # Verify CR detected correctly

def test_session_append():
    """Append loot to session file."""
    # Create mock session file
    # Append loot
    # Verify section updated correctly
```

## Performance Considerations

- All operations should complete in <1 second for console output
- Dice rolls use Python's random module (fast)
- Reference linking uses cached index (already loaded)
- No file I/O for treasure generation itself

## Dependencies

### Python Standard Library

- `random` - Dice rolling
- `argparse` - CLI parsing
- `dataclasses` - Data structures
- `re` - Pattern matching for encounter parsing
- `pathlib` - File path handling

### Project Dependencies

- `scripts/lib/reference_linker.py` - Item linking
- `scripts/lib/markdown_writer.py` - Formatting utilities
