"""Tests for encounter builder."""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from campaign.encounter_builder import (
    CR_XP,
    Creature,
    Encounter,
    EncounterEntry,
    cr_to_xp,
    filter_creatures,
    generate_encounter,
    get_encounter_multiplier,
    get_party_thresholds,
    parse_cr,
)


class TestCRParsing:
    """Tests for CR parsing functions."""

    def test_parse_whole_number(self):
        """Test parsing whole number CRs."""
        assert parse_cr("1") == 1.0
        assert parse_cr("5") == 5.0
        assert parse_cr("20") == 20.0

    def test_parse_fraction(self):
        """Test parsing fractional CRs."""
        assert parse_cr("1/8") == 0.125
        assert parse_cr("1/4") == 0.25
        assert parse_cr("1/2") == 0.5

    def test_cr_to_xp(self):
        """Test CR to XP conversion."""
        assert cr_to_xp("0") == 10
        assert cr_to_xp("1/4") == 50
        assert cr_to_xp("1") == 200
        assert cr_to_xp("5") == 1800
        assert cr_to_xp("10") == 5900


class TestPartyThresholds:
    """Tests for XP threshold calculations."""

    def test_level_1_party_of_4(self):
        """Test thresholds for a typical starting party."""
        thresholds = get_party_thresholds(1, 4)

        assert thresholds["easy"] == 100  # 25 * 4
        assert thresholds["medium"] == 200  # 50 * 4
        assert thresholds["hard"] == 300  # 75 * 4
        assert thresholds["deadly"] == 400  # 100 * 4

    def test_level_5_party_of_4(self):
        """Test thresholds for level 5 party."""
        thresholds = get_party_thresholds(5, 4)

        assert thresholds["easy"] == 1000  # 250 * 4
        assert thresholds["medium"] == 2000  # 500 * 4

    def test_level_clamp(self):
        """Test that out-of-range levels are clamped."""
        # Level 0 should be treated as 1
        thresholds = get_party_thresholds(0, 4)
        assert thresholds == get_party_thresholds(1, 4)

        # Level 25 should be treated as 20
        thresholds = get_party_thresholds(25, 4)
        assert thresholds == get_party_thresholds(20, 4)


class TestEncounterMultiplier:
    """Tests for encounter multiplier calculation."""

    def test_single_creature(self):
        """Test multiplier for single creature."""
        assert get_encounter_multiplier(1) == 1.0

    def test_two_creatures(self):
        """Test multiplier for two creatures."""
        assert get_encounter_multiplier(2) == 1.5

    def test_group_creatures(self):
        """Test multiplier for groups."""
        assert get_encounter_multiplier(3) == 2.0
        assert get_encounter_multiplier(6) == 2.0
        assert get_encounter_multiplier(7) == 2.5
        assert get_encounter_multiplier(15) == 4.0


class TestCreatureFiltering:
    """Tests for creature filtering."""

    @pytest.fixture
    def sample_creatures(self):
        """Create sample creatures for testing."""
        return [
            Creature("Goblin", "1/4", 50, "creatures/goblin.md", "Humanoid"),
            Creature("Orc", "1/2", 100, "creatures/orc.md", "Humanoid"),
            Creature("Skeleton", "1/4", 50, "creatures/skeleton.md", "Undead"),
            Creature("Zombie", "1/4", 50, "creatures/zombie.md", "Undead"),
            Creature("Ogre", "2", 450, "creatures/ogre.md", "Giant"),
            Creature("Young Dragon", "5", 1800, "creatures/young-dragon.md", "Dragon"),
        ]

    def test_filter_by_type(self, sample_creatures):
        """Test filtering by creature type."""
        undead = filter_creatures(sample_creatures, creature_type="Undead")
        assert len(undead) == 2
        assert all("Undead" in c.creature_type for c in undead)

    def test_filter_by_cr_range(self, sample_creatures):
        """Test filtering by CR range."""
        low_cr = filter_creatures(sample_creatures, cr_max=0.5)
        assert len(low_cr) == 4  # Goblins, Orc, Skeletons, Zombies

        high_cr = filter_creatures(sample_creatures, cr_min=2)
        assert len(high_cr) == 2  # Ogre, Dragon


class TestEncounterGeneration:
    """Tests for encounter generation."""

    @pytest.fixture
    def sample_creatures(self):
        """Create creatures for encounter testing."""
        return [
            Creature("Goblin", "1/4", 50, "creatures/goblin.md", "Humanoid"),
            Creature("Orc", "1/2", 100, "creatures/orc.md", "Humanoid"),
            Creature("Bugbear", "1", 200, "creatures/bugbear.md", "Humanoid"),
            Creature("Ogre", "2", 450, "creatures/ogre.md", "Giant"),
        ]

    def test_generate_medium_encounter(self, sample_creatures):
        """Test generating a medium difficulty encounter."""
        encounter = generate_encounter(
            sample_creatures,
            party_level=3,
            party_size=4,
            difficulty="medium",
        )

        assert encounter is not None
        assert len(encounter.entries) > 0
        assert encounter.total_creatures > 0

    def test_encounter_xp_calculation(self):
        """Test encounter XP calculations."""
        goblin = Creature("Goblin", "1/4", 50, "path", "Humanoid")

        encounter = Encounter(
            entries=[EncounterEntry(goblin, 4)],
            party_level=1,
            party_size=4,
            target_difficulty="medium",
        )

        assert encounter.base_xp == 200  # 50 * 4
        # 4 creatures = 2.0 multiplier
        assert encounter.adjusted_xp == 400  # 200 * 2.0

    def test_encounter_difficulty_calculation(self):
        """Test difficulty determination."""
        goblin = Creature("Goblin", "1/4", 50, "path", "Humanoid")

        # 4 goblins = 200 base XP, 400 adjusted
        # Level 1 party of 4: medium = 200, hard = 300, deadly = 400
        encounter = Encounter(
            entries=[EncounterEntry(goblin, 4)],
            party_level=1,
            party_size=4,
            target_difficulty="medium",
        )

        assert encounter.calculate_difficulty() == "deadly"
