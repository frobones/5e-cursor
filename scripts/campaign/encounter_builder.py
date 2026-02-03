#!/usr/bin/env python3
"""
Encounter Builder - Generate balanced encounters using DMG guidelines.

Usage:
    python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium
    python scripts/campaign/encounter_builder.py --auto --difficulty hard
    python scripts/campaign/encounter_builder.py --level 5 --size 4 --difficulty deadly --type undead
    python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium --save "goblin-ambush"
"""

import argparse
import json
import random
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.markdown_writer import bold, heading, horizontal_rule, iso_date, slugify, table
from lib.reference_linker import ReferenceLinker


# DMG XP Thresholds by Character Level (PHB 2024 / DMG 2024)
# Format: level -> (easy, medium, hard, deadly)
XP_THRESHOLDS = {
    1: (25, 50, 75, 100),
    2: (50, 100, 150, 200),
    3: (75, 150, 225, 400),
    4: (125, 250, 375, 500),
    5: (250, 500, 750, 1100),
    6: (300, 600, 900, 1400),
    7: (350, 750, 1100, 1700),
    8: (450, 900, 1400, 2100),
    9: (550, 1100, 1600, 2400),
    10: (600, 1200, 1900, 2800),
    11: (800, 1600, 2400, 3600),
    12: (1000, 2000, 3000, 4500),
    13: (1100, 2200, 3400, 5100),
    14: (1250, 2500, 3800, 5700),
    15: (1400, 2800, 4300, 6400),
    16: (1600, 3200, 4800, 7200),
    17: (2000, 3900, 5900, 8800),
    18: (2100, 4200, 6300, 9500),
    19: (2400, 4900, 7300, 10900),
    20: (2800, 5700, 8500, 12700),
}

# XP values by Challenge Rating
CR_XP = {
    "0": 10,
    "1/8": 25,
    "1/4": 50,
    "1/2": 100,
    "1": 200,
    "2": 450,
    "3": 700,
    "4": 1100,
    "5": 1800,
    "6": 2300,
    "7": 2900,
    "8": 3900,
    "9": 5000,
    "10": 5900,
    "11": 7200,
    "12": 8400,
    "13": 10000,
    "14": 11500,
    "15": 13000,
    "16": 15000,
    "17": 18000,
    "18": 20000,
    "19": 22000,
    "20": 25000,
    "21": 33000,
    "22": 41000,
    "23": 50000,
    "24": 62000,
    "25": 75000,
    "26": 90000,
    "27": 105000,
    "28": 120000,
    "29": 135000,
    "30": 155000,
}

# Encounter multipliers based on number of monsters (DMG)
# Format: (min_monsters, max_monsters) -> multiplier
ENCOUNTER_MULTIPLIERS = [
    (1, 1, 1.0),
    (2, 2, 1.5),
    (3, 6, 2.0),
    (7, 10, 2.5),
    (11, 14, 3.0),
    (15, float("inf"), 4.0),
]

DIFFICULTY_NAMES = ["easy", "medium", "hard", "deadly"]


@dataclass
class Creature:
    """A creature from the reference data."""

    name: str
    cr: str
    xp: int
    path: str
    creature_type: str = ""
    size: str = ""
    alignment: str = ""
    environments: list[str] = field(default_factory=list)


@dataclass
class EncounterEntry:
    """A creature in an encounter with quantity."""

    creature: Creature
    count: int

    @property
    def total_xp(self) -> int:
        return self.creature.xp * self.count


@dataclass
class Encounter:
    """A generated encounter."""

    entries: list[EncounterEntry]
    party_level: int
    party_size: int
    target_difficulty: str
    actual_difficulty: str = ""

    @property
    def total_creatures(self) -> int:
        return sum(e.count for e in self.entries)

    @property
    def base_xp(self) -> int:
        """Total XP before multiplier."""
        return sum(e.total_xp for e in self.entries)

    @property
    def adjusted_xp(self) -> int:
        """XP after applying encounter multiplier."""
        multiplier = get_encounter_multiplier(self.total_creatures)
        return int(self.base_xp * multiplier)

    def calculate_difficulty(self) -> str:
        """Determine actual difficulty based on adjusted XP."""
        thresholds = get_party_thresholds(self.party_level, self.party_size)
        adjusted = self.adjusted_xp

        if adjusted >= thresholds["deadly"]:
            return "deadly"
        elif adjusted >= thresholds["hard"]:
            return "hard"
        elif adjusted >= thresholds["medium"]:
            return "medium"
        else:
            return "easy"


