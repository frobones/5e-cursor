# Tasks: Loot Generator

**Feature**: Loot Generator  
**Spec**: [spec.md](spec.md)  
**Plan**: [plan.md](plan.md)  
**Data Model**: [data-model.md](data-model.md)

## Phase 1: Core Infrastructure

- [X] **Task 1.1**: Create `scripts/campaign/loot_generator.py` with module structure
  - Imports and path setup (matching encounter_builder.py pattern)
  - Module docstring with usage examples
  - Empty main() function with argparse skeleton

- [X] **Task 1.2**: Implement DiceRoll dataclass and roll_dice function
  - DiceRoll dataclass with count, sides, multiplier
  - roll_dice(dice, rng) function
  - roll_d100(rng) function
  - Support for seeded random.Random instance

- [X] **Task 1.3**: Implement CR tier mapping
  - CR_TIERS dictionary mapping ranges to tiers 1-4
  - get_cr_tier(cr) function
  - parse_cr(cr_str) function for "1/2", "1/4", "1/8" handling

**Checkpoint**: Can instantiate module, roll dice deterministically, and map CRs to tiers.

## Phase 2: Treasure Tables (Embedded Data)

- [X] **Task 2.1**: Embed individual treasure tables
  - INDIVIDUAL_TREASURE dictionary by tier
  - Each tier: list of (threshold, coin_dice) tuples
  - All four tiers (CR 0-4, 5-10, 11-16, 17+)

- [X] **Task 2.2**: Embed hoard base coins
  - HOARD_COINS dictionary by tier
  - Each tier: dict of coin types to DiceRoll

- [X] **Task 2.3**: Embed hoard gem/art/magic item tables
  - HOARD_TABLES dictionary by tier
  - Each tier: list of (threshold, gems_art_info, magic_info) tuples

- [X] **Task 2.4**: Embed gem name lists by value
  - GEMS dictionary: value -> list of gem names
  - All six value tiers (10, 50, 100, 500, 1000, 5000 gp)

- [X] **Task 2.5**: Embed art object lists by value
  - ART_OBJECTS dictionary: value -> list of descriptions
  - All five value tiers (25, 250, 750, 2500, 7500 gp)

- [X] **Task 2.6**: Embed magic item tables A-I
  - MAGIC_ITEM_TABLES dictionary: letter -> list of (threshold, item_name)
  - All nine tables (A through I)

**Checkpoint**: All DMG 2024 treasure tables embedded and accessible.

## Phase 3: Core Generation Logic

- [X] **Task 3.1**: Implement Treasure dataclass
  - coins: dict[str, int]
  - gems: list[tuple[int, str]]
  - art_objects: list[tuple[int, str]]
  - magic_items: list[str]
  - Optional metadata fields

- [X] **Task 3.2**: Implement LootGenerator class skeleton
  - __init__(reference_index_path, seed)
  - Initialize random.Random with seed
  - Initialize ReferenceLinker if path provided

- [X] **Task 3.3**: Implement generate_individual(cr, count)
  - Determine tier from CR
  - Roll on individual treasure table per creature
  - Accumulate coins across count creatures
  - Return Treasure object

- [X] **Task 3.4**: Implement generate_hoard(cr)
  - Determine tier from CR
  - Roll base coins
  - Roll d100 for gems/art and magic items
  - Select specific gems/art names
  - Roll on magic item tables as needed
  - Return Treasure object

- [X] **Task 3.5**: Implement roll_magic_item_table(table, count)
  - Validate table letter (A-I)
  - Roll d100 for each item
  - Return list of item names

- [X] **Task 3.6**: Implement _select_gems_or_art helper
  - Random selection from value-appropriate pool
  - Return list of (value, name) tuples

**Checkpoint**: Can generate individual treasure, hoards, and magic items programmatically.

## Phase 4: Output Formatting

- [X] **Task 4.1**: Implement TreasureFormatter class
  - __init__(linker: ReferenceLinker | None)
  - format_console(treasure, title) -> str
  - format_markdown(treasure, title) -> str

- [X] **Task 4.2**: Format coins output
  - Order: pp, gp, ep, sp, cp (descending value)
  - Format with thousands separators
  - Skip zero amounts

- [X] **Task 4.3**: Format gems output
  - Group by value
  - List individual gem names
  - Format: "**Gems (3x 50 gp):**" then bullet list

- [X] **Task 4.4**: Format art objects output
  - Group by value
  - List individual descriptions
  - Format: "**Art Objects (2x 250 gp):**" then bullet list

