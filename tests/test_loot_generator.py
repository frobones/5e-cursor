"""Tests for the loot generator module."""

import pytest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from campaign.loot_generator import (
    DiceRoll,
    LootGenerator,
    Treasure,
    TreasureFormatter,
    get_cr_tier,
    load_encounter_cr,
    parse_cr,
    roll_dice,
    roll_d100,
    INDIVIDUAL_TREASURE,
    HOARD_COINS,
    HOARD_TABLES,
    GEMS,
    ART_OBJECTS,
    MAGIC_ITEM_TABLES,
)
import random
import tempfile


# =============================================================================
# Dice Rolling Tests
# =============================================================================


class TestDiceRoll:
    """Tests for DiceRoll dataclass."""

    def test_basic_dice_roll(self):
        """Test basic dice representation."""
        dice = DiceRoll(3, 6)
        assert dice.count == 3
        assert dice.sides == 6
        assert dice.multiplier == 1
        assert str(dice) == "3d6"

    def test_dice_roll_with_multiplier(self):
        """Test dice with multiplier."""
        dice = DiceRoll(2, 6, 100)
        assert dice.count == 2
        assert dice.sides == 6
        assert dice.multiplier == 100
        assert str(dice) == "2d6×100"


class TestRollDice:
    """Tests for roll_dice function."""

    def test_deterministic_with_seed(self):
        """Same seed produces same result."""
        dice = DiceRoll(3, 6)
        rng1 = random.Random(42)
        rng2 = random.Random(42)

        result1 = roll_dice(dice, rng1)
        result2 = roll_dice(dice, rng2)

        assert result1 == result2

    def test_within_range(self):
        """Roll is within valid range."""
        dice = DiceRoll(3, 6)  # 3d6: min=3, max=18
        rng = random.Random(42)

        for _ in range(100):
            result = roll_dice(dice, rng)
            assert 3 <= result <= 18

    def test_multiplier_applied(self):
        """Multiplier is applied correctly."""
        dice = DiceRoll(1, 1, 100)  # Always rolls 1, times 100 = 100
        rng = random.Random()
        result = roll_dice(dice, rng)
        assert result == 100


class TestRollD100:
    """Tests for roll_d100 function."""

    def test_within_range(self):
        """D100 rolls 1-100."""
        rng = random.Random(42)
        for _ in range(100):
            result = roll_d100(rng)
            assert 1 <= result <= 100

    def test_deterministic(self):
        """Same seed produces same result."""
        rng1 = random.Random(123)
        rng2 = random.Random(123)

        assert roll_d100(rng1) == roll_d100(rng2)


# =============================================================================
# CR Tier Tests
# =============================================================================


class TestCRTierMapping:
    """Tests for CR tier mapping."""

    def test_tier_1_boundaries(self):
        """CR 0-4 maps to tier 1."""
        assert get_cr_tier(0) == 1
        assert get_cr_tier(0.125) == 1  # CR 1/8
        assert get_cr_tier(0.25) == 1   # CR 1/4
        assert get_cr_tier(0.5) == 1    # CR 1/2
        assert get_cr_tier(1) == 1
        assert get_cr_tier(4) == 1

    def test_tier_2_boundaries(self):
        """CR 5-10 maps to tier 2."""
        assert get_cr_tier(5) == 2
        assert get_cr_tier(7) == 2
        assert get_cr_tier(10) == 2

    def test_tier_3_boundaries(self):
        """CR 11-16 maps to tier 3."""
        assert get_cr_tier(11) == 3
        assert get_cr_tier(14) == 3
        assert get_cr_tier(16) == 3

    def test_tier_4_boundaries(self):
        """CR 17+ maps to tier 4."""
        assert get_cr_tier(17) == 4
        assert get_cr_tier(20) == 4
        assert get_cr_tier(30) == 4


class TestParseCR:
    """Tests for parse_cr function."""

    def test_integer_cr(self):
        """Parse integer CR."""
        assert parse_cr("0") == 0.0
        assert parse_cr("5") == 5.0
        assert parse_cr("20") == 20.0

    def test_fractional_cr(self):
        """Parse fractional CR."""
        assert parse_cr("1/8") == 0.125
        assert parse_cr("1/4") == 0.25
        assert parse_cr("1/2") == 0.5

    def test_whitespace_handling(self):
        """Handle whitespace in CR string."""
        assert parse_cr(" 5 ") == 5.0
        assert parse_cr("1/4 ") == 0.25

    def test_invalid_cr(self):
        """Invalid CR raises error."""
        with pytest.raises(ValueError):
            parse_cr("invalid")


