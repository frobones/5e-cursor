#!/usr/bin/env python3
"""
Import a character from D&D Beyond.

Usage:
    python scripts/campaign/import_character.py https://www.dndbeyond.com/characters/157884334
    python scripts/campaign/import_character.py 157884334
"""

import argparse
import sys
from datetime import date
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.dndbeyond_client import Character, fetch_character
from lib.markdown_writer import (
    bold,
    heading,
    horizontal_rule,
    iso_date,
    link,
    slugify,
    table,
)
from lib.reference_linker import ReferenceLinker


SKILL_STATS = {
    "Acrobatics": "dexterity",
    "Animal Handling": "wisdom",
    "Arcana": "intelligence",
    "Athletics": "strength",
    "Deception": "charisma",
    "History": "intelligence",
    "Insight": "wisdom",
    "Intimidation": "charisma",
    "Investigation": "intelligence",
    "Medicine": "wisdom",
    "Nature": "intelligence",
    "Perception": "wisdom",
    "Performance": "charisma",
    "Persuasion": "charisma",
    "Religion": "intelligence",
    "Sleight Of Hand": "dexterity",
    "Stealth": "dexterity",
    "Survival": "wisdom",
}

# Short stat names for display
STAT_ABBREVS = {
    "strength": "STR",
    "dexterity": "DEX",
    "constitution": "CON",
    "intelligence": "INT",
    "wisdom": "WIS",
    "charisma": "CHA",
}


def calculate_skill_modifier(char: Character, skill: str) -> int:
    """Calculate skill modifier including proficiency and expertise."""
    stat = SKILL_STATS.get(skill, "intelligence")
    mod = char.stats.modifier(stat)

    # Normalize skill name for comparison
    skill_lower = skill.lower().replace(" ", "").replace("-", "")

    for prof in char.skill_proficiencies:
        if prof.lower().replace(" ", "").replace("-", "") == skill_lower:
            mod += char.proficiency_bonus
            break

    for exp in char.skill_expertise:
        if exp.lower().replace(" ", "").replace("-", "") == skill_lower:
            mod += char.proficiency_bonus  # Additional bonus for expertise
            break

    return mod


def format_modifier(mod: int) -> str:
    """Format a modifier with sign."""
    return f"+{mod}" if mod >= 0 else str(mod)


