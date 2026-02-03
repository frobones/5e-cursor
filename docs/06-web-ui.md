# Web UI

The Campaign Web UI is a browser-based viewer for your campaign and reference data. You can browse NPCs, locations, sessions, party, encounters, timeline, and relationships, and search across everything without using the terminal or Cursor.

## Prerequisites

- **Python 3.11+** and project dependencies installed (`pip install -r requirements.txt`)
- **Node.js 18+** and npm
- **Initialized campaign** – run `python scripts/campaign/init_campaign.py "Your Campaign"` if you haven’t already
- **Reference data** – run `make` so the reference browser and search have content

## Demo Campaign

Want to explore the Web UI without setting up your own campaign? Extract the included demo campaign:

```bash
make demo-campaign
```

This unpacks a sample Spelljammer campaign with sessions, NPCs, locations, encounters, and a party character. Then run `make web-ui` to explore.

To remove the demo campaign:

```bash
make demo-campaign-clean
```

This only removes the demo campaign (it checks for a marker file). If you've created your own campaign, the command will refuse to delete it.

## Running the Web UI

### Quick start (one command)

From the repository root:

```bash
make web-ui
```

This starts the backend and frontend in the background. Open **http://localhost:5173** in your browser. To stop both servers:

```bash
make web-ui-stop
```

### Running in separate terminals

If you prefer to see backend and frontend logs in two terminals:

**Terminal 1 – Backend** (with virtual environment activated):

```bash
cd scripts && python -m web.main
```

Or with uvicorn: `uvicorn scripts.web.main:app --reload --port 8000`. API: `http://localhost:8000`.

**Terminal 2 – Frontend:**

```bash
cd frontend
npm run dev
```

App: **http://localhost:5173**. The frontend proxies `/api` and `/ws` to the backend.

## Main Features

### Dashboard

The home page shows:

- Campaign name and setting (if set in `campaign/campaign.md`)
- Counts for NPCs, locations, sessions, and party size (each clickable to the list view)
- Quick navigation cards to NPCs, Locations, Sessions, Party, Encounters, Timeline, Relationships, Reference
- Recent sessions with links to session detail

### Entity Browsing

- **NPCs** – List with role badges; click a card to open the NPC detail page. Filter by role (ally, neutral, enemy) if needed.
- **Locations** – List and detail with region, type, and discovery date when present.
- **Sessions** – Session list and full session detail with markdown-rendered summary.
- **Party** – Party overview and individual character sheets (markdown-rendered, with links to reference content).
- **Encounters** – List of saved encounters; open one to see difficulty, party level/size, and creature list. Click **Run Combat** to start the combat tracker.

All list items are clickable cards; breadcrumbs and sidebar help you navigate back.

### Encounter Builder

Build balanced encounters directly in the browser:

1. Go to **Encounters** → **Build New Encounter** (or `/encounters/builder`)
2. Set party level and size (or it auto-detects from your party)
3. Search and add creatures from the reference data
4. Watch the difficulty rating update in real-time (Easy, Medium, Hard, Deadly)
5. Click **Save Encounter** to add it to your campaign

The difficulty calculator uses the 2024 DMG XP thresholds.

### Combat Tracker

Run encounters with full combat management:

1. Open an encounter and click **Run Combat** (or **Resume Combat** if one is in progress)
2. **Party Selection** – Choose which party members are in the fight
3. **Initiative Setup** – Roll initiative for monsters (grouped by creature type) and enter player initiatives. A roll log shows each d20 + modifier.
4. **Combat Round** – Track initiative order, HP, conditions, and damage history for each combatant

Features:
- **Creature Stats Panel** – Click a monster to see its full stat block (AC, HP, abilities, actions)
- **Character Stats Panel** – Click a PC to see their character sheet
- **Damage/Healing** – Apply damage or healing with a single click
- **Conditions** – Add/remove conditions (prone, stunned, etc.)
- **Save & Exit** – Pause combat and return later; state is preserved
- **End Combat** – Finish the encounter and clear state

### Global Search (Cmd+K / Ctrl+K)

Press **Cmd+K** (macOS) or **Ctrl+K** (Windows/Linux) anywhere to open the search modal. Type to search across:

- Campaign: NPCs, locations, sessions, characters, encounters
- Reference: spells, creatures, items, and other reference types

Results are grouped by type. Click a result to go to that entity’s or reference’s page.

### Timeline

Go to **Timeline** (sidebar or `/timeline`) for a chronological view of campaign events:

- Sessions (with in-game date when set)
- NPC first appearances
- Location discoveries
- Custom events from `campaign/events.md` (if you use the [timeline generator](09-optional-tools.md#campaign-timeline))

Events that link to a session or entity are clickable.

### Relationship Graph

Go to **Relationships** (sidebar or `/relationships`) to see:

- A **Mermaid diagram** of NPC connections (from `campaign_manager.py add-relationship` or the `## Connections` sections in NPC files)
- A list of **NPCs** with connection counts; each NPC is a link to their detail page
- An **All Connections** list (source → type → target) with clickable names

Generate or update the underlying data with `python scripts/campaign/relationship_graph.py` (see [Optional Tools](09-optional-tools.md#npc-relationship-graph)).

### Reference Browser

Use **Reference** (sidebar or `/reference`) to browse extracted D&D content:

- **Types** – Spells, creatures, items, classes, species, feats, backgrounds, rules, etc.
- **Filters** – By level (spells), CR (creatures), rarity (items), etc., depending on type
- **Detail pages** – Full markdown content with cross-links to other reference entries

Links in campaign content (e.g. spell names in a character sheet) open in the reference browser when possible.

### Cross-References in Content

Inside markdown content (NPCs, locations, sessions, character sheets, encounters):

- **Campaign links** – NPC and location names link to their campaign detail pages.
- **Reference links** – Spells, items, and other reference terms link to the reference browser (often with a tooltip preview).

### Dark Mode

Use the sun/moon icon in the header to toggle light and dark theme. The choice is stored in your browser (localStorage).

### Live Reload

When campaign files change on disk (e.g. you edit an NPC in Cursor or run a CLI command), the Web UI receives a notification over WebSocket and can refresh data. You may need to navigate away and back or use search again to see the latest content, depending on the page.

## Troubleshooting

### “No campaign found”

Initialize a campaign from the repo root:

```bash
python scripts/campaign/init_campaign.py "Your Campaign"
```

### Blank or missing reference data

Run extraction so `books/` is populated:

```bash
make
```

### Backend not responding

- Ensure the backend process is running and listening on port 8000.
- Check for errors in the terminal where you started the backend.
- From another terminal: `curl http://localhost:8000/api/campaign` (or the health endpoint if documented).

### Frontend won’t start or build

- From `frontend/`: run `npm install`, then `npm run dev` again.
- If issues persist, try `rm -rf node_modules && npm install`.

### Search or reference empty

- Confirm `books/reference-index.json` exists (run `make` if needed).
- Ensure the backend can read the `books/` and `campaign/` directories (correct working directory and permissions).

For more on running and developing the app, see the spec quickstart: `specs/8-campaign-web-ui/quickstart.md`.