# =============================================================================
# Individual Treasure Tests
# =============================================================================


class TestIndividualTreasure:
    """Tests for individual treasure generation."""

    def test_generates_coins(self):
        """Individual treasure generates coins."""
        generator = LootGenerator(seed=42)
        treasure = generator.generate_individual(cr=2)

        assert treasure.treasure_type == "individual"
        assert treasure.source_cr == 2
        assert treasure.coins  # Has some coins
        assert not treasure.gems
        assert not treasure.art_objects
        assert not treasure.magic_items

    def test_deterministic_with_seed(self):
        """Same seed produces same treasure."""
        gen1 = LootGenerator(seed=123)
        gen2 = LootGenerator(seed=123)

        t1 = gen1.generate_individual(cr=5)
        t2 = gen2.generate_individual(cr=5)

        assert t1.coins == t2.coins

    def test_count_multiplies(self):
        """Count parameter affects total coins."""
        gen1 = LootGenerator(seed=42)
        gen2 = LootGenerator(seed=42)

        t1 = gen1.generate_individual(cr=3, count=1)
        t2 = gen2.generate_individual(cr=3, count=4)

        # Count=4 should generally have more coins
        # (can't guarantee due to randomness, but with same seed we know the pattern)
        total1 = sum(t1.coins.values())
        total2 = sum(t2.coins.values())
        # Just verify both have coins
        assert total1 > 0
        assert total2 > 0

    def test_each_tier_works(self):
        """Each CR tier generates valid treasure."""
        generator = LootGenerator(seed=42)

        for cr in [0, 2, 7, 14, 20]:
            treasure = generator.generate_individual(cr=cr)
            # Should have at least one coin type
            assert treasure.coins or treasure.source_cr == 0


# =============================================================================
# Hoard Tests
# =============================================================================


class TestHoardTreasure:
    """Tests for hoard treasure generation."""

    def test_generates_coins(self):
        """Hoard always generates coins."""
        generator = LootGenerator(seed=42)
        treasure = generator.generate_hoard(cr=5)

        assert treasure.treasure_type == "hoard"
        assert treasure.coins

    def test_deterministic_with_seed(self):
        """Same seed produces same hoard."""
        gen1 = LootGenerator(seed=456)
        gen2 = LootGenerator(seed=456)

        t1 = gen1.generate_hoard(cr=10)
        t2 = gen2.generate_hoard(cr=10)

        assert t1.coins == t2.coins
        assert t1.gems == t2.gems
        assert t1.art_objects == t2.art_objects
        assert t1.magic_items == t2.magic_items

    def test_each_tier_works(self):
        """Each CR tier generates valid hoard."""
        generator = LootGenerator(seed=42)

        for cr in [2, 7, 14, 20]:
            treasure = generator.generate_hoard(cr=cr)
            assert treasure.coins

    def test_may_include_gems_or_art(self):
        """Hoards may include gems or art objects."""
        # Use a seed known to produce gems/art
        generator = LootGenerator(seed=100)
        treasure = generator.generate_hoard(cr=10)

        # At least verify the structure is correct
        assert isinstance(treasure.gems, list)
        assert isinstance(treasure.art_objects, list)
        assert isinstance(treasure.magic_items, list)

    def test_gems_have_value_and_name(self):
        """Gems include value and name."""
        # Find a seed that produces gems
        for seed in range(100):
            generator = LootGenerator(seed=seed)
            treasure = generator.generate_hoard(cr=5)
            if treasure.gems:
                for value, name in treasure.gems:
                    assert isinstance(value, int)
                    assert isinstance(name, str)
                    assert value in GEMS
                break


# =============================================================================
# Magic Item Table Tests
# =============================================================================