- [X] **Task 4.5**: Format magic items with reference links
  - Use ReferenceLinker to generate links
  - Fall back to plain text if no link found
  - Add "[No Reference]" marker if not found

**Checkpoint**: Treasure outputs as readable, formatted markdown.

## Phase 5: CLI Interface

- [X] **Task 5.1**: Implement argparse with subcommands
  - `individual` subcommand with --cr, --count, --seed
  - `hoard` subcommand with --cr, --seed, --add-to-session
  - `magic-item` subcommand with --table, --count, --seed
  - `for-encounter` subcommand with encounter name, --individual

- [X] **Task 5.2**: Implement `individual` command handler
  - Parse and validate CR
  - Generate treasure
  - Print formatted output

- [X] **Task 5.3**: Implement `hoard` command handler
  - Parse and validate CR
  - Generate treasure
  - Print formatted output
  - Optional session integration

- [X] **Task 5.4**: Implement `magic-item` command handler
  - Validate table letter
  - Roll specified count times
  - Print items with links

- [X] **Task 5.5**: Add --help documentation for all commands
  - Clear descriptions
  - Usage examples in epilog

**Checkpoint**: Full CLI works for individual, hoard, and magic-item commands.

## Phase 6: Encounter Integration

- [X] **Task 6.1**: Implement load_encounter_cr(encounter_name)
  - Find encounter file in campaign/encounters/
  - Parse CR from creature table
  - Return highest CR or estimate from XP

- [X] **Task 6.2**: Implement `for-encounter` command handler
  - Load encounter file
  - Determine CR
  - Generate hoard (or individual with --individual flag)
  - Print formatted output

- [X] **Task 6.3**: Handle encounter file not found
  - Clear error message
  - List available encounters

**Checkpoint**: Can generate loot directly from saved encounters.

## Phase 7: Session Integration

- [X] **Task 7.1**: Implement find_loot_section(session_content)
  - Locate "## Loot & Rewards" section
  - Return position or None

- [X] **Task 7.2**: Implement append_to_session(session_number, treasure_md)
  - Load session file
  - Find or create Loot & Rewards section
  - Append treasure with separator
  - Write updated file

- [X] **Task 7.3**: Handle session file not found
  - Clear error message
  - Suggest creating session first

- [X] **Task 7.4**: Add --add-to-session to hoard and for-encounter commands
  - Accept session number
  - Append after printing to console

**Checkpoint**: Generated loot can be saved to session files.

## Phase 8: Testing

- [X] **Task 8.1**: Create `tests/test_loot_generator.py`
  - Test imports and module structure

- [X] **Task 8.2**: Test dice rolling
  - Deterministic with seed
  - Correct range for various dice

- [X] **Task 8.3**: Test CR tier mapping
  - Fractional CRs (1/8, 1/4, 1/2)
  - Boundary values (4, 5, 10, 11, 16, 17)

- [X] **Task 8.4**: Test individual treasure generation
  - Each CR tier
  - Count multiplier
  - Deterministic output with seed

- [X] **Task 8.5**: Test hoard generation
  - Each CR tier
  - Contains expected components
  - Deterministic output with seed

- [X] **Task 8.6**: Test magic item table rolls
  - Each table A-I
  - Items are valid table entries
  - Deterministic output with seed

- [X] **Task 8.7**: Test output formatting
  - Coins formatted correctly
  - Gems grouped by value
  - Items have links when available

- [X] **Task 8.8**: Test session integration
  - Appending to existing section
  - Creating new section
  - Preserving existing content

**Checkpoint**: All tests pass; feature is fully validated.

## Phase 9: Documentation & Polish

- [X] **Task 9.1**: Add module docstring with comprehensive usage
  - All commands with examples
  - Seed usage for reproducibility

- [X] **Task 9.2**: Add loot_generator.py to campaign module __init__.py
  - Export main classes/functions

- [X] **Task 9.3**: Update campaign-lookup.mdc rule with loot commands
  - Add loot generation examples
  - Document output locations

- [X] **Task 9.4**: Create quickstart.md for loot generator
  - Installation prerequisites
  - Basic usage workflow
  - Integration with encounters and sessions

**Checkpoint**: Feature is documented and discoverable.

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 3 | Core infrastructure (module, dice, CR tiers) |
| 2 | 6 | Embed all treasure tables |
| 3 | 6 | Core generation logic |
| 4 | 5 | Output formatting |
| 5 | 5 | CLI interface |
| 6 | 3 | Encounter integration |
| 7 | 4 | Session integration |
| 8 | 8 | Testing |
| 9 | 4 | Documentation |
| **Total** | **44** | |
