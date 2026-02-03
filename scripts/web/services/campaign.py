"""
Campaign service for overview and statistics.
"""

import re
from pathlib import Path
from typing import Optional

from web.models.campaign import CampaignOverview, CampaignStats


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_campaign_dir() -> Path:
    """Get the campaign directory."""
    return get_repo_root() / "campaign"


class CampaignService:
    """Service for campaign-level operations."""

    def __init__(self) -> None:
        """Initialize the campaign service."""
        self.campaign_dir = get_campaign_dir()

    def campaign_exists(self) -> bool:
        """Check if a campaign has been initialized."""
        return (self.campaign_dir / "campaign.md").exists()

    def get_overview(self) -> CampaignOverview:
        """Get campaign overview information."""
        campaign_file = self.campaign_dir / "campaign.md"
        content = campaign_file.read_text(encoding="utf-8") if campaign_file.exists() else ""

        name = self._extract_name(content)
        setting = self._extract_metadata(content, "Setting")
        current_session = self._get_current_session()
        created = self._extract_metadata(content, "Created")

        return CampaignOverview(
            name=name,
            setting=setting,
            current_session=current_session,
            created=created,
            stats=self.get_stats(),
        )

    def get_stats(self) -> CampaignStats:
        """Get campaign entity statistics."""
        return CampaignStats(
            npcs=self._count_entities("npcs"),
            locations=self._count_entities("locations"),
            sessions=self._count_sessions(),
            encounters=self._count_entities("encounters"),
            party_size=self._count_party_members(),
        )

    def _extract_name(self, content: str) -> str:
        """Extract campaign name from markdown heading."""
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled Campaign"

    def _extract_metadata(self, content: str, key: str) -> Optional[str]:
        """Extract metadata value from bold key pattern."""
        pattern = rf"\*\*{key}\*\*:\s*(.+?)(?:\s\s|\n|$)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None

    def _count_entities(self, entity_type: str) -> int:
        """Count markdown files in an entity directory (excluding index.md)."""
        entity_dir = self.campaign_dir / entity_type
        if not entity_dir.exists():
            return 0
        return sum(1 for f in entity_dir.glob("*.md") if f.name != "index.md")

    def _count_sessions(self) -> int:
        """Count session files."""
        sessions_dir = self.campaign_dir / "sessions"
        if not sessions_dir.exists():
            return 0
        return sum(1 for f in sessions_dir.glob("session-*.md"))

    def _get_current_session(self) -> int:
        """Get the highest session number."""
        sessions_dir = self.campaign_dir / "sessions"
        if not sessions_dir.exists():
            return 0

        session_files = list(sessions_dir.glob("session-*.md"))
        if not session_files:
            return 0

        numbers = []
        for f in session_files:
            match = re.search(r"session-(\d+)\.md", f.name)
            if match:
                numbers.append(int(match.group(1)))

        return max(numbers) if numbers else 0

    def _count_party_members(self) -> int:
        """Count party character files."""
        characters_dir = self.campaign_dir / "party" / "characters"
        if not characters_dir.exists():
            return 0
        return sum(1 for f in characters_dir.glob("*.md"))