def generate_character_markdown(char: Character, linker: ReferenceLinker, from_path: str) -> str:
    """Generate markdown content for a character sheet.

    Args:
        char: Parsed character data
        linker: Reference linker for creating links
        from_path: Path of the output file (for relative link calculation)

    Returns:
        Markdown content string
    """
    lines = []

    # Title
    lines.append(heading(char.name))
    lines.append("")

    # Basic info
    lines.append(f"{bold('Player')}: {char.player}  ")
    lines.append(f"{bold('Species')}: {linker.link_or_text(char.species, from_path, 'species')}  ")
    lines.append(f"{bold('Class')}: {char.class_string()}  ")
    if char.background:
        lines.append(f"{bold('Background')}: {char.background}  ")
    if char.alignment:
        lines.append(f"{bold('Alignment')}: {char.alignment}")
    lines.append("")

    # Ability Scores
    lines.append(heading("Ability Scores", 2))
    lines.append("")

    stat_abbrevs = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    stat_names = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    stat_values = []
    for stat_name in stat_names:
        total = char.stats.total(stat_name)
        mod = char.stats.modifier_str(stat_name)
        stat_values.append(f"{total} ({mod})")

    lines.append(table(stat_abbrevs, [stat_values]))
    lines.append("")

    # Combat
    lines.append(heading("Combat", 2))
    lines.append("")
    lines.append(f"- {bold('Armor Class')}: {char.armor_class}")
    lines.append(f"- {bold('Hit Points')}: {char.current_hp} / {char.max_hp}")
    lines.append(f"- {bold('Speed')}: {char.speed} ft.")
    lines.append(f"- {bold('Proficiency Bonus')}: +{char.proficiency_bonus}")
    lines.append("")

    # Saving Throws
    lines.append(heading("Saving Throws", 2))
    lines.append("")
    save_parts = []
    for abbrev, stat_name in zip(stat_abbrevs, stat_names):
        mod = char.stats.modifier(stat_name)
        if abbrev in char.saving_throws:
            mod += char.proficiency_bonus
            save_parts.append(f"{bold(abbrev)} {format_modifier(mod)}")
        else:
            save_parts.append(f"{abbrev} {format_modifier(mod)}")
    lines.append(", ".join(save_parts))
    lines.append("")

    # Skills
    lines.append(heading("Skills", 2))
    lines.append("")

    skill_lines = []
    for skill in sorted(SKILL_STATS.keys()):
        mod = calculate_skill_modifier(char, skill)
        stat_abbrev = STAT_ABBREVS.get(SKILL_STATS[skill], "INT")

        skill_lower = skill.lower().replace(" ", "").replace("-", "")
        is_proficient = any(
            p.lower().replace(" ", "").replace("-", "") == skill_lower
            for p in char.skill_proficiencies
        )
        is_expert = any(
            e.lower().replace(" ", "").replace("-", "") == skill_lower
            for e in char.skill_expertise
        )

        if is_expert:
            skill_lines.append(f"- {bold(skill)} ({stat_abbrev}) {format_modifier(mod)} *(Expertise)*")
        elif is_proficient:
            skill_lines.append(f"- {bold(skill)} ({stat_abbrev}) {format_modifier(mod)}")
        else:
            skill_lines.append(f"- {skill} ({stat_abbrev}) {format_modifier(mod)}")

    lines.extend(skill_lines)
    lines.append("")

    # Languages
    if char.languages:
        lines.append(heading("Languages", 2))
        lines.append("")
        lines.append(", ".join(char.languages))
        lines.append("")

    # Tool Proficiencies
    if char.tool_proficiencies:
        lines.append(heading("Tool Proficiencies", 2))
        lines.append("")
        tool_links = [linker.link_or_text(t, from_path, "equipment") for t in char.tool_proficiencies]
        lines.append(", ".join(tool_links))
        lines.append("")

    # Features & Traits
    lines.append(heading("Features & Traits", 2))
    lines.append("")

    # Species traits
    if char.species_traits:
        lines.append(heading(f"Species: {char.species}", 3))
        lines.append("")
        for trait in char.species_traits:
            trait_name = trait.get("name", "")
            trait_link = linker.link(trait_name, from_path)
            if trait_link:
                lines.append(f"- {trait_link}")
            else:
                lines.append(f"- {bold(trait_name)}")
        lines.append("")

    # Class features by class
    for cls in char.classes:
        lines.append(heading(f"Class: {cls.name} {cls.level}", 3))
        lines.append("")
        for feature in cls.features:
            feat_name = feature.get("name", "")
            feat_link = linker.link(feat_name, from_path, "class-features")
            if feat_link:
                lines.append(f"- {feat_link}")
            else:
                lines.append(f"- {bold(feat_name)}")
        lines.append("")

    # Feats
    if char.feats:
        lines.append(heading("Feats", 3))
        lines.append("")
        for feat in char.feats:
            feat_name = feat.get("name", "")
            feat_link = linker.link(feat_name, from_path, "feats")
            if feat_link:
                lines.append(f"- {feat_link}")
            else:
                lines.append(f"- {bold(feat_name)}")
        lines.append("")

    # Equipment
    lines.append(heading("Equipment", 2))
    lines.append("")

    # Weapons
    weapons = [i for i in char.inventory if i.damage]
    if weapons:
        lines.append(heading("Weapons", 3))
        lines.append("")
        weapon_headers = ["Weapon", "Attack", "Damage", "Properties"]
        weapon_rows = []
        for w in weapons:
            attack_mod = char.stats.modifier("dexterity") + char.proficiency_bonus  # Simplified
            damage_mod = char.stats.modifier("dexterity")
            weapon_link = linker.link_or_text(w.name, from_path, "equipment")
            props = ", ".join(w.properties) if w.properties else "-"
            weapon_rows.append([
                weapon_link,
                format_modifier(attack_mod),
                f"{w.damage}{format_modifier(damage_mod)} {w.damage_type or ''}".strip(),
                props,
            ])
        lines.append(table(weapon_headers, weapon_rows))
        lines.append("")

    # Armor
    armor = [i for i in char.inventory if i.armor_class and i.equipped]
    if armor:
        lines.append(heading("Armor", 3))
        lines.append("")
        for a in armor:
            armor_link = linker.link_or_text(a.name, from_path, "equipment")
            lines.append(f"- {armor_link} (AC {a.armor_class})")
        lines.append("")

    # Other gear
    gear = [i for i in char.inventory if not i.damage and not i.armor_class]
    if gear:
        lines.append(heading("Gear", 3))
        lines.append("")
        for g in gear:
            gear_link = linker.link_or_text(g.name, from_path, "equipment")
            qty = f" ({g.quantity})" if g.quantity > 1 else ""
            lines.append(f"- {gear_link}{qty}")
        lines.append("")

    # Currency
    lines.append(heading("Currency", 3))
    lines.append("")
    currency_parts = []
    for coin in ["cp", "sp", "gp", "ep", "pp"]:
        amount = char.currency.get(coin, 0)
        currency_parts.append(f"{amount} {coin.upper()}")
    lines.append(", ".join(currency_parts))
    lines.append("")

    # Personality
    if any([char.personality_traits, char.ideals, char.bonds, char.flaws]):
        lines.append(heading("Personality", 2))
        lines.append("")
        if char.personality_traits:
            lines.append(f"{bold('Traits')}: {char.personality_traits}")
            lines.append("")
        if char.ideals:
            lines.append(f"{bold('Ideals')}: {char.ideals}")
            lines.append("")
        if char.bonds:
            lines.append(f"{bold('Bonds')}: {char.bonds}")
            lines.append("")
        if char.flaws:
            lines.append(f"{bold('Flaws')}: {char.flaws}")
            lines.append("")

    # Appearance
    if char.appearance:
        lines.append(heading("Appearance", 2))
        lines.append("")
        lines.append(char.appearance)
        lines.append("")

    # Notes
    if any([char.allies, char.enemies, char.organizations, char.backstory]):
        lines.append(heading("Notes", 2))
        lines.append("")
        if char.allies:
            lines.append(heading("Allies", 3))
            lines.append("")
            lines.append(char.allies)
            lines.append("")
        if char.organizations:
            lines.append(heading("Organizations", 3))
            lines.append("")
            lines.append(char.organizations)
            lines.append("")
        if char.enemies:
            lines.append(heading("Enemies", 3))
            lines.append("")
            lines.append(char.enemies)
            lines.append("")
        if char.backstory:
            lines.append(heading("Backstory", 3))
            lines.append("")
            lines.append(char.backstory)
            lines.append("")

    # Footer
    lines.append(horizontal_rule())
    lines.append("")
    lines.append(f"*Imported from D&D Beyond on {iso_date()}*  ")
    lines.append(f"*Source: {char.source_url}*")

    return "\n".join(lines)


