# 5e-cursor User Guide

This guide explains how to set up and use 5e-cursor for AI-first D&D 5e campaign management. Whether you prefer chatting with the AI in Cursor or running commands and browsing the Web UI, these documents cover everything.

## Who This Is For

- **DMs** who want to manage NPCs, locations, sessions, and encounters without memorizing commands
- **Players** who want to import and maintain D&D Beyond character sheets
- **Anyone** who wants rules lookups with citations, balanced encounter building, and a browsable campaign

No coding experience is required. The AI handles scripts and file structure; you use natural language or the Web UI.

## Documentation Map

| Document | What It Covers |
| -------- | -------------- |
| [Introduction](01-introduction.md) | High-level overview and "what you can do" |
| [Getting Started](02-getting-started.md) | Clone, install, first extraction, source configuration |
| [Campaign Setup](03-campaign-setup.md) | Initialize a campaign, `campaign.md`, directory layout, setting and themes |
| [Using the AI](04-using-the-ai.md) | How to work with Cursor AI, example prompts, rules and context |
| [Campaign Management](05-campaign-management.md) | NPCs, locations, sessions, encounters, party—workflows and CLI |
| [Web UI](06-web-ui.md) | Running the app, dashboard, search, timeline, relationships, live reload |
| [Reference Data](07-reference-data.md) | Extraction, source books, indexes, cross-references |
| [CLI Reference](08-cli-reference.md) | All campaign scripts and subcommands in one place |
| [Optional Tools](09-optional-tools.md) | Loot generator, session transcription, timeline, relationship graph |

## Recommended Path

1. **New to the project** → [Introduction](01-introduction.md) then [Getting Started](02-getting-started.md).
2. **Ready to run a campaign** → [Campaign Setup](03-campaign-setup.md) then [Using the AI](04-using-the-ai.md).
3. **Want to browse in a browser** → [Web UI](06-web-ui.md).
4. **Prefer typing commands** → [CLI Reference](08-cli-reference.md) and [Campaign Management](05-campaign-management.md).
5. **Advanced workflows** → [Optional Tools](09-optional-tools.md) (loot, transcription, timeline, relationships).

## Quick Reference

- **Start extraction:** `make` (from repo root)
- **Initialize campaign:** `make campaign-init NAME="Campaign Name"`
- **Try the demo:** `make demo-campaign` (extract sample campaign for testing)
- **Start Web UI:** `make web-ui` (starts backend and frontend; open http://localhost:5173). Stop with `make web-ui-stop`.
- **Ask the AI:** e.g. *"Build a hard encounter for my party"*, *"Add an NPC named Vex, tavern owner"*, *"What happened in session 3?"*

For full details, use the documents above.