def get_encounter_multiplier(num_creatures: int) -> float:
    """Get the encounter multiplier based on number of creatures."""
    for min_c, max_c, mult in ENCOUNTER_MULTIPLIERS:
        if min_c <= num_creatures <= max_c:
            return mult
    return 4.0


def get_party_thresholds(level: int, size: int) -> dict[str, int]:
    """Calculate XP thresholds for a party.

    Args:
        level: Average party level
        size: Number of party members

    Returns:
        Dict with easy, medium, hard, deadly thresholds
    """
    level = max(1, min(20, level))  # Clamp to valid range
    thresholds = XP_THRESHOLDS[level]

    return {
        "easy": thresholds[0] * size,
        "medium": thresholds[1] * size,
        "hard": thresholds[2] * size,
        "deadly": thresholds[3] * size,
    }


def parse_cr(cr_string: str) -> float:
    """Parse a CR string to a numeric value for sorting.

    Args:
        cr_string: CR like "1/4", "1/2", "1", "10"

    Returns:
        Numeric value
    """
    if "/" in cr_string:
        num, denom = cr_string.split("/")
        return int(num) / int(denom)
    try:
        return float(cr_string)
    except ValueError:
        return 0.0


def cr_to_xp(cr: str) -> int:
    """Convert a CR to XP value."""
    return CR_XP.get(cr, 0)


def load_creatures(books_dir: Path) -> list[Creature]:
    """Load creatures from the reference index.

    Args:
        books_dir: Path to books directory

    Returns:
        List of Creature objects
    """
    index_path = books_dir / "reference-index.json"
    if not index_path.exists():
        return []

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    creatures = []
    seen = set()  # Avoid duplicates

    for entry in data.get("entries", []):
        if entry.get("type") != "creatures":
            continue

        name = entry.get("name", "")
        if name in seen:
            continue
        seen.add(name)

        cr = entry.get("cr", "0")
        xp = cr_to_xp(cr)

        # Handle creature_type which can be a string or a dict with "choose" array
        raw_type = entry.get("creature_type", "")
        if isinstance(raw_type, dict):
            # Use first choice if it's a choose structure
            choices = raw_type.get("choose", [])
            creature_type = choices[0] if choices else ""
        else:
            creature_type = raw_type

        creatures.append(Creature(
            name=name,
            cr=cr,
            xp=xp,
            path=entry.get("path", ""),
            creature_type=creature_type,
            size=entry.get("size", ""),
            alignment=entry.get("alignment", ""),
            environments=entry.get("environments", []),
        ))

    return creatures


def filter_creatures(
    creatures: list[Creature],
    cr_min: Optional[float] = None,
    cr_max: Optional[float] = None,
    creature_type: Optional[str] = None,
    environment: Optional[str] = None,
) -> list[Creature]:
    """Filter creatures by various criteria.

    Args:
        creatures: List of creatures to filter
        cr_min: Minimum CR (inclusive)
        cr_max: Maximum CR (inclusive)
        creature_type: Filter by creature type (undead, beast, etc.)
        environment: Filter by environment

    Returns:
        Filtered list of creatures
    """
    result = []

    for c in creatures:
        cr_val = parse_cr(c.cr)

        if cr_min is not None and cr_val < cr_min:
            continue
        if cr_max is not None and cr_val > cr_max:
            continue
        if creature_type and creature_type.lower() not in c.creature_type.lower():
            continue
        if environment:
            env_lower = environment.lower()
            if not any(env_lower in e.lower() for e in c.environments):
                continue

        result.append(c)

    return result


def get_max_cr_for_level(level: int) -> float:
    """Get recommended maximum CR for a party level.

    A single creature at this CR would be a deadly solo encounter.
    """
    # Rough guideline: party level / 4 for easy, level for deadly solo
    return float(level)


