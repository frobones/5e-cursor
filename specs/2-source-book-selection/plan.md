# Implementation Plan: Source Book Selection

**Branch**: `2-source-book-selection` | **Date**: 2026-01-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/2-source-book-selection/spec.md`

## Summary

Add configurable source book selection for D&D content extraction. Users specify sources via `sources.yaml` config file; defaults to 2024 core rulebooks (XPHB, XDMG, XMM). Supports Makefile override for quick testing.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyYAML (for config parsing)
**Storage**: YAML config file (`sources.yaml`)
**Testing**: pytest
**Target Platform**: CLI / Makefile
**Project Type**: Single project (scripts)
**Performance Goals**: N/A (extraction is already batch)
**Constraints**: Must not break existing extraction workflow
**Scale/Scope**: ~15 extractors to update

## Constitution Check

- [x] Reuse existing code patterns (extractors already support source filtering)
- [x] Simple configuration (single YAML file)
- [x] No new dependencies except PyYAML (already in requirements.txt)
- [x] Maintains backward compatibility (defaults work without config)

## Project Structure

### Documentation (this feature)

```text
specs/2-source-book-selection/
├── plan.md              # This file
├── research.md          # Design decisions
├── data-model.md        # Config schema
├── tasks.md             # Implementation tasks
└── spec.md              # Feature specification
```

### Source Code (repository root)

```text
# New files
sources.yaml.example     # Example config (committed)
sources.yaml             # User config (gitignored)

# Modified files
scripts/
├── extract_all.py       # Load config, pass to extractors
├── lib/
│   └── source_config.py # NEW: Config loader + presets
└── extractors/
    └── *.py             # Update to use sources list consistently
```

## Architecture

### Config Loading Flow

```
sources.yaml (or defaults)
        ↓
  SourceConfig.load()
        ↓
  List[str] sources
        ↓
  extract_all.py passes to each extractor
        ↓
  Extractors filter entries by source
```

### Component Changes

| Component | Change Type | Description |
|-----------|-------------|-------------|
| `scripts/lib/source_config.py` | New | Config loader with presets, defaults, validation |
| `scripts/extract_all.py` | Modify | Load config at start, pass sources to all extractors |
| `scripts/extractors/*.py` | Modify | Ensure consistent `sources` param handling |
| `Makefile` | Modify | Add SOURCES override, pass to Python script |
| `.gitignore` | Modify | Add `/sources.yaml` |
| `sources.yaml.example` | New | Example config for users |

## Implementation Phases

### Phase 1: Config Infrastructure

1. Create `scripts/lib/source_config.py` with:
   - `SourceConfig` dataclass
   - `load_config()` function
   - `PRESETS` dictionary
   - `DEFAULT_SOURCES` list
   - `KNOWN_SOURCES` set for validation

2. Add `pyyaml` to requirements.txt (if not present)

### Phase 2: Extract Script Integration

1. Modify `scripts/extract_all.py`:
   - Import and load config at start
   - Pass `sources` to all extractor functions
   - Update each `extract_*` function to use config sources

2. Add environment/CLI override support

### Phase 3: Makefile Integration

1. Add `SOURCES` variable support
2. Pass to Python script via environment or argument

### Phase 4: Documentation & Examples

1. Create `sources.yaml.example`
2. Update README with config instructions
3. Add to `.gitignore`

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Breaking existing workflow | Defaults match current behavior |
| Invalid source codes | Validate against KNOWN_SOURCES, warn but continue |
| Missing PyYAML | Already in requirements.txt via pytest |
