"""Base utilities for extractors."""

import re
from pathlib import Path


def make_safe_filename(name: str) -> str:
    """Convert a name to a safe filename."""
    safe = name.lower()
    safe = re.sub(r'[^\w\s-]', '', safe)
    safe = re.sub(r'[-\s]+', '-', safe)
    return safe.strip('-')[:50]


def ordinal(n: int) -> str:
    """Convert number to ordinal string."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