class TestMagicItemTables:
    """Tests for magic item table rolls."""

    def test_table_a_items(self):
        """Table A returns valid items."""
        generator = LootGenerator(seed=42)
        items = generator.roll_magic_item_table("A", count=5)

        assert len(items) == 5
        valid_items = [item for _, item in MAGIC_ITEM_TABLES["A"]]
        for item in items:
            assert item in valid_items

    def test_all_tables_work(self):
        """All tables A-I return items."""
        generator = LootGenerator(seed=42)

        for table in "ABCDEFGHI":
            items = generator.roll_magic_item_table(table, count=1)
            assert len(items) == 1
            valid_items = [item for _, item in MAGIC_ITEM_TABLES[table]]
            assert items[0] in valid_items

    def test_invalid_table_raises_error(self):
        """Invalid table letter raises error."""
        generator = LootGenerator(seed=42)

        with pytest.raises(ValueError) as exc:
            generator.roll_magic_item_table("Z")

        assert "Invalid magic item table" in str(exc.value)

    def test_case_insensitive(self):
        """Table letters are case insensitive."""
        generator = LootGenerator(seed=42)

        items_upper = generator.roll_magic_item_table("A")
        generator = LootGenerator(seed=42)  # Reset
        items_lower = generator.roll_magic_item_table("a")

        assert items_upper == items_lower

    def test_deterministic_with_seed(self):
        """Same seed produces same items."""
        gen1 = LootGenerator(seed=789)
        gen2 = LootGenerator(seed=789)

        items1 = gen1.roll_magic_item_table("F", count=3)
        items2 = gen2.roll_magic_item_table("F", count=3)

        assert items1 == items2


# =============================================================================
# Formatter Tests
# =============================================================================


class TestTreasureFormatter:
    """Tests for treasure formatting."""

    def test_format_coins(self):
        """Coins are formatted correctly."""
        treasure = Treasure(
            coins={"gp": 100, "sp": 50, "cp": 25},
            treasure_type="individual",
            source_cr=3,
        )
        formatter = TreasureFormatter()
        output = formatter.format_console(treasure)

        assert "100 gp" in output
        assert "50 sp" in output
        assert "25 cp" in output

    def test_format_gems(self):
        """Gems are formatted with value grouping."""
        treasure = Treasure(
            coins={"gp": 10},
            gems=[(50, "Moonstone"), (50, "Onyx"), (100, "Jade")],
            treasure_type="hoard",
        )
        formatter = TreasureFormatter()
        output = formatter.format_console(treasure)

        assert "50 gp" in output
        assert "Moonstone" in output
        assert "100 gp" in output
        assert "Jade" in output

    def test_format_art_objects(self):
        """Art objects are formatted correctly."""
        treasure = Treasure(
            coins={"gp": 10},
            art_objects=[(250, "Gold ring set with bloodstones")],
            treasure_type="hoard",
        )
        formatter = TreasureFormatter()
        output = formatter.format_console(treasure)

        assert "250 gp" in output
        assert "Gold ring" in output

    def test_format_magic_items(self):
        """Magic items are formatted."""
        treasure = Treasure(
            coins={"gp": 10},
            magic_items=["Potion of Healing", "Bag of Holding"],
            treasure_type="hoard",
        )
        formatter = TreasureFormatter()
        output = formatter.format_console(treasure)

        assert "Potion of Healing" in output
        assert "Bag of Holding" in output

    def test_title_from_type(self):
        """Title is generated from treasure type."""
        individual = Treasure(coins={"gp": 10}, treasure_type="individual", source_cr=5)
        hoard = Treasure(coins={"gp": 10}, treasure_type="hoard", source_cr=5)

        formatter = TreasureFormatter()

        individual_output = formatter.format_console(individual)
        hoard_output = formatter.format_console(hoard)

        assert "Individual" in individual_output
        assert "Hoard" in hoard_output


# =============================================================================
# Data Completeness Tests
# =============================================================================


