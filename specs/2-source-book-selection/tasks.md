# Tasks: Source Book Selection

## Phase 1: Config Infrastructure

- [X] **Task 1.1**: Create `scripts/lib/source_config.py`
  - SourceConfig dataclass
  - load() classmethod
  - PRESETS dictionary
  - DEFAULT_SOURCES list
  - KNOWN_SOURCES set
  - validate() method

- [X] **Task 1.2**: Add PyYAML to requirements.txt (if not present)

- [X] **Task 1.3**: Create unit tests for source_config.py
  - Test default loading
  - Test YAML parsing
  - Test preset expansion
  - Test validation warnings

## Phase 2: Extract Script Integration

- [X] **Task 2.1**: Modify `scripts/extract_all.py` to load config
  - Import SourceConfig
  - Load at script start
  - Store in module-level variable

- [X] **Task 2.2**: Update spell extraction to use config sources
  - Pass sources to SpellExtractor

- [X] **Task 2.3**: Update creature extraction to use config sources
  - Pass sources to CreatureExtractor
  - Update per-file filtering

- [X] **Task 2.4**: Update item extraction to use config sources
  - Already supports sources param

- [X] **Task 2.5**: Update class extraction to use config sources
  - Update ClassExtractor to support multiple sources
  - Update class feature extraction

- [X] **Task 2.6**: Update remaining extractors to use config sources
  - FeatExtractor
  - BackgroundExtractor
  - SpeciesExtractor
  - RulesExtractor
  - EquipmentExtractor
  - VehicleExtractor
  - OptionalFeatureExtractor
  - TrapExtractor
  - Misc extractors

## Phase 3: Makefile Integration

- [X] **Task 3.1**: Add SOURCES variable to Makefile
  - Pass to extract command via environment

- [X] **Task 3.2**: Support DND_SOURCES environment variable
  - Check in source_config.py

## Phase 4: Documentation & Examples

- [X] **Task 4.1**: Create `sources.yaml.example`
  - Show explicit sources
  - Show preset usage
  - Show additional_sources

- [X] **Task 4.2**: Add `sources.yaml` to .gitignore

- [X] **Task 4.3**: Update README with source selection docs
  - Config file usage
  - Available presets
  - Makefile override

## Phase 5: Testing

- [X] **Task 5.1**: Add integration test for filtered extraction
  - Extract with subset of sources
  - Verify index only contains those sources

- [X] **Task 5.2**: Test Makefile override

- [X] **Task 5.3**: Test default behavior (no config)
