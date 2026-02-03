"""Tests for relationship_parser.py"""

import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.relationship_parser import (
    RELATIONSHIP_TYPES,
    Relationship,
    add_relationship_to_content,
    format_relationship_line,
    parse_connections_section,
    parse_relationship_line,
    parse_connections_from_file,
)


class TestParseRelationshipLine:
    """Tests for parsing individual relationship lines."""

    def test_parse_linked_with_description(self):
        """Test parsing a relationship with a markdown link and description."""
        line = "- [Grimbold](grimbold.md) | ally | Childhood friend"
        result = parse_relationship_line(line)

        assert result is not None
        name, file, rel_type, desc = result
        assert name == "Grimbold"
        assert file == "grimbold.md"
        assert rel_type == "ally"
        assert desc == "Childhood friend"

    def test_parse_linked_without_description(self):
        """Test parsing a relationship with a link but no description."""
        line = "- [Mayor Thorne](mayor-thorne.md) | employer"
        result = parse_relationship_line(line)

        assert result is not None
        name, file, rel_type, desc = result
        assert name == "Mayor Thorne"
        assert file == "mayor-thorne.md"
        assert rel_type == "employer"
        assert desc == ""

    def test_parse_unlinked_with_description(self):
        """Test parsing a relationship without a link."""
        line = "- The Shadow Guild | enemy | Hunted for past crimes"
        result = parse_relationship_line(line)

        assert result is not None
        name, file, rel_type, desc = result
        assert name == "The Shadow Guild"
        assert file is None
        assert rel_type == "enemy"
        assert desc == "Hunted for past crimes"

    def test_parse_unlinked_without_description(self):
        """Test parsing a simple relationship without link or description."""
        line = "- The King | neutral"
        result = parse_relationship_line(line)

        assert result is not None
        name, file, rel_type, desc = result
        assert name == "The King"
        assert file is None
        assert rel_type == "neutral"
        assert desc == ""

    def test_parse_strips_whitespace(self):
        """Test that extra whitespace is handled correctly."""
        line = "  -   [Elara](elara.md)  |  ally  |  Best friend  "
        result = parse_relationship_line(line)

        assert result is not None
        name, file, rel_type, desc = result
        assert name == "Elara"
        assert rel_type == "ally"
        assert desc == "Best friend"

    def test_parse_returns_none_for_invalid(self):
        """Test that invalid lines return None."""
        assert parse_relationship_line("") is None
        assert parse_relationship_line("Not a relationship") is None
        assert parse_relationship_line("- Missing pipe separator") is None

    def test_parse_case_insensitive_type(self):
        """Test that relationship types are lowercased."""
        line = "- [Test](test.md) | ALLY | Test"
        result = parse_relationship_line(line)

        assert result is not None
        assert result[2] == "ally"


class TestParseConnectionsSection:
    """Tests for parsing the full Connections section."""

    def test_parse_multiple_relationships(self):
        """Test parsing multiple relationships from content."""
        content = """# Test NPC

## Connections

- [Ally One](ally-one.md) | ally | Best friend
- [Enemy One](enemy-one.md) | enemy | Arch-nemesis
- Neutral Party | neutral

## Secrets

Some secrets here.
"""
        relationships = parse_connections_section(content)

        assert len(relationships) == 3
        assert relationships[0][0] == "Ally One"
        assert relationships[1][0] == "Enemy One"
        assert relationships[2][0] == "Neutral Party"

    def test_parse_empty_section(self):
        """Test parsing when Connections section is empty."""
        content = """# Test NPC

## Connections

## Secrets

Some secrets.
"""
        relationships = parse_connections_section(content)
        assert len(relationships) == 0

    def test_parse_no_connections_section(self):
        """Test parsing when there's no Connections section."""
        content = """# Test NPC

## Description

A test character.
"""
        relationships = parse_connections_section(content)
        assert len(relationships) == 0

    def test_parse_ignores_placeholder_text(self):
        """Test that placeholder text is ignored."""
        content = """# Test NPC

## Connections

*Add relationships using: `- [Name](file.md) | type | description`*

- [Real Relationship](real.md) | ally | Actually parsed

## Secrets
"""
        relationships = parse_connections_section(content)
        assert len(relationships) == 1
        assert relationships[0][0] == "Real Relationship"