def update_party_index(campaign_dir: Path, char: Character, char_filename: str) -> None:
    """Update the party index with the new character.

    Args:
        campaign_dir: Path to campaign directory
        char: Character data
        char_filename: Filename of the character markdown
    """
    index_path = campaign_dir / "party" / "index.md"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")

    # Check if character already listed
    char_link = f"characters/{char_filename}"
    if char_link in content:
        print(f"Character already in party index")
        return

    # Find the Members section and add character
    lines = content.split("\n")
    new_lines = []
    in_members = False

    for line in lines:
        new_lines.append(line)
        if "## Members" in line:
            in_members = True
        elif in_members and line.startswith("*No characters"):
            # Replace the placeholder
            new_lines[-1] = f"- [{char.name}]({char_link}) - {char.species} {char.class_string()}"
            in_members = False
        elif in_members and line.startswith("-"):
            # There are already characters, we'll add after them
            pass
        elif in_members and line.startswith("##"):
            # End of members section, insert before this
            new_lines.insert(-1, f"- [{char.name}]({char_link}) - {char.species} {char.class_string()}")
            in_members = False

    # If we're still in members at end, append
    if in_members:
        new_lines.append(f"- [{char.name}]({char_link}) - {char.species} {char.class_string()}")

    index_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"Updated party index: {index_path}")


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
        description="Import a character from D&D Beyond.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/import_character.py https://www.dndbeyond.com/characters/157884334
    python scripts/campaign/import_character.py 157884334

Note: The character must have Public privacy settings in D&D Beyond.
        """,
    )
    parser.add_argument(
        "url",
        help="D&D Beyond character URL or ID",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: campaign/party/characters/<name>.md)",
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = find_repo_root()
    campaign_dir = repo_root / "campaign"

    # Check if campaign exists
    if not campaign_dir.exists():
        print(f"Campaign directory not found. Run 'python scripts/campaign/init_campaign.py' first.")
        sys.exit(1)

    # Check if reference data exists
    books_dir = repo_root / "books"
    if not books_dir.exists():
        print(f"Reference data not found. Run 'make' to extract reference data first.")
        sys.exit(1)

    # Fetch character
    print(f"Fetching character from D&D Beyond...")
    try:
        char = fetch_character(args.url)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to fetch character: {e}")
        sys.exit(1)

    print(f"Found: {char.name} ({char.species} {char.class_string()})")

    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        filename = f"{slugify(char.name)}.md"
        output_path = campaign_dir / "party" / "characters" / filename

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Initialize reference linker
    try:
        linker = ReferenceLinker(books_dir)
    except FileNotFoundError as e:
        print(f"Warning: {e}")
        print("Character will be generated without reference links.")
        linker = None

    # Generate markdown
    from_path = str(output_path.relative_to(repo_root))

    if linker:
        content = generate_character_markdown(char, linker, from_path)
    else:
        # Fallback without linking - create a dummy linker that doesn't link
        class DummyLinker:
            def link_or_text(self, name, *args, **kwargs):
                return name

            def link(self, name, *args, **kwargs):
                return None

        content = generate_character_markdown(char, DummyLinker(), from_path)

    # Write file
    output_path.write_text(content, encoding="utf-8")
    print(f"Created: {output_path}")

    # Update party index
    update_party_index(campaign_dir, char, output_path.name)

    print(f"\nCharacter '{char.name}' imported successfully!")


if __name__ == "__main__":
    main()
