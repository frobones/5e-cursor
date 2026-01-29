"""Class and subclass extractor for 5etools data."""

import json
import sys
from pathlib import Path
from typing import Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


class ClassExtractor:
    """Extracts classes and subclasses to individual markdown files."""

    def __init__(self, output_dir: str, source: str = 'XPHB'):
        """
        Initialize the class extractor.

        Args:
            output_dir: Directory to output class files
            source: Source code to filter by (defaults to XPHB for 2024 rules)
        """
        self.output_dir = Path(output_dir)
        self.source = source.upper()
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract classes from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        classes = data.get('class', [])
        subclasses = data.get('subclass', [])
        class_features = data.get('classFeature', [])
        subclass_features = data.get('subclassFeature', [])

        count = 0

        for cls in classes:
            if not isinstance(cls, dict):
                continue

            # Filter by source
            cls_source = cls.get('source', '').upper()
            if cls_source != self.source:
                continue

            # Get features for this class
            cls_name = cls.get('name', '')
            cls_features = [f for f in class_features
                            if f.get('className', '').lower() == cls_name.lower()
                            and f.get('classSource', '').upper() == self.source]

            # Get subclasses for this class
            cls_subclasses = [s for s in subclasses
                              if s.get('className', '').lower() == cls_name.lower()
                              and s.get('classSource', '').upper() == self.source
                              and s.get('source', '').upper() == self.source]

            self._extract_class(cls, cls_features, cls_subclasses, subclass_features)
            count += 1

        return count

    def _extract_class(self, cls: dict, features: list, subclasses: list, all_subclass_features: list) -> None:
        """Extract a class and its subclasses."""
        name = cls.get('name', 'Unknown')
        safe_name = make_safe_filename(name)

        # Create class directory
        class_dir = self.output_dir / safe_name
        class_dir.mkdir(parents=True, exist_ok=True)

        # Create subclasses directory
        subclass_dir = class_dir / 'subclasses'
        subclass_dir.mkdir(parents=True, exist_ok=True)

        # Extract main class file
        class_content = self._class_to_markdown(cls, features)
        class_file = class_dir / f"{safe_name}.md"
        with open(class_file, 'w', encoding='utf-8') as f:
            f.write(class_content)

        # Extract subclasses
        subclass_entries = []
        for subclass in subclasses:
            sc_name = subclass.get('name', 'Unknown')
            sc_short = subclass.get('shortName', sc_name)
            sc_safe = make_safe_filename(sc_name)

            # Get features for this subclass
            sc_features = [f for f in all_subclass_features
                           if f.get('subclassShortName', '').lower() == sc_short.lower()
                           and f.get('className', '').lower() == name.lower()
                           and f.get('source', '').upper() == self.source]

            sc_content = self._subclass_to_markdown(subclass, sc_features, name)
            sc_file = subclass_dir / f"{sc_safe}.md"
            with open(sc_file, 'w', encoding='utf-8') as f:
                f.write(sc_content)

            subclass_entries.append({
                'name': sc_name,
                'path': f"subclasses/{sc_safe}.md",
            })

        # Add to index
        hd = cls.get('hd', {})
        hit_die = f"d{hd.get('faces', 8)}" if isinstance(hd, dict) else 'd8'

        self.index_entries.append({
            'name': name,
            'hit_die': hit_die,
            'subclasses': subclass_entries,
            'path': f"{safe_name}/{safe_name}.md",
        })

    def _class_to_markdown(self, cls: dict, features: list) -> str:
        """Convert a class to markdown."""
        parts = []

        name = cls.get('name', 'Unknown')
        source = cls.get('source', '')
        page = cls.get('page', '')

        parts.append(f"# {name}")
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

        # Hit Dice
        hd = cls.get('hd', {})
        if isinstance(hd, dict):
            parts.append(f"**Hit Dice:** d{hd.get('faces', 8)}")
            parts.append("")

        # Starting Proficiencies
        profs = cls.get('startingProficiencies', {})
        if profs:
            parts.append("## Starting Proficiencies")
            parts.append("")

            armor = profs.get('armor', [])
            if armor:
                armor_str = ', '.join(self._format_prof_item(a) for a in armor)
                parts.append(f"**Armor:** {armor_str}")

            weapons = profs.get('weapons', [])
            if weapons:
                weapon_str = ', '.join(self._format_prof_item(w) for w in weapons)
                parts.append(f"**Weapons:** {weapon_str}")

            tools = profs.get('tools', [])
            if tools:
                tool_str = ', '.join(self._format_prof_item(t) for t in tools)
                parts.append(f"**Tools:** {tool_str}")

            skills = profs.get('skills', [])
            if skills:
                skill_str = self._format_skill_profs(skills)
                parts.append(f"**Skills:** {skill_str}")

            parts.append("")

        # Starting Equipment
        equip = cls.get('startingEquipment', {})
        if equip:
            parts.append("## Starting Equipment")
            parts.append("")
            default_equip = equip.get('default', [])
            for item in default_equip:
                parts.append(f"- {TagConverter.convert_tags(item)}")
            parts.append("")

        # Multiclassing
        multi = cls.get('multiclassing', {})
        if multi:
            parts.append("## Multiclassing")
            parts.append("")
            reqs = multi.get('requirements', {})
            if reqs:
                req_parts = []
                for stat, val in reqs.items():
                    req_parts.append(f"{stat.upper()} {val}")
                parts.append(f"**Requirements:** {', '.join(req_parts)}")
            parts.append("")

        # Class Features by Level
        parts.append("## Class Features")
        parts.append("")

        # Group features by level
        by_level = {}
        for feature in features:
            level = feature.get('level', 1)
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(feature)

        for level in sorted(by_level.keys()):
            parts.append(f"### Level {level}")
            parts.append("")
            for feature in by_level[level]:
                feat_name = feature.get('name', '')
                entries = feature.get('entries', [])
                parts.append(f"#### {feat_name}")
                parts.append("")
                content = self.converter.convert(entries, 0)
                if content:
                    parts.append(content)
                parts.append("")

        return "\n".join(parts)

    def _subclass_to_markdown(self, subclass: dict, features: list, class_name: str) -> str:
        """Convert a subclass to markdown."""
        parts = []

        name = subclass.get('name', 'Unknown')
        source = subclass.get('source', '')
        page = subclass.get('page', '')

        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*{class_name} Subclass*")
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

        # Subclass Features by Level
        if features:
            by_level = {}
            for feature in features:
                level = feature.get('level', 3)
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(feature)

            for level in sorted(by_level.keys()):
                parts.append(f"## Level {level} Features")
                parts.append("")
                for feature in by_level[level]:
                    feat_name = feature.get('name', '')
                    entries = feature.get('entries', [])
                    parts.append(f"### {feat_name}")
                    parts.append("")
                    content = self.converter.convert(entries, 0)
                    if content:
                        parts.append(content)
                    parts.append("")

        return "\n".join(parts)

    def _format_prof_item(self, item) -> str:
        """Format a proficiency item."""
        if isinstance(item, str):
            return item
        elif isinstance(item, dict):
            if 'proficiency' in item:
                return item['proficiency']
            if 'full' in item:
                return item['full']
            # Return first value
            for v in item.values():
                if isinstance(v, str):
                    return v
        return str(item)

    def _format_skill_profs(self, skills: list) -> str:
        """Format skill proficiencies."""
        for skill in skills:
            if isinstance(skill, dict):
                choose = skill.get('choose', {})
                if choose:
                    from_list = choose.get('from', [])
                    count = choose.get('count', 2)
                    if from_list:
                        return f"Choose {count} from: {', '.join(s.title() for s in from_list)}"
        return ''

    def create_index(self) -> None:
        """Create the class index file."""
        parts = ["# Class Index", ""]
        parts.append(f"**Total Classes:** {len(self.index_entries)}")
        parts.append("")

        for cls in sorted(self.index_entries, key=lambda x: x['name']):
            name = cls['name']
            hit_die = cls['hit_die']
            path = cls['path']
            subclasses = cls['subclasses']

            parts.append(f"## [{name}]({path})")
            parts.append("")
            parts.append(f"**Hit Die:** {hit_die}")
            parts.append("")

            if subclasses:
                parts.append("**Subclasses:**")
                parts.append("")
                for sc in sorted(subclasses, key=lambda x: x['name']):
                    sc_name = sc['name']
                    sc_path = f"{make_safe_filename(name)}/{sc['path']}"
                    parts.append(f"- [{sc_name}]({sc_path})")
                parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