class TestParseConnectionsFromFile:
    """Tests for parsing relationships from a file."""

    def test_parse_from_file(self, tmp_path):
        """Test parsing relationships from an actual file."""
        npc_file = tmp_path / "test-npc.md"
        npc_file.write_text("""# Test NPC

## Connections

- [Friend](friend.md) | ally | Close companion

## Secrets
""")

        relationships = parse_connections_from_file(npc_file)

        assert len(relationships) == 1
        rel = relationships[0]
        assert rel.source_name == "Test NPC"
        assert rel.source_file == "test-npc.md"
        assert rel.target_name == "Friend"
        assert rel.target_file == "friend.md"
        assert rel.relationship_type == "ally"
        assert rel.description == "Close companion"

    def test_parse_nonexistent_file(self, tmp_path):
        """Test parsing a file that doesn't exist."""
        relationships = parse_connections_from_file(tmp_path / "nonexistent.md")
        assert len(relationships) == 0


class TestFormatRelationshipLine:
    """Tests for formatting relationship lines."""

    def test_format_with_link_and_description(self):
        """Test formatting a complete relationship."""
        line = format_relationship_line("Grimbold", "grimbold.md", "ally", "Old friend")
        assert line == "- [Grimbold](grimbold.md) | ally | Old friend"

    def test_format_with_link_no_description(self):
        """Test formatting without description."""
        line = format_relationship_line("Grimbold", "grimbold.md", "ally")
        assert line == "- [Grimbold](grimbold.md) | ally"

    def test_format_without_link(self):
        """Test formatting without a file link."""
        line = format_relationship_line("The Guild", None, "enemy", "Dangerous")
        assert line == "- The Guild | enemy | Dangerous"


class TestAddRelationshipToContent:
    """Tests for adding relationships to NPC content."""

    def test_add_relationship_to_empty_section(self):
        """Test adding a relationship to an empty section."""
        content = """# Test NPC

## Connections

*List relationships...*

## Secrets
"""
        updated = add_relationship_to_content(
            content, "Friend", "friend.md", "ally", "Good friend"
        )

        assert "- [Friend](friend.md) | ally | Good friend" in updated
        assert "*List relationships...*" not in updated

    def test_add_relationship_preserves_existing(self):
        """Test that existing relationships are preserved."""
        content = """# Test NPC

## Connections

- [Existing](existing.md) | ally | Already here

## Secrets
"""
        updated = add_relationship_to_content(
            content, "New Friend", "new-friend.md", "ally", "New addition"
        )

        assert "- [Existing](existing.md) | ally | Already here" in updated
        assert "- [New Friend](new-friend.md) | ally | New addition" in updated

    def test_no_duplicate_relationships(self):
        """Test that duplicate relationships are not added."""
        content = """# Test NPC

## Connections

- [Friend](friend.md) | ally | Already here

## Secrets
"""
        updated = add_relationship_to_content(
            content, "Friend", "friend.md", "enemy", "Different type"
        )

        # Should not add because "Friend" already exists (case-insensitive)
        assert updated.count("Friend") == 1


class TestRelationshipInverses:
    """Tests for relationship type inverses."""

    def test_get_inverse_type(self):
        """Test getting inverse relationship types."""
        rel = Relationship(
            source_name="A", source_file=None,
            target_name="B", target_file=None,
            relationship_type="employer"
        )
        assert rel.get_inverse_type() == "employee"

    def test_symmetric_inverse(self):
        """Test that symmetric types return themselves."""
        rel = Relationship(
            source_name="A", source_file=None,
            target_name="B", target_file=None,
            relationship_type="ally"
        )
        assert rel.get_inverse_type() == "ally"

    def test_all_types_have_inverses(self):
        """Test that all standard types have defined inverses."""
        for rel_type in RELATIONSHIP_TYPES:
            inverse = RELATIONSHIP_TYPES[rel_type]
            assert inverse in RELATIONSHIP_TYPES
