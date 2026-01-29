# 5e-cursor: AI-first D&D Campaign Management

**Using 5etools data to power your campaign through natural language.**

## What It Is

An open-source tool that extracts 5etools D&D 5e content and converts it into markdown files and JSON indexes optimized for AI context. It's designed to work with [Cursor](https://cursor.com)—a free code editor with built-in AI that can read your files and run commands. You don't need to be a developer to use it; once set up, you just chat with the AI in plain English to manage your campaign.

## What You Can Do

- Import characters from D&D Beyond with auto-linked features
- Build balanced encounters using DMG XP thresholds
- Look up rules, spells, creatures, items with citations
- Track sessions, NPCs, and locations
- Generate rich NPCs and locations from simple prompts

## Campaign Management That Grows With Your World

Your campaign lives in organized markdown files—party roster, NPCs, locations, session summaries, and encounters. The AI can read all of it, so it understands your world's context. When you say *"Create a blacksmith NPC for the market district"*, it checks for name conflicts, connects them to existing locations, and generates a full profile with personality, secrets, and stat block.

Session tracking lets you record what happened each session. Later you can ask *"What happened in session 3?"* or *"When did we last see Captain Vex?"* and get answers based on your actual session notes. The AI maintains awareness of your party composition, NPC relationships, and campaign history—so suggestions stay consistent with your established world.

## How It Works

```bash
git clone https://github.com/frobones/5e-cursor.git
cd 5e-cursor
make
```

The extraction pulls from the 5etools submodule and creates ~2,500 indexed entries across spells, creatures, items, classes, feats, etc. Sources are fully configurable via `sources.yaml` or command line—use presets like `2024-core` or `spelljammer`, or specify individual source codes to pull exactly what you need.

Instead of memorizing commands, you just ask the AI things like *"Build a hard encounter for my party"* or *"How does the prone condition work?"* and it handles the lookups and tool invocations.

## Learn More

See the [README](../README.md) for full documentation, including:

- Source book configuration
- Campaign initialization
- CLI reference
- Project structure

## Acknowledgments

This project wouldn't be possible without the [5etools](https://5e.tools) team maintaining such well-structured data.
