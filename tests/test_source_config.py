"""Tests for source_config module."""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.source_config import (
    DEFAULT_SOURCES,
    KNOWN_SOURCES,
    PRESETS,
    SourceConfig,
)


class TestSourceConfigDefaults:
    """Test default behavior."""

    def test_default_sources(self):
        """Default sources should be 2024 core + Spelljammer + EFA."""
        config = SourceConfig()
        assert "XPHB" in config.sources
        assert "XDMG" in config.sources
        assert "XMM" in config.sources
        assert "AAG" in config.sources
        assert "BAM" in config.sources
        assert "EFA" in config.sources

    def test_load_without_config_returns_defaults(self):
        """Loading without config file should return defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = SourceConfig.load(repo_root=Path(tmpdir))
            assert config.sources == DEFAULT_SOURCES


class TestSourceConfigYaml:
    """Test YAML config loading."""

    def test_load_explicit_sources(self):
        """Should load explicit sources from YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sources.yaml"
            config_path.write_text("sources:\n  - XPHB\n  - AAG\n")

            config = SourceConfig.load(config_path=config_path)
            assert config.sources == ["XPHB", "AAG"]

    def test_load_preset(self):
        """Should expand preset to sources."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sources.yaml"
            config_path.write_text("preset: 2024-core\n")

            config = SourceConfig.load(config_path=config_path)
            assert config.sources == PRESETS["2024-core"]

    def test_load_preset_with_additional(self):
        """Should add additional sources to preset."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sources.yaml"
            config_path.write_text("preset: 2024-core\nadditional_sources:\n  - AAG\n  - BAM\n")

            config = SourceConfig.load(config_path=config_path)
            assert "XPHB" in config.sources
            assert "AAG" in config.sources
            assert "BAM" in config.sources

    def test_invalid_yaml_returns_defaults(self):
        """Should return defaults on invalid YAML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sources.yaml"
            config_path.write_text("sources: [invalid yaml {{{")

            config = SourceConfig.load(config_path=config_path)
            assert config.sources == DEFAULT_SOURCES


class TestSourceConfigEnv:
    """Test environment variable loading."""

    def test_load_from_env(self):
        """Should load from DND_SOURCES environment variable."""
        os.environ["DND_SOURCES"] = "XPHB,AAG,BAM"
        try:
            config = SourceConfig.load()
            assert config.sources == ["XPHB", "AAG", "BAM"]
        finally:
            del os.environ["DND_SOURCES"]

    def test_env_overrides_config_file(self):
        """Environment variable should take precedence over config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "sources.yaml"
            config_path.write_text("sources:\n  - PHB\n  - DMG\n")

            os.environ["DND_SOURCES"] = "XPHB"
            try:
                config = SourceConfig.load(config_path=config_path)
                assert config.sources == ["XPHB"]
            finally:
                del os.environ["DND_SOURCES"]


class TestSourceConfigValidation:
    """Test source validation."""

    def test_valid_sources_no_warnings(self):
        """Known sources should not produce warnings."""
        config = SourceConfig(sources=["XPHB", "XDMG", "XMM"])
        warnings = config.validate()
        assert warnings == []

    def test_unknown_source_warning(self):
        """Unknown sources should produce warnings."""
        config = SourceConfig(sources=["XPHB", "FAKESOURCE"])
        warnings = config.validate()
        assert len(warnings) == 1
        assert "FAKESOURCE" in warnings[0]


class TestSourceConfigIncludes:
    """Test source inclusion checking."""

    def test_includes_exact_match(self):
        """Should match exact source codes."""
        config = SourceConfig(sources=["XPHB", "XDMG"])
        assert config.includes("XPHB") is True
        assert config.includes("XMM") is False

    def test_includes_case_insensitive(self):
        """Should match case-insensitively."""
        config = SourceConfig(sources=["XPHB"])
        assert config.includes("xphb") is True
        assert config.includes("Xphb") is True


class TestPresets:
    """Test preset configurations."""

    def test_2024_core_preset(self):
        """2024-core preset should have correct sources."""
        assert PRESETS["2024-core"] == ["XPHB", "XDMG", "XMM"]

    def test_2014_core_preset(self):
        """2014-core preset should have correct sources."""
        assert PRESETS["2014-core"] == ["PHB", "DMG", "MM"]

    def test_spelljammer_preset(self):
        """spelljammer preset should have correct sources."""
        assert "AAG" in PRESETS["spelljammer"]
        assert "BAM" in PRESETS["spelljammer"]


class TestKnownSources:
    """Test known sources list."""

    def test_2024_core_known(self):
        """2024 core sources should be known."""
        assert "XPHB" in KNOWN_SOURCES
        assert "XDMG" in KNOWN_SOURCES
        assert "XMM" in KNOWN_SOURCES

    def test_2014_core_known(self):
        """2014 core sources should be known."""
        assert "PHB" in KNOWN_SOURCES
        assert "DMG" in KNOWN_SOURCES
        assert "MM" in KNOWN_SOURCES
