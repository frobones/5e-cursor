"""
Visualization service for timeline and relationship graph.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(scripts_dir))

from lib.campaign_calendar import parse_in_game_date
from lib.markdown_writer import slugify
from lib.relationship_parser import parse_connections_from_file

from web.models.visualizations import (
    TimelineEvent,
    TimelineDay,
    TimelineResponse,
    RelationshipNode,
    RelationshipEdge,
    RelationshipGraphResponse,
)
from web.services.campaign import get_campaign_dir


class VisualizationService:
    """Service for visualization data."""

    def __init__(self) -> None:
        """Initialize the visualization service."""
        self.campaign_dir = get_campaign_dir()

    def get_timeline(self) -> TimelineResponse:
        """Get timeline data for visualization."""
        events: list[TimelineEvent] = []

        # Collect session events
        events.extend(self._collect_session_events())

        # Collect NPC first appearances
        events.extend(self._collect_npc_events())

        # Collect location discoveries
        events.extend(self._collect_location_events())

        # Collect custom events
        events.extend(self._collect_custom_events())

        # Sort by day
        events.sort(key=lambda e: (e.day, e.category))

        # Group by day
        days_dict: dict[int, list[TimelineEvent]] = defaultdict(list)
        for event in events:
            days_dict[event.day].append(event)

        days = [
            TimelineDay(
                day=day,
                in_game_date=f"Day {day}",
                events=day_events,
            )
            for day, day_events in sorted(days_dict.items())
        ]

        current_day = max(days_dict.keys()) if days_dict else 1

        return TimelineResponse(
            current_day=current_day,
            total_events=len(events),
            days=days,
        )

    def _collect_session_events(self) -> list[TimelineEvent]:
        """Collect events from session files."""
        events = []
        sessions_dir = self.campaign_dir / "sessions"

        if not sessions_dir.exists():
            return events

        for session_file in sessions_dir.glob("session-*.md"):
            content = session_file.read_text(encoding="utf-8")

            # Extract session number
            match = re.search(r"session-(\d+)\.md", session_file.name)
            if not match:
                continue
            session_num = int(match.group(1))

            # Extract in-game date
            date_match = re.search(r"\*\*In-Game Date\*\*:\s*([Dd]ay\s*\d+)", content)
            if not date_match:
                continue

            in_game_date = parse_in_game_date(date_match.group(1))
            if not in_game_date:
                continue

            # Extract title
            title_match = re.search(r"# Session \d+: (.+)", content)
            title = title_match.group(1) if title_match else f"Session {session_num}"

            events.append(
                TimelineEvent(
                    in_game_date=f"Day {in_game_date.day}",
                    day=in_game_date.day,
                    title=f"Session {session_num}: {title}",
                    category="session",
                    session_number=session_num,
                    entity_path=f"/sessions/{session_num}",
                    entity_type="session",
                )
            )

        return events

    def _collect_npc_events(self) -> list[TimelineEvent]:
        """Collect NPC first appearance events."""
        events = []
        npcs_dir = self.campaign_dir / "npcs"

        if not npcs_dir.exists():
            return events

        for npc_file in npcs_dir.glob("*.md"):
            if npc_file.name == "index.md":
                continue

            content = npc_file.read_text(encoding="utf-8")

            # Extract first appearance date
            date_match = re.search(r"\*\*First Appearance\*\*:\s*([Dd]ay\s*\d+)", content)
            if not date_match:
                continue

            in_game_date = parse_in_game_date(date_match.group(1))
            if not in_game_date:
                continue

            # Extract name
            name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            name = name_match.group(1) if name_match else npc_file.stem

            events.append(
                TimelineEvent(
                    in_game_date=f"Day {in_game_date.day}",
                    day=in_game_date.day,
                    title=f"{name} first appears",
                    category="npc",
                    entity_path=f"/npcs/{npc_file.stem}",
                    entity_type="npc",
                )
            )

        return events

    def _collect_location_events(self) -> list[TimelineEvent]:
        """Collect location discovery events."""
        events = []
        locations_dir = self.campaign_dir / "locations"

        if not locations_dir.exists():
            return events

        for loc_file in locations_dir.glob("*.md"):
            if loc_file.name == "index.md":
                continue

            content = loc_file.read_text(encoding="utf-8")

            # Extract discovered date
            date_match = re.search(r"\*\*Discovered\*\*:\s*([Dd]ay\s*\d+)", content)
            if not date_match:
                continue

            in_game_date = parse_in_game_date(date_match.group(1))
            if not in_game_date:
                continue

            # Extract name
            name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            name = name_match.group(1) if name_match else loc_file.stem

            events.append(
                TimelineEvent(
                    in_game_date=f"Day {in_game_date.day}",
                    day=in_game_date.day,
                    title=f"{name} discovered",
                    category="location",
                    entity_path=f"/locations/{loc_file.stem}",
                    entity_type="location",
                )
            )

        return events

    def _collect_custom_events(self) -> list[TimelineEvent]:
        """Collect custom events from events.md."""
        events = []
        events_file = self.campaign_dir / "events.md"

        if not events_file.exists():
            return events

        content = events_file.read_text(encoding="utf-8")

        # Parse table rows
        # | In-Game Date | Event | Session | Category |
        for line in content.split("\n"):
            if not line.startswith("|"):
                continue
            if "---" in line or "In-Game Date" in line:
                continue

            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) < 4:
                continue

            date_str, event_title, session_str, category = cells[:4]

            in_game_date = parse_in_game_date(date_str)
            if not in_game_date:
                continue

            session_num = None
            if session_str.isdigit():
                session_num = int(session_str)

            events.append(
                TimelineEvent(
                    in_game_date=f"Day {in_game_date.day}",
                    day=in_game_date.day,
                    title=event_title,
                    category=category.lower() if category else "custom",
                    session_number=session_num,
                    entity_type="event",
                )
            )

        return events

    def get_relationships(self) -> RelationshipGraphResponse:
        """Get relationship graph data."""
        npcs_dir = self.campaign_dir / "npcs"

        nodes: dict[str, RelationshipNode] = {}
        edges: list[RelationshipEdge] = []
        seen_edges: set[tuple[str, str, str]] = set()

        if not npcs_dir.exists():
            return RelationshipGraphResponse(nodes=[], edges=[], mermaid="")

        for npc_file in sorted(npcs_dir.glob("*.md")):
            if npc_file.name == "index.md":
                continue

            # Parse relationships from file
            relationships = parse_connections_from_file(npc_file)
            if not relationships:
                continue

            # Get source info
            content = npc_file.read_text(encoding="utf-8")
            name_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            source_name = name_match.group(1) if name_match else npc_file.stem
            source_slug = slugify(source_name)

            # Extract role
            role_match = re.search(r"\*\*Role\*\*:\s*(\w+)", content)
            role = role_match.group(1).lower() if role_match else None

            # Add source node
            if source_slug not in nodes:
                nodes[source_slug] = RelationshipNode(
                    id=source_slug,
                    name=source_name,
                    role=role,
                )

            # Process relationships
            for rel in relationships:
                target_slug = slugify(rel.target_name)

                # Add target node if not exists
                if target_slug not in nodes:
                    nodes[target_slug] = RelationshipNode(
                        id=target_slug,
                        name=rel.target_name,
                    )

                # Avoid duplicate edges
                edge_key = tuple(sorted([source_slug, target_slug])) + (rel.relationship_type,)
                if edge_key in seen_edges:
                    continue
                seen_edges.add(edge_key)

                edges.append(
                    RelationshipEdge(
                        source=source_slug,
                        target=target_slug,
                        type=rel.relationship_type,
                        description=rel.description if rel.description else None,
                    )
                )

        # Generate Mermaid code
        mermaid = self._generate_mermaid(list(nodes.values()), edges)

        return RelationshipGraphResponse(
            nodes=list(nodes.values()),
            edges=edges,
            mermaid=mermaid,
        )

    def _generate_mermaid(
        self, nodes: list[RelationshipNode], edges: list[RelationshipEdge]
    ) -> str:
        """Generate Mermaid flowchart code."""
        if not nodes:
            return ""

        lines = ["flowchart LR"]

        # Add nodes
        for node in nodes:
            # Escape quotes in name
            safe_name = node.name.replace('"', "'")
            lines.append(f'    {node.id}["{safe_name}"]')

        lines.append("")

        # Add edges
        for edge in edges:
            lines.append(f"    {edge.source} -->|{edge.type}| {edge.target}")

        return "\n".join(lines)
