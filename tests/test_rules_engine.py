"""Tests for rules engine."""

import sys
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from campaign.rules_engine import (
    derive_source,
    extract_keywords,
    format_quote,
    fuzzy_match,
)


class TestKeywordExtraction:
    """Tests for keyword extraction."""

    def test_simple_query(self):
        """Test extracting keywords from simple query."""
        keywords = extract_keywords("What is fireball?")
        assert "fireball" in keywords

    def test_removes_stop_words(self):
        """Test that stop words are removed."""
        keywords = extract_keywords("What is the prone condition?")
        assert "what" not in keywords
        assert "is" not in keywords
        assert "the" not in keywords
        assert "prone" in keywords
        assert "condition" in keywords

    def test_multi_word_phrases(self):
        """Test that multi-word phrases are extracted."""
        keywords = extract_keywords("sneak attack damage")
        # Should include phrases
        assert any("sneak attack" in k for k in keywords)

    def test_empty_query(self):
        """Test handling empty query."""
        keywords = extract_keywords("")
        assert keywords == []


class TestFuzzyMatch:
    """Tests for fuzzy matching."""

    def test_exact_match(self):
        """Test exact matching."""
        assert fuzzy_match("fireball", "Fireball")
        assert fuzzy_match("sneak attack", "Sneak Attack")

    def test_substring_match(self):
        """Test substring matching."""
        assert fuzzy_match("fire", "Fireball")
        assert fuzzy_match("sneak", "Sneak Attack")

    def test_fuzzy_match(self):
        """Test fuzzy matching with typos."""
        # Close enough
        assert fuzzy_match("firebll", "Fireball", threshold=0.7)

    def test_no_match(self):
        """Test non-matching strings."""
        assert not fuzzy_match("ice storm", "Fireball")


class TestFormatQuote:
    """Tests for quote formatting."""

    def test_single_line(self):
        """Test quoting single line."""
        result = format_quote("This is a rule.")
        assert result == "> This is a rule."

    def test_multi_line(self):
        """Test quoting multiple lines."""
        content = "Line one.\nLine two.\nLine three."
        result = format_quote(content)
        assert result == "> Line one.\n> Line two.\n> Line three."


class TestDeriveSource:
    """Tests for source derivation."""

    def test_spells_path(self):
        """Test deriving source from spell path."""
        source = derive_source("reference/spells/3rd-level/fireball.md")
        assert "Spells" in source

    def test_creatures_path(self):
        """Test deriving source from creature path."""
        source = derive_source("reference/creatures/goblin.md")
        assert "MM" in source or "Creatures" in source
