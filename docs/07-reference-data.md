# Reference Data

5e-cursor uses D&D 5e content extracted from the [5etools](https://5e.tools) data repository. This document explains what gets extracted, where it lives, how to configure sources, and how the indexes and cross-references work.

## What Gets Extracted

The extraction pipeline reads the 5etools submodule (`5etools-src/`) and produces:

| Output | Description |
| ------ | ----------- |
| **Markdown files** | One file per spell, creature, item, class, species, feat, etc. in `books/reference/<category>/` |
| **reference-index.json** | Master index: normalized name → list of { path, source, type } for fast lookups |
| **keyword-index.json** | Semantic index: damage types, creature types, spell schools, etc. for “find by keyword” style queries |
| **cross-references/** | Grouped tables, e.g. creatures by CR, spells by level, items by rarity |
| **quick-reference.md** | Per-category compact stat/summary tables |

The AI and the Web UI use these so they can resolve names (e.g. “fireball”, “goblin”) to the right markdown file without scanning the filesystem.

## Default Sources

By default, extraction uses a preset that includes:

- **2024 Core:** XPHB (Player’s Handbook), XDMG (Dungeon Master’s Guide), XMM (Monster Manual)
- **Spelljammer:** AAG, BAM, LoX, SJA (Astral Adventurer’s Guide, Boo’s Astral Menagerie, Light of Xaryxis, Spelljammer Academy)
- **Artificer:** EFA (Eberron: Forge of the Artificer, class only)

So after `make` you get core 2024 rules plus Spelljammer content and the Artificer class.

## Customizing Sources

### Presets

In `sources.yaml` (copy from `sources.yaml.example`) you can set:

```yaml
preset: 2024-core
```

Common presets include:

- **2024-core** – XPHB, XDMG, XMM only
- **spelljammer** – 2024 core + Spelljammer + Artificer (often the default)
- Others as defined in `sources.yaml.example`

### Explicit Source List

Instead of a preset, list source codes:

```yaml
sources:
  - XPHB
  - XDMG
  - XMM
  - AAG
  - BAM
```

Source codes are listed in the README and in `sources.yaml.example` (e.g. XPHB, XDMG, XMM, AAG, BAM, LoX, SJA, EFA).

### Command-Line Override

For a one-off extraction without changing the config file:

```bash
make extract SOURCES="XPHB,XDMG,XMM"
```

This overrides whatever is in `sources.yaml` for that run.

## Where Things Live

- **books/reference/spells/** – One markdown file per spell
- **books/reference/creatures/** – One file per creature/monster
- **books/reference/items/** – Magic items
- **books/reference/equipment/** – Weapons, armor, gear
- **books/reference/classes/** – Classes and subclasses
- **books/reference/species/** – Species (races)
- **books/reference/feats/** – Feats
- **books/reference/backgrounds/** – Backgrounds
- **books/reference/rules/** – Rules and conditions (e.g. prone, stunned)
- **books/core/** – Core rulebook content (if extracted)
- **books/reference-index.json** – Root of the repo under `books/`
- **books/keyword-index.json** – Same
- **books/cross-references/** – Grouped lookup tables

The exact categories and counts depend on the sources you extract; see the README table for typical counts.

## How the AI Uses Reference Data

Cursor rules (e.g. `.cursor/rules/dnd-reference-lookup.mdc`) tell the AI to:

1. Resolve names (spell, creature, item, rule) using the reference index and any aliases (e.g. equipment name variants from D&D Beyond).
2. Read the corresponding markdown file(s) when it needs to cite rules, stats, or text.
3. Use keyword and cross-reference data when you ask for things like “CR 3 creatures” or “level 2 spells”.

So when you ask “How does fireball work?” or “What’s the AC of a goblin?”, the AI looks up the right file and answers from that content.

## How the Web UI Uses Reference Data

- **Reference browser** – Lists and detail pages are built from the same markdown and index data. Filters (e.g. by level, CR, rarity) use metadata in the index or in the files.
- **Search** – Global search (Cmd+K) includes reference entries; results link to the reference detail page for that type and slug.
- **Cross-links** – When campaign content (e.g. a character sheet) contains a reference link, the Web UI can open that reference in the reference browser or show a tooltip.

## Re-running Extraction

- **Full re-extract:** `make` (or `make extract` if the submodule is already in place). This overwrites `books/` with a fresh extraction.
- **Clean then extract:** `make clean` removes `books/`, then `make` extracts again. Use this if the output is corrupted or you want a clean slate.

After changing `sources.yaml` or the source list, run `make extract` (or `make`) so the indexes and markdown reflect the new set of sources.