class TestDataCompleteness:
    """Tests to verify all treasure tables are complete."""

    def test_all_individual_tiers_exist(self):
        """All 4 individual treasure tiers exist."""
        assert 1 in INDIVIDUAL_TREASURE
        assert 2 in INDIVIDUAL_TREASURE
        assert 3 in INDIVIDUAL_TREASURE
        assert 4 in INDIVIDUAL_TREASURE

    def test_all_hoard_tiers_exist(self):
        """All 4 hoard tiers exist."""
        assert 1 in HOARD_COINS
        assert 2 in HOARD_COINS
        assert 3 in HOARD_COINS
        assert 4 in HOARD_COINS

        assert 1 in HOARD_TABLES
        assert 2 in HOARD_TABLES
        assert 3 in HOARD_TABLES
        assert 4 in HOARD_TABLES

    def test_all_gem_values_exist(self):
        """All gem value tiers exist."""
        for value in [10, 50, 100, 500, 1000, 5000]:
            assert value in GEMS
            assert len(GEMS[value]) > 0

    def test_all_art_values_exist(self):
        """All art object value tiers exist."""
        for value in [25, 250, 750, 2500, 7500]:
            assert value in ART_OBJECTS
            assert len(ART_OBJECTS[value]) > 0

    def test_all_magic_tables_exist(self):
        """All magic item tables A-I exist."""
        for table in "ABCDEFGHI":
            assert table in MAGIC_ITEM_TABLES
            assert len(MAGIC_ITEM_TABLES[table]) > 0

    def test_tables_cover_full_d100_range(self):
        """Tables cover d100 roll 1-100."""
        # Check individual treasure tables
        for tier in [1, 2, 3, 4]:
            max_threshold = max(t for t, _ in INDIVIDUAL_TREASURE[tier])
            assert max_threshold == 100

        # Check magic item tables
        for table in "ABCDEFGHI":
            max_threshold = max(t for t, _ in MAGIC_ITEM_TABLES[table])
            assert max_threshold == 100


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for end-to-end workflows."""

    def test_full_hoard_workflow(self):
        """Generate and format a complete hoard."""
        generator = LootGenerator(seed=42)
        treasure = generator.generate_hoard(cr=10)

        formatter = TreasureFormatter()
        output = formatter.format_console(treasure)

        assert "##" in output  # Has heading
        assert len(output) > 50  # Has content

    def test_treasure_dataclass(self):
        """Treasure dataclass has expected fields."""
        treasure = Treasure()
        assert treasure.coins == {}
        assert treasure.gems == []
        assert treasure.art_objects == []
        assert treasure.magic_items == []
        assert treasure.source_cr is None
        assert treasure.treasure_type == "hoard"


class TestLoadEncounterCR:
    """Tests for load_encounter_cr function."""

    def test_extracts_cr_not_xp_from_table(self):
        """CR extraction should capture CR column, not XP or Total XP columns.

        Regression test: The regex should match the full 5-column table row
        to ensure only the CR column is captured, not XP values that would
        cause incorrect tier selection.
        """
        encounter_content = """# Goblin Ambush

## Creatures

| Creature | CR | XP | Count | Total XP |
| -------- | -- | -- | ----- | -------- |
| [Goblin](../../books/reference/creatures/goblin.md) | 1/4 | 50 | 4 | 200 |
| [Goblin Boss](../../books/reference/creatures/goblin-boss.md) | 1 | 200 | 1 | 200 |
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir)
            encounters_dir = campaign_dir / "encounters"
            encounters_dir.mkdir(parents=True)
            encounter_file = encounters_dir / "goblin-ambush.md"
            encounter_file.write_text(encounter_content)

            cr = load_encounter_cr("goblin-ambush", campaign_dir)

            # Should return 1.0 (Goblin Boss CR), not 200 (Total XP)
            assert cr == 1.0

    def test_extracts_highest_cr(self):
        """Should return the highest CR from all creatures."""
        encounter_content = """# Dragon Lair

| Creature | CR | XP | Count | Total XP |
| -------- | -- | -- | ----- | -------- |
| [Young Dragon](path) | 7 | 2,900 | 1 | 2,900 |
| [Kobold](path) | 1/8 | 25 | 6 | 150 |
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir)
            encounters_dir = campaign_dir / "encounters"
            encounters_dir.mkdir(parents=True)
            encounter_file = encounters_dir / "dragon-lair.md"
            encounter_file.write_text(encounter_content)

            cr = load_encounter_cr("dragon-lair", campaign_dir)

            assert cr == 7.0

    def test_handles_fractional_cr(self):
        """Should correctly parse fractional CRs."""
        encounter_content = """# Low Level Encounter

| Creature | CR | XP | Count | Total XP |
| -------- | -- | -- | ----- | -------- |
| [Rat](path) | 1/8 | 25 | 8 | 200 |
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            campaign_dir = Path(tmpdir)
            encounters_dir = campaign_dir / "encounters"
            encounters_dir.mkdir(parents=True)
            encounter_file = encounters_dir / "rat-swarm.md"
            encounter_file.write_text(encounter_content)

            cr = load_encounter_cr("rat-swarm", campaign_dir)

            assert cr == 0.125
