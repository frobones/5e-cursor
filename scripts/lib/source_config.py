"""
Source book configuration for D&D content extraction.

Allows users to specify which source books to include via:
1. sources.yaml config file
2. DND_SOURCES environment variable
3. Makefile SOURCES variable
4. Default sources (2024 core)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


# Default sources when no config exists (matches original extraction)
DEFAULT_SOURCES = [
    # 2024 Core
    "XPHB", "XDMG", "XMM",
    # Spelljammer
    "AAG", "BAM", "LoX", "SJA",
    # Eberron (Artificer only)
    "EFA",
]

# Named presets for common configurations
PRESETS = {
    "default": ["XPHB", "XDMG", "XMM", "AAG", "BAM", "LoX", "SJA", "EFA"],
    "2024-core": ["XPHB", "XDMG", "XMM"],
    "2014-core": ["PHB", "DMG", "MM"],
    "spelljammer": ["XPHB", "XDMG", "XMM", "AAG", "BAM", "LoX", "SJA", "EFA"],
    "spelljammer-minimal": ["XPHB", "AAG", "BAM"],
}

# Known valid source codes for validation
KNOWN_SOURCES = {
    # 2024 Core
    "XPHB", "XDMG", "XMM",
    # 2014 Core
    "PHB", "DMG", "MM",
    # Major Supplements
    "TCE", "XGE", "MPMM", "FTD", "VGM", "MTF", "BGG",
    # Spelljammer
    "AAG", "BAM", "LoX", "SJA",
    # Eberron
    "ERLW", "ERLW-FULL", "EFA", "EFA-FULL",
    # Wildemount
    "EGW", "EGW-FULL",
    # Settings
    "GGR", "MOT", "SCC", "EGW", "VRGR", "SCAG",
    # Other Supplements
    "AI", "WBtW", "DSotDQ", "PAitM", "SatO", "BMT", "VEoR", "QftIS",
    # Adventures
    "CoS", "LMoP", "HotDQ", "RoT", "PotA", "OotA", "SKT", "TftYP",
    "ToA", "WDH", "WDMM", "GoS", "DC", "DIP", "SLW", "SDW", "BGDIA",
    "IDRotF", "CM", "CRCotN", "JttRC", "KftGV", "PaBTSO", "DoSI",
    # Third Party
    "HWCS", "HWAitW", "ToB", "ToB2", "CC", "GHLoE", "DoDk", "ToD",
}


@dataclass
class SourceConfig:
    """Configuration for source book filtering."""

    sources: list[str] = field(default_factory=lambda: DEFAULT_SOURCES.copy())
    """List of source codes to include in extraction."""

    @classmethod
    def load(cls, config_path: Optional[Path] = None, repo_root: Optional[Path] = None) -> "SourceConfig":
        """Load source configuration.

        Priority order:
        1. DND_SOURCES environment variable
        2. Config file (sources.yaml)
        3. Default sources

        Args:
            config_path: Explicit path to config file. If None, looks for sources.yaml in repo root.
            repo_root: Repository root directory. If None, auto-detected.

        Returns:
            SourceConfig instance
        """
        # Check environment variable first
        env_sources = os.environ.get("DND_SOURCES")
        if env_sources:
            sources = [s.strip().upper() for s in env_sources.split(",") if s.strip()]
            config = cls(sources=sources)
            warnings = config.validate()
            for warning in warnings:
                print(f"  Warning: {warning}")
            return config

        # Find repo root if not provided
        if repo_root is None:
            repo_root = cls._find_repo_root()

        # Determine config path
        if config_path is None and repo_root:
            config_path = repo_root / "sources.yaml"

        # Load from config file if it exists
        if config_path and config_path.exists():
            return cls._load_from_yaml(config_path)

        # Return defaults
        return cls()

    @classmethod
    def _find_repo_root(cls) -> Optional[Path]:
        """Find the repository root by looking for marker files."""
        current = Path(__file__).resolve()
        while current.parent != current:
            if (current / "Makefile").exists() and (current / "scripts").exists():
                return current
            current = current.parent
        return None

    @classmethod
    def _load_from_yaml(cls, config_path: Path) -> "SourceConfig":
        """Load configuration from YAML file.

        Args:
            config_path: Path to sources.yaml

        Returns:
            SourceConfig instance
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            print(f"  Error: Invalid YAML in {config_path}: {e}")
            print("  Using default sources.")
            return cls()

        sources = []

        # Check for explicit sources list
        if "sources" in data and isinstance(data["sources"], list):
            sources = [s.strip().upper() for s in data["sources"] if isinstance(s, str)]

        # Check for preset
        elif "preset" in data:
            preset_name = data["preset"]
            if preset_name in PRESETS:
                sources = PRESETS[preset_name].copy()
                print(f"  Using preset '{preset_name}': {', '.join(sources)}")
            else:
                print(f"  Warning: Unknown preset '{preset_name}'. Available: {', '.join(PRESETS.keys())}")
                print("  Using default sources.")
                return cls()

        # Add additional sources if specified
        if "additional_sources" in data and isinstance(data["additional_sources"], list):
            additional = [s.strip().upper() for s in data["additional_sources"] if isinstance(s, str)]
            for src in additional:
                if src not in sources:
                    sources.append(src)

        # Use defaults if no sources specified
        if not sources:
            return cls()

        config = cls(sources=sources)
        warnings = config.validate()
        for warning in warnings:
            print(f"  Warning: {warning}")

        return config

    def validate(self) -> list[str]:
        """Validate source codes against known sources.

        Returns:
            List of warning messages for unknown sources
        """
        warnings = []
        for source in self.sources:
            if source not in KNOWN_SOURCES:
                warnings.append(f"Unknown source code '{source}' - may not match any data")
        return warnings

    def includes(self, source: str) -> bool:
        """Check if a source is included in the configuration.

        Args:
            source: Source code to check

        Returns:
            True if source is included
        """
        return source.upper() in [s.upper() for s in self.sources]

    def __str__(self) -> str:
        return f"SourceConfig(sources={self.sources})"
