# Research: Source Book Selection

## Design Decisions

### Default Sources

When no `sources.yaml` exists, use **2024 core rulebooks**:
- XPHB (2024 Player's Handbook)
- XDMG (2024 Dungeon Master's Guide)
- XMM (2024 Monster Manual)

**Rationale**: These are the current edition and what most new users will want.

### Config File Location

Use `sources.yaml` in the repository root.

**Rationale**: Simple, discoverable, follows convention of other config files.

### Cross-Source References

When content from source A references content from source B (e.g., a creature referencing a spell), and source B is not included:
- Extract the reference as plain text (not a link)
- Do not fail or warn for every broken reference

**Rationale**: This is the least disruptive approach. Users understand that excluding a source means losing those references.

## Available Source Codes

From 5etools data, common source codes include:

### 2024 Core (Default)
| Code | Full Name |
|------|-----------|
| XPHB | Player's Handbook (2024) |
| XDMG | Dungeon Master's Guide (2024) |
| XMM | Monster Manual (2024) |

### 2014 Core
| Code | Full Name |
|------|-----------|
| PHB | Player's Handbook (2014) |
| DMG | Dungeon Master's Guide (2014) |
| MM | Monster Manual (2014) |

### Supplements
| Code | Full Name |
|------|-----------|
| AAG | Astral Adventurer's Guide |
| BAM | Boo's Astral Menagerie |
| EFA | Eberron: Forge of the Artificer |
| TCE | Tasha's Cauldron of Everything |
| XGE | Xanathar's Guide to Everything |
| VGM | Volo's Guide to Monsters |
| MPMM | Mordenkainen Presents: Monsters of the Multiverse |

### Presets

| Preset | Sources |
|--------|---------|
| `2024-core` | XPHB, XDMG, XMM |
| `2014-core` | PHB, DMG, MM |
| `spelljammer` | XPHB, AAG, BAM |
| `all-2024` | XPHB, XDMG, XMM, plus any 2024-compatible supplements |

## Current Extractor Source Support

Reviewed extractors in `scripts/extractors/`:

| Extractor | Source Filtering | Notes |
|-----------|------------------|-------|
| SpellExtractor | `sources` param | Already supports list of sources |
| CreatureExtractor | Per-file filtering | Needs update to support config |
| ItemExtractor | `sources` param | Already supports list of sources |
| ClassExtractor | `source` param | Single source, needs update |
| FeatExtractor | Implicit | Filters by checking entry source |
| BackgroundExtractor | Implicit | Filters by checking entry source |
| SpeciesExtractor | Implicit | Filters by checking entry source |
| RulesExtractor | Implicit | Filters by checking entry source |

Most extractors already have source filtering capability. The main work is:
1. Create config loader
2. Pass sources consistently to all extractors
3. Update extractors that don't support multi-source filtering
