"""Optional feature extractor for Eldritch Invocations, Maneuvers, Metamagic."""

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

# Feature type codes
FEATURE_TYPE_MAP = {
    'EI': 'Eldritch Invocation',
    'MM': 'Metamagic',
    'MV:B': 'Battle Master Maneuver',
    'MV': 'Maneuver',
    'FS:F': 'Fighting Style (Fighter)',
    'FS:P': 'Fighting Style (Paladin)',
    'FS:R': 'Fighting Style (Ranger)',
    'AS': 'Arcane Shot',
    'PB': 'Pact Boon',
    'AI': 'Artificer Infusion',
    'OR': 'Onomancy Resonant',
    'RN': 'Rune Knight Rune',
}


class OptionalFeatureExtractor:
    """Extracts optional features to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract optional features from a source file."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = data.get('optionalfeature', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for feature in features:
            if not isinstance(feature, dict):
                continue

            source = feature.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_feature(feature)
            count += 1

        return count

    def _extract_feature(self, feature: dict) -> None:
        """Extract a single optional feature."""
        name = feature.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._feature_to_markdown(feature)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get feature type
        ftypes = feature.get('featureType', [])
        ftype_name = self._get_feature_type_name(ftypes)
        source = feature.get('source', '')

        self.index_entries.append({
            'name': name,
            'type': ftype_name,
            'source': source,
            'path': filename,
        })

    def _feature_to_markdown(self, feature: dict) -> str:
        """Convert an optional feature to markdown."""
        parts = []

        name = feature.get('name', 'Unknown')
        source = feature.get('source', '')
        page = feature.get('page', '')
        ftypes = feature.get('featureType', [])
        ftype_name = self._get_feature_type_name(ftypes)

        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*{ftype_name}*")
        parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Prerequisites
        prereqs = feature.get('prerequisite', [])
        if prereqs:
            prereq_str = self._format_prerequisites(prereqs)
            if prereq_str:
                parts.append(f"**Prerequisite:** {prereq_str}")
                parts.append("")

        parts.append("---")
        parts.append("")

        # Description
        entries = feature.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _get_feature_type_name(self, ftypes: list) -> str:
        """Convert feature type codes to readable name."""
        if not ftypes:
            return 'Optional Feature'
        
        names = []
        for ft in ftypes:
            if ft in FEATURE_TYPE_MAP:
                names.append(FEATURE_TYPE_MAP[ft])
            else:
                names.append(ft)
        
        return ', '.join(names) if names else 'Optional Feature'

    def _format_prerequisites(self, prereqs: list) -> str:
        """Format prerequisite list."""
        parts = []
        for prereq in prereqs:
            if isinstance(prereq, dict):
                if 'level' in prereq:
                    level = prereq['level']
                    if isinstance(level, dict):
                        level = level.get('level', level)
                    parts.append(f"Level {level}")
                if 'pact' in prereq:
                    parts.append(f"Pact of the {prereq['pact'].title()}")
                if 'patron' in prereq:
                    parts.append(f"{prereq['patron']} patron")
                if 'spell' in prereq:
                    spells = prereq['spell']
                    if isinstance(spells, list):
                        spell_names = []
                        for s in spells:
                            if isinstance(s, str):
                                spell_names.append(s.split('|')[0])
                            elif isinstance(s, dict):
                                spell_names.append(s.get('name', str(s)))
                        if spell_names:
                            parts.append(f"Spell: {', '.join(spell_names)}")
        return '; '.join(parts) if parts else ''

    def create_index(self) -> None:
        """Create the optional feature index file."""
        parts = ["# Optional Feature Index", ""]
        parts.append(f"**Total Features:** {len(self.index_entries)}")
        parts.append("")

        # Group by type
        by_type = {}
        for feat in self.index_entries:
            ftype = feat['type']
            if ftype not in by_type:
                by_type[ftype] = []
            by_type[ftype].append(feat)

        for ftype in sorted(by_type.keys()):
            parts.append(f"## {ftype}")
            parts.append("")
            parts.append("| Feature | Source |")
            parts.append("| ------- | ------ |")

            for feat in sorted(by_type[ftype], key=lambda x: x['name']):
                name = feat['name']
                source = feat['source']
                path = feat['path']
                parts.append(f"| [{name}]({path}) | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