def generate_encounter(
    creatures: list[Creature],
    party_level: int,
    party_size: int,
    difficulty: str,
    max_creatures: int = 8,
) -> Optional[Encounter]:
    """Generate a balanced encounter.

    Args:
        creatures: Available creatures to choose from
        party_level: Average party level
        party_size: Number of party members
        difficulty: Target difficulty (easy, medium, hard, deadly)
        max_creatures: Maximum number of creatures in encounter

    Returns:
        Generated Encounter or None if no valid encounter possible
    """
    if not creatures:
        return None

    thresholds = get_party_thresholds(party_level, party_size)
    difficulty_index = DIFFICULTY_NAMES.index(difficulty)

    target_xp = thresholds[difficulty]

    # Get valid CR range for this party
    max_cr = get_max_cr_for_level(party_level)

    # Filter to creatures within CR range
    valid_creatures = [c for c in creatures if parse_cr(c.cr) <= max_cr and c.xp > 0]

    if not valid_creatures:
        return None

    # Sort by XP for easier selection
    valid_creatures.sort(key=lambda c: c.xp, reverse=True)

    # Try different approaches to build an encounter
    best_encounter = None
    best_diff = float("inf")

    for attempt in range(50):  # Try multiple random combinations
        entries = []
        current_xp = 0

        # Shuffle for variety
        shuffled = valid_creatures.copy()
        random.shuffle(shuffled)

        for creature in shuffled:
            if sum(e.count for e in entries) >= max_creatures:
                break

            # How many of this creature can we add?
            count = 0
            test_entries = entries.copy()

            while count < 4:  # Max 4 of same creature type
                count += 1
                test_entry = EncounterEntry(creature, count)

                # Calculate what the XP would be
                test_entries_with_new = [e for e in entries if e.creature != creature]
                test_entries_with_new.append(test_entry)

                total_count = sum(e.count for e in test_entries_with_new)
                if total_count > max_creatures:
                    break

                base_xp = sum(e.total_xp for e in test_entries_with_new)
                multiplier = get_encounter_multiplier(total_count)
                adjusted_xp = base_xp * multiplier

                if adjusted_xp <= target_xp * 1.2:  # Allow 20% over
                    entries = test_entries_with_new
                    current_xp = adjusted_xp
                else:
                    break

        if entries:
            # Calculate how close we are to target
            base_xp = sum(e.total_xp for e in entries)
            total_count = sum(e.count for e in entries)
            multiplier = get_encounter_multiplier(total_count)
            adjusted_xp = base_xp * multiplier

            diff = abs(adjusted_xp - target_xp)

            # Prefer encounters that are at least 80% of target
            if adjusted_xp >= target_xp * 0.8 and diff < best_diff:
                best_diff = diff
                best_encounter = Encounter(
                    entries=entries,
                    party_level=party_level,
                    party_size=party_size,
                    target_difficulty=difficulty,
                )

    if best_encounter:
        best_encounter.actual_difficulty = best_encounter.calculate_difficulty()

    return best_encounter


def generate_encounter_loot(encounter: Encounter) -> str:
    """Generate loot for an encounter based on creatures.

    Args:
        encounter: The encounter to generate loot for

    Returns:
        Markdown-formatted loot section
    """
    try:
        from campaign.loot_generator import LootGenerator, TreasureFormatter

        # Find the highest CR among creatures
        max_cr = 0.0
        for entry in encounter.entries:
            cr = parse_cr(entry.creature.cr)
            if cr > max_cr:
                max_cr = cr

        if max_cr == 0 and encounter.entries:
            max_cr = 0.25  # Default to CR 1/4 if all CRs invalid

        # Generate individual loot for each creature
        reference_index = Path("books/reference/reference-index.json")
        generator = LootGenerator(
            reference_index_path=reference_index if reference_index.exists() else None
        )
        treasure = generator.generate_individual(max_cr, encounter.total_creatures)

        # Format as markdown
        formatter = TreasureFormatter(generator.linker)
        loot_text = formatter.format_console(
            treasure, f"Treasure (Individual, {encounter.total_creatures} creatures)"
        )

        return loot_text
    except Exception as e:
        # If loot generation fails, return error message
        return f"## Treasure\n\n*Loot generation failed: {e}*\n"


