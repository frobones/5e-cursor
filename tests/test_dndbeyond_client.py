"""Tests for D&D Beyond client."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.dndbeyond_client import (
    Character,
    extract_character_id,
    parse_character,
)


class TestExtractCharacterId:
    """Tests for extract_character_id function."""

    def test_full_url(self):
        """Test extracting ID from full URL."""
        url = "https://www.dndbeyond.com/characters/157884334"
        assert extract_character_id(url) == 157884334

    def test_url_without_www(self):
        """Test extracting ID from URL without www."""
        url = "https://dndbeyond.com/characters/157884334"
        assert extract_character_id(url) == 157884334

    def test_just_id(self):
        """Test extracting ID when just number is provided."""
        assert extract_character_id("157884334") == 157884334

    def test_invalid_url(self):
        """Test that invalid URL raises ValueError."""
        with pytest.raises(ValueError):
            extract_character_id("https://example.com/foo")


class TestParseCharacter:
    """Tests for parse_character function."""

    @pytest.fixture
    def sample_data(self):
        """Load sample D&D Beyond response."""
        fixture_path = Path(__file__).parent / "fixtures" / "dndbeyond_sample.json"
        with open(fixture_path) as f:
            return json.load(f)

    def test_basic_info(self, sample_data):
        """Test parsing basic character info."""
        char = parse_character(sample_data)

        assert char.name == "Meilin Starwell"
        assert char.player == "Frobones"
        assert char.species == "Human"
        assert char.gender == "Female"
        assert char.age == 26

    def test_classes(self, sample_data):
        """Test parsing class info."""
        char = parse_character(sample_data)

        assert len(char.classes) == 1
        assert char.classes[0].name == "Rogue"
        assert char.classes[0].level == 1
        assert char.level == 1

    def test_stats(self, sample_data):
        """Test parsing ability scores."""
        char = parse_character(sample_data)

        assert char.stats.strength == 8
        assert char.stats.dexterity == 15
        assert char.stats.constitution == 12
        assert char.stats.intelligence == 13
        assert char.stats.wisdom == 14
        assert char.stats.charisma == 10

    def test_stat_bonuses(self, sample_data):
        """Test that stat bonuses are applied."""
        char = parse_character(sample_data)

        # Human gets +2 DEX, +1 INT from choices
        assert char.stats.dexterity_bonus == 2
        assert char.stats.intelligence_bonus == 1
        assert char.stats.total("dexterity") == 17
        assert char.stats.total("intelligence") == 14

    def test_class_string(self, sample_data):
        """Test class string formatting."""
        char = parse_character(sample_data)

        assert char.class_string() == "Rogue 1"

    def test_inventory(self, sample_data):
        """Test parsing inventory."""
        char = parse_character(sample_data)

        assert len(char.inventory) > 0

        # Find leather armor
        leather = next((i for i in char.inventory if "Leather" in i.name), None)
        assert leather is not None
        assert leather.equipped is True
        assert leather.armor_class == 11

        # Find dagger
        dagger = next((i for i in char.inventory if "Dagger" in i.name), None)
        assert dagger is not None
        assert dagger.damage == "1d4"

    def test_feats(self, sample_data):
        """Test parsing feats."""
        char = parse_character(sample_data)

        feat_names = [f["name"] for f in char.feats]
        assert "Healer" in feat_names
        assert "Skilled" in feat_names

    def test_proficiencies(self, sample_data):
        """Test parsing proficiencies."""
        char = parse_character(sample_data)

        # Skill proficiencies
        assert "Investigation" in char.skill_proficiencies or any(
            "investigation" in s.lower() for s in char.skill_proficiencies
        )

        # Expertise
        assert len(char.skill_expertise) > 0

        # Languages
        assert any("Common" in lang for lang in char.languages)

    def test_source_url(self, sample_data):
        """Test source URL is set."""
        char = parse_character(sample_data)

        assert "dndbeyond.com/characters/157884334" in char.source_url
