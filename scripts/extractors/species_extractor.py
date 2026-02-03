"""Species/Race extractor for 5etools data."""

import json
import sys
from pathlib import Path
from typing import Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


# Sources to include
ALLOWED_SOURCES = {'XPHB', 'XDMG', 'XMM', 'AAG', 'BAM', 'EFA'}

# Size codes
SIZE_MAP = {
    'T': 'Tiny',
    'S': 'Small',
    'M': 'Medium',
    'L': 'Large',
    'H': 'Huge',
    'G': 'Gargantuan',
}


class SpeciesExtractor:
    """Extracts species/races to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the species extractor.

        Args:
            output_dir: Directory to output species files
            sources: List of source codes to filter by (defaults to ALLOWED_SOURCES)
        """
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []
        self.trait_entries = []  # Species traits for searchability

    def extract_file(self, source_path: str) -> int:
        """Extract species from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        races = data.get('race', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for race in races:
            if not isinstance(race, dict):
                continue

            # Filter by source
            race_source = race.get('source', '').upper()
            if race_source not in self.sources:
                continue

            self._extract_species(race)
            count += 1

        return count

    def _extract_species(self, race: dict) -> None:
        """Extract a single species to a markdown file."""
        name = race.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._species_to_markdown(race)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index
        source = race.get('source', '')
        size = self._format_size_short(race.get('size', ['M']))
        speed = race.get('speed', 30)
        if isinstance(speed, dict):
            speed = speed.get('walk', 30)

        self.index_entries.append({
            'name': name,
            'source': source,
            'size': size,
            'speed': speed,
            'path': filename,
        })

        # Extract traits for searchability
        entries = race.get('entries', [])
        for entry in entries:
            if isinstance(entry, dict) and entry.get('type') == 'entries':
                trait_name = entry.get('name', '')
                if trait_name:
                    # Create anchor-friendly slug
                    trait_anchor = trait_name.lower().replace(" ", "-").replace("'", "")
                    self.trait_entries.append({
                        'name': trait_name,
                        'parent_species': name,
                        'source': source,
                        'path': filename,
                        'anchor': trait_anchor,
                    })

    def _species_to_markdown(self, race: dict) -> str:
        """Convert a species to markdown."""
        parts = []

        name = race.get('name', 'Unknown')
        source = race.get('source', '')
        page = race.get('page', '')

        parts.append(f"# {name}")
        parts.append("")
        parts.append("*Species*")
        parts.append("")

        # Source
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        # Creature type
        creature_types = race.get('creatureTypes', [])
        if creature_types:
            parts.append(f"**Creature Type:** {', '.join(creature_types).title()}")
            parts.append("")

        # Size
        sizes = race.get('size', ['M'])
        size_str = self._format_size(sizes)
        parts.append(f"**Size:** {size_str}")

        # Size entry (if detailed)
        size_entry = race.get('sizeEntry')
        if size_entry and isinstance(size_entry, dict):
            size_desc = size_entry.get('entries', [])
            if size_desc:
                content = self.converter.convert(size_desc, 0)
                if content:
                    parts.append(f" - {content}")
        parts.append("")

        # Speed
        speed = race.get('speed', 30)
        speed_str = self._format_speed(speed)
        parts.append(f"**Speed:** {speed_str}")
        parts.append("")

        # Darkvision
        darkvision = race.get('darkvision')
        if darkvision:
            parts.append(f"**Darkvision:** {darkvision} ft.")
            parts.append("")

        # Resistances
        resist = race.get('resist', [])
        if resist:
            resist_list = []
            for r in resist:
                if isinstance(r, str):
                    resist_list.append(r)
                elif isinstance(r, dict):
                    # Complex resistance with conditions
                    resist_type = r.get('resist', r.get('type', ''))
                    if isinstance(resist_type, list):
                        resist_list.extend(resist_type)
                    elif resist_type:
                        resist_list.append(str(resist_type))
            if resist_list:
                parts.append(f"**Damage Resistance:** {', '.join(resist_list)}")
                parts.append("")

        parts.append("---")
        parts.append("")

        # Traits/entries
        entries = race.get('entries', [])
        if entries:
            parts.append("## Traits")
            parts.append("")
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _format_size(self, sizes: list) -> str:
        """Format size list."""
        if not sizes:
            return 'Medium'
        size_names = [SIZE_MAP.get(s, s) for s in sizes]
        return ' or '.join(size_names)

    def _format_size_short(self, sizes: list) -> str:
        """Format size for index (short form)."""
        if not sizes:
            return 'M'
        return '/'.join(sizes)

    def _format_speed(self, speed) -> str:
        """Format speed value."""
        if isinstance(speed, int):
            return f"{speed} ft."
        elif isinstance(speed, dict):
            parts = []
            walk = speed.get('walk', 30)
            parts.append(f"{walk} ft.")
            if 'fly' in speed:
                fly = speed['fly']
                if isinstance(fly, dict):
                    fly = fly.get('number', fly)
                parts.append(f"fly {fly} ft.")
            if 'swim' in speed:
                parts.append(f"swim {speed['swim']} ft.")
            if 'climb' in speed:
                parts.append(f"climb {speed['climb']} ft.")
            if 'burrow' in speed:
                parts.append(f"burrow {speed['burrow']} ft.")
            return ', '.join(parts)
        return f"{speed} ft."

    def create_index(self) -> None:
        """Create the species index file."""
        parts = ["# Species Index", ""]
        parts.append(f"**Total Species:** {len(self.index_entries)}")
        parts.append("")

        parts.append("| Species | Size | Speed | Source |")
        parts.append("| ------- | ---- | ----- | ------ |")

        for species in sorted(self.index_entries, key=lambda x: x['name']):
            name = species['name']
            size = species['size']
            speed = species['speed']
            source = species['source']
            path = species['path']
            parts.append(f"| [{name}]({path}) | {size} | {speed} ft. | {source} |")

        parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