def format_encounter_markdown(
    encounter: Encounter,
    linker: Optional[ReferenceLinker],
    from_path: str,
    name: Optional[str] = None,
) -> str:
    """Format an encounter as markdown.

    Matches the Web UI format for consistency.

    Args:
        encounter: The encounter to format
        linker: Reference linker for creature links (unused, kept for API compat)
        from_path: Path of output file for relative links (unused, kept for API compat)
        name: Optional encounter name

    Returns:
        Markdown string
    """
    lines = []

    # Title
    title = name or f"Encounter (Party Level {encounter.party_level})"
    lines.append(heading(title))
    lines.append("")

    # Header metadata (matches Web UI format)
    lines.append(f"{bold('Difficulty')}: {encounter.actual_difficulty.title()}  ")
    lines.append(f"{bold('Party Level')}: {encounter.party_level}  ")
    lines.append(f"{bold('Party Size')}: {encounter.party_size}  ")
    lines.append(f"{bold('Total Creatures')}: {encounter.total_creatures}  ")
    lines.append(f"{bold('Base XP')}: {encounter.base_xp:,}  ")
    lines.append(f"{bold('Adjusted XP')}: {encounter.adjusted_xp:,}  ")
    lines.append(f"{bold('Created')}: {iso_date()}")
    lines.append("")

    # Creatures table (no markdown links, matches Web UI)
    lines.append(heading("Creatures", 2))
    lines.append("")

    headers = ["Creature", "CR", "XP", "Count", "Total XP"]
    rows = []

    for entry in sorted(encounter.entries, key=lambda e: parse_cr(e.creature.cr), reverse=True):
        rows.append([
            entry.creature.name,
            entry.creature.cr,
            f"{entry.creature.xp:,}",
            str(entry.count),
            f"{entry.total_xp:,}",
        ])

    lines.append(table(headers, rows))
    lines.append("")

    # Treasure section (matches Web UI)
    loot_markdown = generate_encounter_loot(encounter)
    lines.append(loot_markdown)
    lines.append("")

    return "\n".join(lines)


def read_party_info(campaign_dir: Path) -> tuple[int, int]:
    """Read party level and size from campaign data.

    Args:
        campaign_dir: Path to campaign directory

    Returns:
        Tuple of (average_level, party_size)
    """
    characters_dir = campaign_dir / "party" / "characters"
    if not characters_dir.exists():
        return 1, 4  # Default

    levels = []
    for char_file in characters_dir.glob("*.md"):
        content = char_file.read_text(encoding="utf-8")

        # Look for class line with level
        # Format: **Class**: Rogue 1 or **Class**: Fighter 3 / Wizard 2
        for line in content.split("\n"):
            if "**Class**:" in line:
                # Extract all numbers after class names
                numbers = re.findall(r"(\d+)", line.split("**Class**:")[1])
                if numbers:
                    # Sum multiclass levels
                    total = sum(int(n) for n in numbers)
                    levels.append(total)
                break

    if not levels:
        return 1, 4

    avg_level = sum(levels) // len(levels)
    return avg_level, len(levels)


def save_encounter(
    encounter: Encounter,
    name: str,
    campaign_dir: Path,
    linker: Optional[ReferenceLinker],
) -> Path:
    """Save an encounter to the encounters directory.

    Args:
        encounter: Encounter to save
        name: Name for the encounter
        campaign_dir: Path to campaign directory
        linker: Reference linker for links

    Returns:
        Path to saved file
    """
    encounters_dir = campaign_dir / "encounters"
    encounters_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{slugify(name)}.md"
    output_path = encounters_dir / filename
    from_path = f"campaign/encounters/{filename}"

    content = format_encounter_markdown(encounter, linker, from_path, name)
    output_path.write_text(content, encoding="utf-8")

    # Update index
    update_encounter_index(campaign_dir, name, encounter, filename)

    return output_path


