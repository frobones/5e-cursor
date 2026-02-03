# Using the AI

5e-cursor is designed for **AI-first** workflow: you tell the AI what you want in plain English, and it uses the reference data and campaign tools to do it. This document explains how to get the most out of Cursor (or a similar AI assistant) with this project.

## How It Works

1. **Reference data** – The extracted markdown and JSON indexes in `books/` give the AI access to spells, creatures, items, rules, and conditions. Cursor rules (e.g. `.cursor/rules/dnd-reference-lookup.mdc`) guide it on how to look up this data efficiently.

2. **Campaign data** – The AI can read and edit files in `campaign/`: party, NPCs, locations, sessions, encounters. It understands the structure from the index files and markdown conventions.

3. **Campaign tools** – When you ask for something that requires a script (e.g. import a character, build an encounter), the AI runs the appropriate Python script from `scripts/campaign/` and interprets the result.

You don’t need to memorize script names or flags; describe the goal and the AI chooses the tool and arguments.

## What to Ask

### Character and Party

| You say | What the AI does |
| -------- | ----------------- |
| *"Import my character from D&D Beyond: [paste URL]"* | Runs `import_character.py import <url>`, creates a character markdown file and updates the party index |
| *"Update all my characters from D&D Beyond"* | Runs update for each imported character |
| *"What spells does Meilin have prepared?"* | Reads the character sheet in `campaign/party/characters/` and lists prepared spells |
| *"List the party"* | Reads `campaign/party/index.md` and/or character files |

### Encounters

| You say | What the AI does |
| -------- | ----------------- |
| *"Build a hard encounter for my party"* | Reads party level/size from campaign data, runs `encounter_builder.py` with appropriate difficulty |
| *"Build an encounter for 4 level 5 characters, medium difficulty, undead"* | Runs encounter builder with those parameters |
| *"Save this encounter as goblin-ambush"* | Writes the encounter to `campaign/encounters/goblin-ambush.md` and updates the encounter index |

### Rules and Reference

| You say | What the AI does |
| -------- | ----------------- |
| *"How does the prone condition work?"* | Looks up the condition in reference data and returns the rule with citation |
| *"What’s the range of fireball?"* | Looks up the spell and reports range (and other details if relevant) |
| *"What’s a good CR 3 creature for a swamp?"* | Uses reference/cross-reference data to suggest creatures and may summarize stats |

### Sessions

| You say | What the AI does |
| -------- | ----------------- |
| *"Create a new session called 'Into the Underdark'"* | Runs `session_manager.py new "Into the Underdark"` and updates the session index |
| *"What happened in session 3?"* | Reads `campaign/sessions/session-003.md` and summarizes |
| *"When did we last see Captain Vex?"* | Searches session summaries and NPC/location references for that NPC |

### NPCs and Locations

| You say | What the AI does |
| -------- | ----------------- |
| *"Add an NPC named Vex, she’s a tavern owner, ally"* | Runs `campaign_manager.py add-npc` or creates the NPC file and updates the index |
| *"Create a blacksmith NPC for the market district"* | May check for name conflicts, link to the market district location, and generate a rich NPC (description, personality, secrets) using AI and reference data |
| *"Add a hidden temple in the forest"* | Creates a location file, optionally links to nearby locations and NPCs |
| *"List all NPCs"* | Reads `campaign/npcs/index.md` or lists NPC files |

The AI uses the campaign’s **setting** and **themes** from `campaign/campaign.md` to keep tone and world-building consistent.

## Cursor Rules

The project includes rules in `.cursor/rules/` that steer the AI:

- **dnd-reference-lookup.mdc** – How to look up spells, creatures, items, rules from the extracted data and indexes
- **campaign-lookup.mdc** – How to find and use campaign data (party, NPCs, locations, sessions)
- **npc-location-generation.mdc** – How to generate NPCs and locations that fit the campaign
- **spec-first-development.mdc** – For contributors: work from specs and branches

You don’t need to read these unless you’re curious or customizing behavior; the AI loads them automatically in Cursor.

## Tips for Best Results

1. **Be specific when it helps** – e.g. *"Build a hard encounter for 4 level 5 characters, prefer undead"* is clearer than *"Build an encounter."*
2. **Mention context** – e.g. *"Add a blacksmith NPC in the market district"* lets the AI link the NPC to that location.
3. **Ask for one logical task at a time** – e.g. create one session, then add notes, rather than one long message that does five things.
4. **Confirm destructive or big changes** – If the AI suggests deleting or rewriting many files, double-check before accepting.

## When the AI Runs Scripts

The AI will run commands in your project (e.g. in the integrated terminal). For that to work:

- You need to be in the repository root (or the AI should `cd` there).
- Python should be the one from your virtual environment (activate `.venv` first in that terminal if needed).
- Scripts are run as: `python scripts/campaign/<script>.py <args>`.

If a command fails, the AI can read the error and suggest a fix (e.g. missing dependency, wrong path, or invalid argument).

## Next Steps

- See [Campaign Management](05-campaign-management.md) for detailed workflows and CLI equivalents.
- See [CLI Reference](08-cli-reference.md) for all script options if you prefer to run commands yourself.
