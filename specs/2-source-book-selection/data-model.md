# Data Model: Source Book Selection

## Config File Schema

### sources.yaml

```yaml
# Option 1: Explicit source list
sources:
  - XPHB
  - XDMG
  - XMM

# Option 2: Use a preset
preset: 2024-core

# Option 3: Preset plus additional sources
preset: 2024-core
additional_sources:
  - AAG
  - BAM
```

### Field Definitions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sources` | list[str] | No | Explicit list of source codes to include |
| `preset` | str | No | Named preset that expands to a list of sources |
| `additional_sources` | list[str] | No | Extra sources to add when using a preset |

**Note**: Either `sources` or `preset` should be specified. If both are present, `sources` takes precedence.

## Source Presets

```python
PRESETS = {
    "2024-core": ["XPHB", "XDMG", "XMM"],
    "2014-core": ["PHB", "DMG", "MM"],
    "spelljammer": ["XPHB", "AAG", "BAM"],
    "all-2024": ["XPHB", "XDMG", "XMM", "XPHB2024", "EFA"],
}
```

## Default Sources

When no config file exists:

```python
DEFAULT_SOURCES = ["XPHB", "XDMG", "XMM"]
```

## Known Source Codes

For validation purposes:

```python
KNOWN_SOURCES = {
    # 2024 Core
    "XPHB", "XDMG", "XMM",
    # 2014 Core
    "PHB", "DMG", "MM",
    # Supplements
    "AAG", "BAM", "EFA", "TCE", "XGE", "VGM", "MPMM",
    "SCAG", "MTF", "GGR", "AI", "ERLW", "EGW", "MOT",
    "FTD", "SCC", "WBtW", "DSotDQ", "BGG", "PAitM", "SatO",
    "ToD", "BMT", "VEoR", "QftIS",
    # Add more as discovered
}
```

## SourceConfig Class

```python
@dataclass
class SourceConfig:
    """Configuration for source book filtering."""
    
    sources: list[str]
    """List of source codes to include in extraction."""
    
    @classmethod
    def load(cls, config_path: Path = None) -> "SourceConfig":
        """Load config from file or return defaults."""
        ...
    
    @classmethod
    def from_env(cls) -> "SourceConfig":
        """Load from DND_SOURCES environment variable."""
        ...
    
    def validate(self) -> list[str]:
        """Return list of warnings for unknown sources."""
        ...
```

## Environment Variable

```bash
# Override via environment
export DND_SOURCES="XPHB,XMM"
make extract

# Or inline
DND_SOURCES="XPHB,XMM" make extract
```

## Makefile Variable

```makefile
# Override via make variable
make extract SOURCES="XPHB,XMM"
```

Priority order (highest first):
1. Makefile `SOURCES` variable
2. `DND_SOURCES` environment variable
3. `sources.yaml` file
4. Default sources
