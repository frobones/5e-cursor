"""
Campaign Calendar - In-game date utilities for campaign timeline.

Provides simple day-based date tracking for D&D campaigns.

Usage:
    from lib.campaign_calendar import InGameDate, parse_in_game_date, format_in_game_date

    # Parse a date string
    date = parse_in_game_date("Day 15")
    print(date.day)  # 15

    # Format a date
    date = InGameDate(day=15)
    print(format_in_game_date(date))  # "Day 15"

Date Format:
    Dates are tracked as simple day counts from campaign start.
    Day 1 is the first day of the campaign.

    Valid formats:
    - "Day 15"
    - "day 15"
    - "Day15"
    - "DAY 15"
"""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class InGameDate:
    """Represents an in-game date as days since campaign start.

    Attributes:
        day: The day number (1-indexed, Day 1 = first day of campaign)
    """

    day: int

    def __post_init__(self) -> None:
        """Validate that day is positive."""
        if self.day < 1:
            raise ValueError(f"Day must be positive, got {self.day}")

    def __lt__(self, other: "InGameDate") -> bool:
        """Support sorting by day."""
        return self.day < other.day

    def __le__(self, other: "InGameDate") -> bool:
        """Support sorting by day."""
        return self.day <= other.day

    def __gt__(self, other: "InGameDate") -> bool:
        """Support sorting by day."""
        return self.day > other.day

    def __ge__(self, other: "InGameDate") -> bool:
        """Support sorting by day."""
        return self.day >= other.day


def parse_in_game_date(date_str: str) -> Optional[InGameDate]:
    """Parse a date string into an InGameDate.

    Accepts formats like:
    - "Day 15"
    - "day 15"
    - "Day15"
    - "DAY 15"

    Args:
        date_str: The date string to parse

    Returns:
        InGameDate if parsing succeeds, None if format is invalid

    Examples:
        >>> parse_in_game_date("Day 15")
        InGameDate(day=15)
        >>> parse_in_game_date("day 1")
        InGameDate(day=1)
        >>> parse_in_game_date("invalid")
        None
    """
    if not date_str:
        return None

    # Match "Day N" with optional whitespace, case-insensitive
    match = re.match(r"[Dd][Aa][Yy]\s*(\d+)", date_str.strip())
    if match:
        day = int(match.group(1))
        if day >= 1:
            return InGameDate(day=day)
    return None


def format_in_game_date(date: InGameDate) -> str:
    """Format an InGameDate as a string.

    Args:
        date: The InGameDate to format

    Returns:
        Formatted string like "Day 15"

    Examples:
        >>> format_in_game_date(InGameDate(day=15))
        'Day 15'
        >>> format_in_game_date(InGameDate(day=1))
        'Day 1'
    """
    return f"Day {date.day}"


def extract_in_game_date_from_content(content: str) -> Optional[InGameDate]:
    """Extract an in-game date from markdown content.

    Looks for patterns like:
    - **In-Game Date**: Day 15
    - **First Appearance**: Day 12
    - **Discovered**: Day 10

    Args:
        content: Markdown content to search

    Returns:
        InGameDate if found, None otherwise
    """
    # Look for common patterns
    patterns = [
        r"\*\*In-Game Date\*\*:\s*([Dd]ay\s*\d+)",
        r"\*\*First Appearance\*\*:\s*([Dd]ay\s*\d+)",
        r"\*\*Discovered\*\*:\s*([Dd]ay\s*\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content)
        if match:
            return parse_in_game_date(match.group(1))

    return None
