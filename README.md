# D&D Spelljammer Campaign Tool

A toolkit for running D&D 5th Edition Spelljammer campaigns, featuring automated extraction of reference materials from 5etools data.

## Quick Start

```bash
# Clone with submodules
git clone --recurse-submodules <repo-url>
cd dnd-tool

# Extract D&D reference books
python scripts/extract_all.py
```

## Features

- **Automated Book Extraction**: Convert 5etools JSON data to readable markdown
- **Spelljammer Focus**: Pre-configured for Spelljammer campaign materials
- **Organized Reference Library**: Structured chapters and creature indices

## Extracted Content

After running the extraction script, the following books are available in `books/`:

| Book | Code | Description |
| ---- | ---- | ----------- |
| Player's Handbook (2024) | XPHB | Core player rules, classes, spells |
| Dungeon Master's Guide (2024) | XDMG | DM rules, treasure, world-building |
| Monster Manual (2024) | XMM | Creature stat blocks |
| Astral Adventurer's Guide | AAG | Spelljammer rules, ships, Rock of Bral |
| Boo's Astral Menagerie | BAM | 72 Spelljammer creatures |
| Light of Xaryxis | LoX | Spelljammer adventure (levels 5-8) |
| Spelljammer Academy | SJA | Introductory adventure (levels 1-4) |

## Project Structure

```
dnd-tool/
├── 5etools-src/          # Git submodule - 5etools data source
├── books/                # Extracted markdown (gitignored)
│   ├── core/             # 2024 core rulebooks
│   └── spelljammer/      # Setting books and adventures
├── scripts/
│   ├── extract_all.py    # Extract all configured books
│   └── extract_book.py   # Core extraction library
└── README.md
```

## Scripts

### `scripts/extract_all.py`

Extracts all Spelljammer campaign books to the `books/` directory.

```bash
python scripts/extract_all.py
```

### `scripts/extract_book.py`

Extract individual books or bestiaries:

```bash
# Extract a book
python scripts/extract_book.py 5etools-src/data/book/book-xphb.json output/xphb/

# Extract a bestiary
python scripts/extract_book.py 5etools-src/data/bestiary/bestiary-mm.json output/mm/
```

## Adding More Books

To add additional books, edit `scripts/extract_all.py` and add entries to the `EXTRACTIONS` list:

```python
{
    "name": "Book Name",
    "source": DATA_DIR / "book" / "book-code.json",
    "output": BOOKS_DIR / "category" / "code",
},
```

## License

The extraction scripts are provided as-is. D&D content extracted from 5etools is property of Wizards of the Coast and is not redistributed in this repository.
