"""Tests for character import functionality."""

import json
import sys
import tempfile
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


class TestExtractDndbeyondId:
    """Tests for extract_dndbeyond_id_from_file function."""

    def test_extract_id_from_valid_file(self, tmp_path):
        """Test extracting ID from a valid character file."""
        from campaign.import_character import extract_dndbeyond_id_from_file

        # Create a test file with a source URL
        char_file = tmp_path / "test-character.md"
        char_file.write_text("""# Test Character

**Class**: Fighter 5

---

*Imported from D&D Beyond on 2026-01-15*  
*Last updated: 2026-01-29*  
*Source: https://www.dndbeyond.com/characters/157884334*
""")

        result = extract_dndbeyond_id_from_file(char_file)
        assert result == 157884334

    def test_extract_id_from_file_without_source(self, tmp_path):
        """Test extracting ID from a file without source URL."""
        from campaign.import_character import extract_dndbeyond_id_from_file

        char_file = tmp_path / "manual-character.md"
        char_file.write_text("""# Manual Character

**Class**: Wizard 3

This character was created manually.
""")

        result = extract_dndbeyond_id_from_file(char_file)
        assert result is None

    def test_extract_id_from_nonexistent_file(self, tmp_path):
        """Test extracting ID from a nonexistent file."""
        from campaign.import_character import extract_dndbeyond_id_from_file

        result = extract_dndbeyond_id_from_file(tmp_path / "nonexistent.md")
        assert result is None


class TestExtractImportedDate:
    """Tests for extract_imported_date_from_file function."""

    def test_extract_date_from_valid_file(self, tmp_path):
        """Test extracting import date from a valid character file."""
        from campaign.import_character import extract_imported_date_from_file

        char_file = tmp_path / "test-character.md"
        char_file.write_text("""# Test Character

---

*Imported from D&D Beyond on 2026-01-15*  
*Last updated: 2026-01-29*  
*Source: https://www.dndbeyond.com/characters/157884334*
""")

        result = extract_imported_date_from_file(char_file)
        assert result == "2026-01-15"

    def test_extract_date_from_file_without_date(self, tmp_path):
        """Test extracting date from a file without import date."""
        from campaign.import_character import extract_imported_date_from_file

        char_file = tmp_path / "manual-character.md"
        char_file.write_text("""# Manual Character

This character was created manually.
""")

        result = extract_imported_date_from_file(char_file)
        assert result is None


class TestListImportedCharacters:
    """Tests for list_imported_characters function."""

    def test_list_empty_directory(self, tmp_path):
        """Test listing characters from empty directory."""
        from campaign.import_character import list_imported_characters

        party_dir = tmp_path / "party"
        party_dir.mkdir()
        (party_dir / "characters").mkdir()

        result = list_imported_characters(party_dir)
        assert result == []

    def test_list_characters(self, tmp_path):
        """Test listing characters from directory with files."""
        from campaign.import_character import list_imported_characters

        party_dir = tmp_path / "party"
        chars_dir = party_dir / "characters"
        chars_dir.mkdir(parents=True)

        # Create test character files
        (chars_dir / "meilin.md").write_text("""# Meilin Starwell

**Class**: Rogue 5  

---

*Imported from D&D Beyond on 2026-01-15*  
*Last updated: 2026-01-20*  
*Source: https://www.dndbeyond.com/characters/157884334*
""")

        (chars_dir / "thorin.md").write_text("""# Thorin Ironforge

**Class**: Fighter 3 / Barbarian 2  

---

*Imported from D&D Beyond on 2026-01-10*  
*Source: https://www.dndbeyond.com/characters/987654321*
""")

        result = list_imported_characters(party_dir)

        assert len(result) == 2

        # Check first character (alphabetically sorted)
        meilin = next(c for c in result if c["name"] == "Meilin Starwell")
        assert meilin["dndbeyond_id"] == 157884334
        assert meilin["imported_date"] == "2026-01-15"
        assert meilin["updated_date"] == "2026-01-20"

        thorin = next(c for c in result if c["name"] == "Thorin Ironforge")
        assert thorin["dndbeyond_id"] == 987654321
        assert thorin["imported_date"] == "2026-01-10"

    def test_list_nonexistent_directory(self, tmp_path):
        """Test listing characters from nonexistent directory."""
        from campaign.import_character import list_imported_characters

        result = list_imported_characters(tmp_path / "nonexistent")
        assert result == []
