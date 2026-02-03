# Quickstart: Campaign Web UI

A web-based viewer for navigating your D&D campaign data.

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- An initialized campaign (`python scripts/campaign/init_campaign.py "Your Campaign"`)

## Installation

### 1. Install Python Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install web UI dependencies
pip install -r requirements.txt
```

### 2. Install Node Dependencies

```bash
cd frontend
npm install
```

## Running the Application

You need two terminals - one for the backend and one for the frontend.

### Terminal 1: Start the Backend

```bash
# From repository root
source .venv/bin/activate
uvicorn scripts.web.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Terminal 2: Start the Frontend

```bash
cd frontend
npm run dev
```

The web UI will be available at `http://localhost:5173`.

## Key Features

### Global Search (Cmd+K)

Press `Cmd+K` (or `Ctrl+K` on Windows/Linux) anywhere to open the global search modal. Search across:
- NPCs, locations, sessions, characters
- Reference data (spells, creatures, items)

### Timeline View

Navigate to `/timeline` to see a chronological view of campaign events including:
- Sessions with in-game dates
- NPC first appearances
- Location discoveries
- Custom events from `campaign/events.md`

### Relationship Graph

Navigate to `/relationships` to see an interactive Mermaid diagram of NPC connections. Click on any node to view that NPC's details.

### Dark Mode

Click the sun/moon icon in the header to toggle between light and dark themes. Your preference is saved to localStorage.

### Live Reload

The web UI automatically refreshes when campaign files change. Edit an NPC with the CLI or your text editor, and the browser updates instantly via WebSocket.

## Features

### Dashboard

The home page shows:
- Campaign name and setting
- Quick stats (NPCs, locations, sessions, party size)
- Recent sessions
- Quick navigation links

### Entity Browsing

- **NPCs**: Filter by role (ally, neutral, enemy)
- **Locations**: Browse all discovered places
- **Sessions**: View session history
- **Party**: See party members and character sheets
- **Encounters**: Review saved encounters

### Cross-References

Click any link in the content to navigate:
- NPC names link to their detail pages
- Locations link to location details
- References (spells, items) link to the reference browser

### Reference Browser

Browse extracted D&D content:
- Spells (filterable by level)
- Creatures (filterable by CR)
- Items (filterable by rarity)
- Rules and conditions

### Theme Toggle

Click the sun/moon icon in the header to switch between light and dark modes.

## Development

### Backend Structure

```
scripts/web/
├── main.py           # FastAPI application
├── api/              # Route handlers
│   ├── campaign.py   # Campaign endpoints
│   ├── entities.py   # NPC, location, session endpoints
│   ├── reference.py  # Reference data endpoints
│   └── search.py     # Search endpoint
├── models/           # Pydantic response models
└── services/         # Business logic
```

### Frontend Structure

```
frontend/src/
├── components/       # Reusable UI components
│   ├── layout/      # Header, Sidebar, Layout
│   └── markdown/    # Markdown renderer
├── pages/           # Route-based pages
├── services/        # API client
├── styles/          # Global CSS
└── types/           # TypeScript types
```

### Adding New Features

1. Add API endpoint in `scripts/web/api/`
2. Add Pydantic models in `scripts/web/models/`
3. Add service logic in `scripts/web/services/`
4. Add React page in `frontend/src/pages/`
5. Add route in `frontend/src/App.tsx`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/campaign` | Campaign overview |
| `GET /api/npcs` | List NPCs |
| `GET /api/npcs/{slug}` | NPC detail |
| `GET /api/locations` | List locations |
| `GET /api/locations/{slug}` | Location detail |
| `GET /api/sessions` | List sessions |
| `GET /api/sessions/{number}` | Session detail |
| `GET /api/party` | Party overview |
| `GET /api/party/characters/{slug}` | Character detail |
| `GET /api/encounters` | List encounters |
| `GET /api/encounters/{slug}` | Encounter detail |
| `GET /api/reference` | Reference index |
| `GET /api/reference/{type}` | List by type |
| `GET /api/reference/{type}/{slug}` | Reference detail |
| `GET /api/search?q=...` | Full-text search |
| `WS /ws` | WebSocket for live file changes |

## Troubleshooting

### "No campaign found"

Initialize a campaign first:

```bash
python scripts/campaign/init_campaign.py "Your Campaign"
```

### API not responding

Check that the backend is running on port 8000:

```bash
curl http://localhost:8000/api/health
```

### Reference data empty

Extract reference data:

```bash
make
```

### Frontend build errors

Try clearing node_modules and reinstalling:

```bash
cd frontend
rm -rf node_modules
npm install
```
