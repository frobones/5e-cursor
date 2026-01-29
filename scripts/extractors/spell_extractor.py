"""Spell extractor for 5etools data."""

import json
import sys
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import EntryConverter
from extractors.base import make_safe_filename, ordinal


class SpellExtractor:
    """Extracts spells to individual markdown files organized by level."""

    SCHOOL_MAP = {
        'A': 'Abjuration',
        'C': 'Conjuration',
        'D': 'Divination',
        'E': 'Enchantment',
        'I': 'Illusion',
        'N': 'Necromancy',
        'T': 'Transmutation',
        'V': 'Evocation',
    }

    LEVEL_DIRS = {
        0: 'cantrips',
        1: '1st-level',
        2: '2nd-level',
        3: '3rd-level',
        4: '4th-level',
        5: '5th-level',
        6: '6th-level',
        7: '7th-level',
        8: '8th-level',
        9: '9th-level',
    }

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract spells from a source file. Returns count of spells extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        spells = data.get('spell', [])
        count = 0

        for spell in spells:
            if not isinstance(spell, dict):
                continue
            self._extract_spell(spell)
            count += 1

        return count

    def _extract_spell(self, spell: dict) -> None:
        """Extract a single spell to a markdown file."""
        name = spell.get('name', 'Unknown')
        level = spell.get('level', 0)
        school = spell.get('school', 'V')
        source = spell.get('source', '')

        # Determine output directory
        level_dir = self.LEVEL_DIRS.get(level, f'{level}th-level')
        spell_dir = self.output_dir / level_dir
        spell_dir.mkdir(parents=True, exist_ok=True)

        # Create filename
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = spell_dir / filename

        # Generate content
        content = self._spell_to_markdown(spell)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index
        school_name = self.SCHOOL_MAP.get(school, school)
        self.index_entries.append({
            'name': name,
            'level': level,
            'school': school_name,
            'source': source,
            'path': f"{level_dir}/{filename}",
        })

    def _spell_to_markdown(self, spell: dict) -> str:
        """Convert a spell to markdown format."""
        parts = []

        name = spell.get('name', 'Unknown')
        level = spell.get('level', 0)
        school = self.SCHOOL_MAP.get(spell.get('school', 'V'), 'Evocation')
        source = spell.get('source', '')
        page = spell.get('page', '')

        # Title
        parts.append(f"# {name}")
        parts.append("")

        # Level and school
        if level == 0:
            parts.append(f"*{school} cantrip*")
        else:
            parts.append(f"*{ordinal(level)}-level {school}*")
        parts.append("")

        # Source
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Casting time
        time = spell.get('time', [])
        if time:
            time_str = self._format_time(time[0])
            parts.append(f"**Casting Time:** {time_str}")

        # Range
        range_data = spell.get('range', {})
        range_str = self._format_range(range_data)
        parts.append(f"**Range:** {range_str}")

        # Components
        components = spell.get('components', {})
        comp_str = self._format_components(components)
        parts.append(f"**Components:** {comp_str}")

        # Duration
        duration = spell.get('duration', [])
        if duration:
            dur_str = self._format_duration(duration[0])
            parts.append(f"**Duration:** {dur_str}")

        parts.append("")
        parts.append("---")
        parts.append("")

        # Description
        entries = spell.get('entries', [])
        content = self.converter.convert(entries, 0)
        if content:
            parts.append(content)

        # Higher levels
        higher = spell.get('entriesHigherLevel', [])
        if higher:
            parts.append("")
            higher_content = self.converter.convert(higher, 0)
            if higher_content:
                parts.append(higher_content)

        # Classes (if available)
        classes = spell.get('classes', {})
        if classes:
            parts.append("")
            class_list = self._format_classes(classes)
            if class_list:
                parts.append(f"**Classes:** {class_list}")

        return "\n".join(parts)

    def _format_time(self, time: dict) -> str:
        """Format casting time."""
        if isinstance(time, dict):
            number = time.get('number', 1)
            unit = time.get('unit', 'action')
            if unit == 'action':
                return f"{number} action" if number == 1 else f"{number} actions"
            elif unit == 'bonus':
                return "1 bonus action"
            elif unit == 'reaction':
                condition = time.get('condition', '')
                return f"1 reaction{', ' + condition if condition else ''}"
            else:
                return f"{number} {unit}"
        return str(time)

    def _format_range(self, range_data: dict) -> str:
        """Format spell range."""
        range_type = range_data.get('type', 'point')
        distance = range_data.get('distance', {})

        if range_type == 'special':
            return 'Special'

        dist_type = distance.get('type', 'feet')
        amount = distance.get('amount', 0)

        if dist_type == 'self':
            return 'Self'
        elif dist_type == 'touch':
            return 'Touch'
        elif dist_type == 'sight':
            return 'Sight'
        elif dist_type == 'unlimited':
            return 'Unlimited'
        elif amount:
            return f"{amount} {dist_type}"
        return 'Self'

    def _format_components(self, components: dict) -> str:
        """Format spell components."""
        parts = []
        if components.get('v'):
            parts.append('V')
        if components.get('s'):
            parts.append('S')
        if components.get('m'):
            material = components.get('m')
            if isinstance(material, dict):
                material = material.get('text', '')
            parts.append(f'M ({material})')
        return ', '.join(parts) if parts else 'None'

    def _format_duration(self, duration: dict) -> str:
        """Format spell duration."""
        dur_type = duration.get('type', 'instant')

        if dur_type == 'instant':
            return 'Instantaneous'
        elif dur_type == 'permanent':
            return 'Permanent'
        elif dur_type == 'special':
            return 'Special'
        elif dur_type == 'timed':
            dur_data = duration.get('duration', {})
            amount = dur_data.get('amount', 1)
            unit = dur_data.get('type', 'minute')
            concentration = duration.get('concentration', False)
            dur_str = f"{amount} {unit}" if amount == 1 else f"{amount} {unit}s"
            if concentration:
                dur_str = f"Concentration, up to {dur_str}"
            return dur_str
        return str(dur_type)

    def _format_classes(self, classes: dict) -> str:
        """Format class list."""
        from_classes = classes.get('fromClassList', [])
        class_names = []
        for cls in from_classes:
            if isinstance(cls, dict):
                class_names.append(cls.get('name', ''))
            else:
                class_names.append(str(cls))
        return ', '.join(sorted(set(class_names)))

    def create_index(self) -> None:
        """Create the spell index file."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        parts = ["# Spell Index", ""]

        # Group by level
        by_level = {}
        for spell in self.index_entries:
            level = spell['level']
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(spell)

        # Generate index by level
        for level in sorted(by_level.keys()):
            level_name = "Cantrips" if level == 0 else f"{ordinal(level)}-Level Spells"
            parts.append(f"## {level_name}")
            parts.append("")
            parts.append("| Spell | School | Source |")
            parts.append("| ----- | ------ | ------ |")

            for spell in sorted(by_level[level], key=lambda x: x['name']):
                name = spell['name']
                school = spell['school']
                source = spell['source']
                path = spell['path']
                parts.append(f"| [{name}]({path}) | {school} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
