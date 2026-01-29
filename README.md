# 5e-cursor

D&D 5e reference data optimized for [Cursor AI](https://cursor.com). Extracts and indexes content from 5etools for efficient AI-assisted D&D gameplay.

## Quick Start

```bash
git clone https://github.com/frobones/5e-cursor.git
cd 5e-cursor
make
```

That's it. `make` initializes the submodule and extracts all reference data.

## What It Does

Extracts D&D 5e (2024) content from the 5etools data repository and converts it to:

- **Markdown files** - Human-readable reference documents
- **JSON indexes** - Fast lookups for AI context
- **Quick reference tables** - Compact stat summaries
- **Cross-reference files** - Grouped lookups (by CR, rarity, spell level, etc.)

## Source Books

| Book | Code | Type |
| ---- | ---- | ---- |
| Player's Handbook (2024) | XPHB | Core Rules |
| Dungeon Master's Guide (2024) | XDMG | Core Rules |
| Monster Manual (2024) | XMM | Core Rules |
| Astral Adventurer's Guide | AAG | Spelljammer |
| Boo's Astral Menagerie | BAM | Spelljammer |
| Light of Xaryxis | LoX | Adventure |
| Spelljammer Academy | SJA | Adventure |
| Eberron: Forge of the Artificer | EFA | Supplement (Artificer only) |

## Extracted Reference Data

| Category | Count | Path |
| -------- | ----- | ---- |
| Spells | 393 | `books/reference/spells/` |
| Creatures | 592 | `books/reference/creatures/` |
| Magic Items | 1,250 | `books/reference/items/` |
| Equipment | 264 | `books/reference/equipment/` |
| Classes | 13 + 53 subclasses | `books/reference/classes/` |
| Species | 21 | `books/reference/species/` |
| Feats | 77 | `books/reference/feats/` |
| Backgrounds | 18 | `books/reference/backgrounds/` |
| Rules/Conditions | 161 | `books/reference/rules/` |

See `books/README.md` for the complete list after extraction.

## AI-Optimized Indexes

| File | Purpose |
| ---- | ------- |
| `books/reference-index.json` | Master index (2,499 entries) |
| `books/keyword-index.json` | Semantic lookups (damage types, creature types, schools) |
| `books/cross-references/` | Grouped tables (creatures by CR, spells by level, etc.) |
| `books/reference/*/quick-reference.md` | Compact stat tables |

## Project Structure

```
5e-cursor/
├── 5etools-src/              # Git submodule (5etools data)
├── books/                    # Extracted content (gitignored)
│   ├── core/                 # Core rulebooks
│   ├── spelljammer/          # Setting & adventures
│   ├── eberron/              # EFA (Artificer)
│   ├── reference/            # Individual entries
│   ├── cross-references/     # Grouped tables
│   ├── reference-index.json  # Master index
│   └── keyword-index.json    # Keyword lookups
├── scripts/
│   ├── extract_all.py        # Main extraction script
│   ├── extract_book.py       # Book extraction library
│   └── extractors/           # Category extractors
├── .cursor/rules/            # Cursor AI rules
├── .cursorignore             # Excludes 5etools-src from Cursor
├── Makefile                  # Build commands
└── README.md
```

## Makefile Commands

| Command | Description |
| ------- | ----------- |
| `make` | Initialize submodule and extract (default) |
| `make extract` | Run extraction only |
| `make submodule` | Initialize/update submodule only |
| `make clean` | Remove extracted books/ |
| `make help` | Show available commands |

## Cursor Integration

The `.cursor/rules/dnd-reference-lookup.mdc` rule guides Cursor on how to efficiently look up D&D reference data. The 5etools-src submodule is excluded via `.cursorignore` to keep AI context focused on the extracted markdown.

## License

Extraction scripts are provided as-is. D&D content is property of Wizards of the Coast and is not redistributed in this repository. Run `make` to generate content locally from the 5etools submodule.