def update_encounter_index(
    campaign_dir: Path,
    name: str,
    encounter: Encounter,
    filename: str,
) -> None:
    """Update the encounters index with a new encounter."""
    index_path = campaign_dir / "encounters" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")

    # Check if already listed
    if filename in content:
        return

    # Build creature list
    creature_names = ", ".join(f"{e.count}x {e.creature.name}" for e in encounter.entries)

    # Find the table and add row
    lines = content.split("\n")
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if line.startswith("| ----"):
            # Add after header separator
            new_row = f"| [{name}]({filename}) | {encounter.actual_difficulty.title()} | {encounter.party_level} | {creature_names} |"
            new_lines.append(new_row)

    # Remove placeholder if present
    final_lines = [l for l in new_lines if "*No encounters saved yet" not in l]

    index_path.write_text("\n".join(final_lines), encoding="utf-8")


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
        description="Generate balanced D&D 5e encounters using DMG guidelines.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate medium encounter for 4 level-3 characters
    python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium

    # Auto-detect party from campaign data
    python scripts/campaign/encounter_builder.py --auto --difficulty hard

    # Filter by creature type
    python scripts/campaign/encounter_builder.py --level 5 --size 4 --difficulty deadly --type undead

    # Save encounter to campaign
    python scripts/campaign/encounter_builder.py --level 3 --size 4 --difficulty medium --save "Goblin Ambush"
        """,
    )
    parser.add_argument(
        "--level", "-l",
        type=int,
        help="Average party level (1-20)",
    )
    parser.add_argument(
        "--size", "-s",
        type=int,
        help="Number of party members",
    )
    parser.add_argument(
        "--auto", "-a",
        action="store_true",
        help="Auto-detect party level and size from campaign data",
    )
    parser.add_argument(
        "--difficulty", "-d",
        choices=DIFFICULTY_NAMES,
        default="medium",
        help="Target difficulty (default: medium)",
    )
    parser.add_argument(
        "--type", "-t",
        help="Filter by creature type (undead, beast, dragon, etc.)",
    )
    parser.add_argument(
        "--environment", "-e",
        help="Filter by environment (forest, underdark, etc.)",
    )
    parser.add_argument(
        "--max-creatures", "-m",
        type=int,
        default=8,
        help="Maximum creatures in encounter (default: 8)",
    )
    parser.add_argument(
        "--save",
        help="Save encounter with given name to campaign/encounters/",
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"
    books_dir = repo_root / "books"

    # Determine party level and size
    if args.auto:
        if not campaign_dir.exists():
            print("Error: Campaign directory not found. Use --level and --size instead.")
            sys.exit(1)
        party_level, party_size = read_party_info(campaign_dir)
        print(f"Auto-detected party: {party_size} characters, average level {party_level}")
    elif args.level and args.size:
        party_level = args.level
        party_size = args.size
    else:
        print("Error: Specify --level and --size, or use --auto")
        sys.exit(1)

    # Validate level
    if party_level < 1 or party_level > 20:
        print("Error: Level must be between 1 and 20")
        sys.exit(1)

    # Load creatures
    print("Loading creatures...")
    creatures = load_creatures(books_dir)
    if not creatures:
        print("Error: No creatures found. Run 'make' to extract reference data.")
        sys.exit(1)

    print(f"Loaded {len(creatures)} creatures")

    # Filter creatures
    filtered = filter_creatures(
        creatures,
        creature_type=args.type,
        environment=args.environment,
    )

    if args.type or args.environment:
        print(f"Filtered to {len(filtered)} creatures")

    if not filtered:
        print("Error: No creatures match the filters")
        sys.exit(1)

    # Generate encounter
    print(f"Generating {args.difficulty} encounter for {party_size} level-{party_level} characters...")
    encounter = generate_encounter(
        filtered,
        party_level,
        party_size,
        args.difficulty,
        args.max_creatures,
    )

    if not encounter:
        print("Error: Could not generate a valid encounter with given constraints")
        sys.exit(1)

    # Initialize linker for output
    try:
        linker = ReferenceLinker(books_dir)
    except FileNotFoundError:
        linker = None

    # Output or save
    if args.save:
        if not campaign_dir.exists():
            print("Error: Campaign directory not found. Run init_campaign.py first.")
            sys.exit(1)

        output_path = save_encounter(encounter, args.save, campaign_dir, linker)
        print(f"\nEncounter saved to: {output_path}")
    else:
        # Print to console
        from_path = "campaign/encounters/temp.md"
        output = format_encounter_markdown(encounter, linker, from_path)
        print("\n" + output)


if __name__ == "__main__":
    main()
