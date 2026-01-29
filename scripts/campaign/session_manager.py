#!/usr/bin/env python3
"""
Session Manager - Track session history and summaries.

Usage:
    python scripts/campaign/session_manager.py new "The Beginning"
    python scripts/campaign/session_manager.py new --title "Into the Dungeon"
    python scripts/campaign/session_manager.py list
    python scripts/campaign/session_manager.py show 3
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import bold, heading, horizontal_rule, iso_date, session_filename


def get_next_session_number(sessions_dir: Path) -> int:
    """Find the next available session number.

    Args:
        sessions_dir: Path to sessions directory

    Returns:
        Next session number
    """
    if not sessions_dir.exists():
        return 1

    max_num = 0
    for session_file in sessions_dir.glob("session-*.md"):
        # Extract number from filename
        match = re.search(r"session-(\d+)\.md", session_file.name)
        if match:
            num = int(match.group(1))
            max_num = max(max_num, num)

    return max_num + 1


def create_session(
    sessions_dir: Path,
    title: str,
    session_number: int,
) -> Path:
    """Create a new session file.

    Args:
        sessions_dir: Path to sessions directory
        title: Session title
        session_number: Session number

    Returns:
        Path to created session file
    """
    sessions_dir.mkdir(parents=True, exist_ok=True)

    filename = session_filename(session_number)
    session_path = sessions_dir / filename

    today = iso_date()

    content = f"""{heading(f"Session {session_number}: {title}")}

{bold("Date")}: {today}  
{bold("Session Number")}: {session_number}

{horizontal_rule()}

## Summary

*Write your session summary here...*

## Key Events

- Event 1
- Event 2
- Event 3

## NPCs Encountered

*List NPCs met or mentioned this session*

## Locations Visited

*List locations visited this session*

## Loot & Rewards

*List any treasure, items, or rewards gained*

## Notes for Next Session

*Hooks, cliffhangers, or things to remember*

{horizontal_rule()}

*Session created on {today}*
"""

    session_path.write_text(content, encoding="utf-8")
    return session_path


def update_session_index(campaign_dir: Path, session_number: int, title: str, filename: str) -> None:
    """Update the session index with a new session.

    Args:
        campaign_dir: Campaign directory
        session_number: Session number
        title: Session title
        filename: Session filename
    """
    index_path = campaign_dir / "sessions" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    today = iso_date()

    # Find the table and add row
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if line.startswith("| ----"):
            # Add after header separator
            new_row = f"| {session_number} | {today} | [{title}]({filename}) |"
            new_lines.append(new_row)

    # Remove placeholder if present
    final_lines = [l for l in new_lines if "*No sessions recorded yet" not in l]

    index_path.write_text("\n".join(final_lines), encoding="utf-8")


def list_sessions(sessions_dir: Path) -> list[dict]:
    """List all sessions.

    Args:
        sessions_dir: Path to sessions directory

    Returns:
        List of session info dicts
    """
    if not sessions_dir.exists():
        return []

    sessions = []

    for session_file in sorted(sessions_dir.glob("session-*.md")):
        content = session_file.read_text(encoding="utf-8")

        # Extract session number
        match = re.search(r"session-(\d+)\.md", session_file.name)
        if not match:
            continue

        session_num = int(match.group(1))

        # Extract title from heading
        title_match = re.search(r"# Session \d+: (.+)", content)
        title = title_match.group(1) if title_match else "Untitled"

        # Extract date
        date_match = re.search(r"\*\*Date\*\*: (\d{4}-\d{2}-\d{2})", content)
        session_date = date_match.group(1) if date_match else "Unknown"

        sessions.append({
            "number": session_num,
            "title": title,
            "date": session_date,
            "filename": session_file.name,
            "path": session_file,
        })

    return sorted(sessions, key=lambda s: s["number"])


def show_session(sessions_dir: Path, session_number: int) -> str:
    """Get content of a specific session.

    Args:
        sessions_dir: Sessions directory
        session_number: Session number to show

    Returns:
        Session content or error message
    """
    filename = session_filename(session_number)
    session_path = sessions_dir / filename

    if not session_path.exists():
        return f"Session {session_number} not found."

    return session_path.read_text(encoding="utf-8")


def find_repo_root() -> Path:
    """Find the repository root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "books").exists() or (current / "scripts").exists():
            return current
        current = current.parent
    return Path.cwd()


def main():
    parser = argparse.ArgumentParser(
        description="Manage campaign session history.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/session_manager.py new "The Beginning"
    python scripts/campaign/session_manager.py new --title "Into the Dungeon"
    python scripts/campaign/session_manager.py list
    python scripts/campaign/session_manager.py show 3
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # new command
    new_parser = subparsers.add_parser("new", help="Create a new session")
    new_parser.add_argument(
        "title",
        nargs="?",
        default=None,
        help="Session title",
    )
    new_parser.add_argument(
        "--title", "-t",
        dest="title_opt",
        help="Session title (alternative to positional)",
    )
    new_parser.add_argument(
        "--number", "-n",
        type=int,
        help="Override session number",
    )

    # list command
    subparsers.add_parser("list", help="List all sessions")

    # show command
    show_parser = subparsers.add_parser("show", help="Show a session")
    show_parser.add_argument(
        "number",
        type=int,
        help="Session number to show",
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"
    sessions_dir = campaign_dir / "sessions"

    if not campaign_dir.exists():
        print("Error: Campaign directory not found. Run init_campaign.py first.")
        sys.exit(1)

    if args.command == "new":
        # Get title from either positional or option
        title = args.title or args.title_opt or "Untitled Session"

        # Get session number
        if args.number:
            session_num = args.number
        else:
            session_num = get_next_session_number(sessions_dir)

        # Create session
        session_path = create_session(sessions_dir, title, session_num)
        update_session_index(campaign_dir, session_num, title, session_path.name)

        print(f"Created session {session_num}: {title}")
        print(f"File: {session_path}")

    elif args.command == "list":
        sessions = list_sessions(sessions_dir)

        if not sessions:
            print("No sessions recorded yet.")
            return

        print(f"{'#':<4} {'Date':<12} {'Title':<40}")
        print("-" * 60)

        for s in sessions:
            print(f"{s['number']:<4} {s['date']:<12} {s['title']:<40}")

        print(f"\nTotal: {len(sessions)} sessions")

    elif args.command == "show":
        content = show_session(sessions_dir, args.number)
        print(content)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
