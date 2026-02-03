# Getting Started

This document walks you through cloning the repository, installing dependencies, running your first extraction, and configuring which source books to use.

## Prerequisites

- **Git** – to clone the repo and the 5etools submodule
- **Python 3.11+** – for all campaign and extraction scripts
- **Node.js 18+ and npm** – only if you want to run the [Web UI](06-web-ui.md)

No Cursor license is required for setup; you need Cursor (or another editor that can run terminal commands) when you want to use the AI workflows described in [Using the AI](04-using-the-ai.md).

## 1. Clone the Repository

```bash
git clone https://github.com/frobones/5e-cursor.git
cd 5e-cursor
```

If you use a fork, replace the URL with your fork. The repository includes a Git submodule (`5etools-src`) that holds the raw 5etools data.

## 2. Run Initial Setup

From the repository root:

```bash
make
```

This will:

1. Initialize and update the `5etools-src` submodule (if not already done)
2. Run the full extraction pipeline

Extraction reads the 5etools data and produces:

- **Markdown files** in `books/reference/` (spells, creatures, items, classes, species, feats, etc.)
- **JSON indexes** in `books/` (`reference-index.json`, `keyword-index.json`)
- **Cross-reference tables** in `books/cross-references/` (e.g. creatures by CR, spells by level)
- **Quick reference tables** in `books/reference/*/quick-reference.md`

The first run can take a few minutes. When it finishes, `books/` will contain thousands of reference entries. The `books/` directory is gitignored so your checkout stays small.

## 3. Python Virtual Environment (Recommended)

Use a virtual environment so project dependencies don’t conflict with system Python:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

From now on, activate `.venv` before running any Python scripts (campaign tools, Web UI backend, etc.).

## 4. Optional: Customize Source Books

By default, extraction uses a preset that includes **2024 Core + Spelljammer + Artificer** (XPHB, XDMG, XMM, AAG, BAM, LoX, SJA, EFA). To change what gets extracted:

### Option A: Config file

Copy the example and edit:

```bash
cp sources.yaml.example sources.yaml
```

Edit `sources.yaml`. For example, to use only 2024 core rules:

```yaml
preset: 2024-core
```

Or list specific sources:

```yaml
sources:
  - XPHB
  - XDMG
  - XMM
```

Then run:

```bash
make extract
```

### Option B: One-off command line

Override without a config file:

```bash
make extract SOURCES="XPHB,XDMG,XMM"
```

Available presets and source codes are documented in `sources.yaml.example`. See [Reference Data](07-reference-data.md) for more detail on extraction and indexes.

## 5. Verify Extraction

After `make` or `make extract`:

- `books/reference-index.json` should exist and contain thousands of entries
- Directories such as `books/reference/spells/`, `books/reference/creatures/` should contain markdown files

You can open any markdown file in `books/reference/` to confirm content. The AI and the Web UI use the indexes to look up these files.

## 6. Next Steps

- **Initialize a campaign** so you have party, NPCs, locations, and sessions: [Campaign Setup](03-campaign-setup.md)
- **Use the AI** for natural-language campaign tasks: [Using the AI](04-using-the-ai.md)
- **Run the Web UI** to browse campaign and reference data: [Web UI](06-web-ui.md)

## Troubleshooting

### Submodule fails to clone

If `make` or `git submodule update` fails:

- Ensure you have network access and (if applicable) SSH keys or credentials for the 5etools repo
- Run `git submodule update --init --recursive` manually and fix any reported errors

### Extraction fails or is incomplete

- Confirm Python 3.11+ is in use: `python --version`
- Ensure you’re in the repo root and the virtual environment is activated
- Check that `5etools-src/` exists and contains data (e.g. `5etools-src/data/`)
- Re-run `make extract` after fixing any missing dependencies (`pip install -r requirements.txt`)

### Books directory is empty after make

- `books/` is created by the extraction scripts; if extraction fails partway through, some folders may be missing
- Run `make clean` then `make` to start extraction from a clean state (this removes `books/` and re-extracts)
