"""Tests for character import functionality."""

import json
import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.dndbeyond_client import parse_character
from lib.markdown_writer import slugify


class TestSlugify:
    """Tests for slugify function."""

    def test_simple_name(self):
        """Test slugifying a simple name."""
        assert slugify("Meilin Starwell") == "meilin-starwell"

    def test_special_characters(self):
        """Test that special characters are removed."""
        assert slugify("Bob's Tavern") == "bobs-tavern"

    def test_multiple_spaces(self):
        """Test multiple spaces become single hyphen."""
        assert slugify("The   Great   Hero") == "the-great-hero"

    def test_uppercase(self):
        """Test uppercase is converted to lowercase."""
        assert slugify("UPPERCASE NAME") == "uppercase-name"


class TestCharacterMarkdown:
    """Tests for character markdown generation."""

    @pytest.fixture
    def sample_character(self):
        """Load and parse sample character."""
        fixture_path = Path(__file__).parent / "fixtures" / "dndbeyond_sample.json"
        with open(fixture_path) as f:
            data = json.load(f)
        return parse_character(data)

    def test_character_has_required_fields(self, sample_character):
        """Test that character has all required fields for markdown."""
        char = sample_character

        assert char.name
        assert char.species
        assert len(char.classes) > 0
        assert char.level > 0
        assert char.stats is not None
        assert char.max_hp > 0

    def test_class_string_multiclass(self):
        """Test class string with multiclass (synthetic test)."""
        from lib.dndbeyond_client import Character, ClassInfo, CharacterStats

        char = Character(
            id=1,
            name="Test",
            classes=[
                ClassInfo(name="Fighter", level=3),
                ClassInfo(name="Wizard", level=2),
            ],
            level=5,
            stats=CharacterStats(),
        )

        assert char.class_string() == "Fighter 3 / Wizard 2"

    def test_modifier_calculation(self, sample_character):
        """Test ability modifier calculation."""
        char = sample_character

        # DEX 15 + 2 bonus = 17, modifier should be +3
        assert char.stats.total("dexterity") == 17
        assert char.stats.modifier("dexterity") == 3
        assert char.stats.modifier_str("dexterity") == "+3"

        # STR 8, modifier should be -1
        assert char.stats.modifier("strength") == -1
        assert char.stats.modifier_str("strength") == "-1"

    def test_proficiency_bonus(self, sample_character):
        """Test proficiency bonus calculation."""
        char = sample_character

        # Level 1 character should have +2 proficiency bonus
        assert char.proficiency_bonus == 2
