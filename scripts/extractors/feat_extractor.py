"""Feat extractor for 5etools data."""

import json
import sys
from pathlib import Path
from typing import Optional

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from extract_book import TagConverter, EntryConverter
from extractors.base import make_safe_filename


# Sources to include
ALLOWED_SOURCES = {'XPHB', 'XDMG', 'XMM', 'AAG', 'BAM'}

# Feat category codes
CATEGORY_MAP = {
    'G': 'General',
    'O': 'Origin',
    'F': 'Fighting Style',
    'E': 'Epic Boon',
}


class FeatExtractor:
    """Extracts feats to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the feat extractor.

        Args:
            output_dir: Directory to output feat files
            sources: List of source codes to filter by (defaults to ALLOWED_SOURCES)
        """
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract feats from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        feats = data.get('feat', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for feat in feats:
            if not isinstance(feat, dict):
                continue

            # Filter by source
            feat_source = feat.get('source', '').upper()
            if feat_source not in self.sources:
                continue

            self._extract_feat(feat)
            count += 1

        return count

    def _extract_feat(self, feat: dict) -> None:
        """Extract a single feat to a markdown file."""
        name = feat.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._feat_to_markdown(feat)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index
        category = feat.get('category', 'G')
        category_name = CATEGORY_MAP.get(category, category)
        source = feat.get('source', '')
        prereq = self._format_prerequisite_short(feat.get('prerequisite', []))

        self.index_entries.append({
            'name': name,
            'category': category_name,
            'source': source,
            'prerequisite': prereq,
            'path': filename,
        })

    def _feat_to_markdown(self, feat: dict) -> str:
        """Convert a feat to markdown."""
        parts = []

        name = feat.get('name', 'Unknown')
        source = feat.get('source', '')
        page = feat.get('page', '')
        category = feat.get('category', 'G')
        category_name = CATEGORY_MAP.get(category, category)

        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*{category_name} Feat*")
        parts.append("")

        # Source
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Prerequisites
        prereqs = feat.get('prerequisite', [])
        if prereqs:
            prereq_str = self._format_prerequisite(prereqs)
            parts.append(f"**Prerequisite:** {prereq_str}")
            parts.append("")

        # Repeatable
        if feat.get('repeatable'):
            parts.append("**Repeatable:** Yes")
            parts.append("")

        parts.append("---")
        parts.append("")

        # Description/entries
        entries = feat.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _format_prerequisite(self, prereqs: list) -> str:
        """Format prerequisite list."""
        parts = []
        for prereq in prereqs:
            if isinstance(prereq, dict):
                if 'level' in prereq:
                    level = prereq['level']
                    if isinstance(level, dict):
                        level = level.get('level', level)
                    parts.append(f"Level {level}")
                if 'ability' in prereq:
                    abilities = prereq['ability']
                    if isinstance(abilities, list):
                        for ab in abilities:
                            for stat, val in ab.items():
                                parts.append(f"{stat.upper()} {val}+")
                if 'spellcasting' in prereq:
                    parts.append("Spellcasting or Pact Magic feature")
                if 'race' in prereq:
                    races = prereq['race']
                    if isinstance(races, list):
                        race_names = [r.get('name', str(r)) if isinstance(r, dict) else str(r) for r in races]
                        parts.append(f"Race: {', '.join(race_names)}")
                if 'feat' in prereq:
                    feats = prereq['feat']
                    if isinstance(feats, list):
                        feat_names = [f.split('|')[0] for f in feats]
                        parts.append(f"Feat: {', '.join(feat_names)}")
                if 'proficiency' in prereq:
                    profs = prereq['proficiency']
                    if isinstance(profs, list):
                        prof_names = []
                        for p in profs:
                            if isinstance(p, dict):
                                for k, v in p.items():
                                    prof_names.append(f"{k}: {v}")
                        if prof_names:
                            parts.append(f"Proficiency: {', '.join(prof_names)}")
        return '; '.join(parts) if parts else 'None'

    def _format_prerequisite_short(self, prereqs: list) -> str:
        """Format prerequisite for index (short form)."""
        parts = []
        for prereq in prereqs:
            if isinstance(prereq, dict):
                if 'level' in prereq:
                    level = prereq['level']
                    if isinstance(level, dict):
                        level = level.get('level', level)
                    parts.append(f"Lvl {level}")
                if 'ability' in prereq:
                    parts.append("Ability")
                if 'spellcasting' in prereq:
                    parts.append("Spellcasting")
        return ', '.join(parts) if parts else '-'

    def create_index(self) -> None:
        """Create the feat index file."""
        parts = ["# Feat Index", ""]
        parts.append(f"**Total Feats:** {len(self.index_entries)}")
        parts.append("")

        # Group by category
        by_category = {}
        for feat in self.index_entries:
            cat = feat['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(feat)

        # Order: Origin, General, Fighting Style, Epic Boon
        category_order = ['Origin', 'General', 'Fighting Style', 'Epic Boon']

        for category in category_order:
            if category not in by_category:
                continue

            parts.append(f"## {category} Feats")
            parts.append("")
            parts.append("| Feat | Prerequisite | Source |")
            parts.append("| ---- | ------------ | ------ |")

            for feat in sorted(by_category[category], key=lambda x: x['name']):
                name = feat['name']
                prereq = feat['prerequisite']
                source = feat['source']
                path = feat['path']
                parts.append(f"| [{name}]({path}) | {prereq} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
