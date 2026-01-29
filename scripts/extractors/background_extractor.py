"""Background extractor for 5etools data."""

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


class BackgroundExtractor:
    """Extracts backgrounds to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the background extractor.

        Args:
            output_dir: Directory to output background files
            sources: List of source codes to filter by (defaults to ALLOWED_SOURCES)
        """
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        """Extract backgrounds from a source file. Returns count extracted."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        backgrounds = data.get('background', [])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for bg in backgrounds:
            if not isinstance(bg, dict):
                continue

            # Filter by source
            bg_source = bg.get('source', '').upper()
            if bg_source not in self.sources:
                continue

            self._extract_background(bg)
            count += 1

        return count

    def _extract_background(self, bg: dict) -> None:
        """Extract a single background to a markdown file."""
        name = bg.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        content = self._background_to_markdown(bg)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to index
        source = bg.get('source', '')
        feat = self._get_feat_name(bg.get('feats', []))

        self.index_entries.append({
            'name': name,
            'source': source,
            'feat': feat,
            'path': filename,
        })

    def _background_to_markdown(self, bg: dict) -> str:
        """Convert a background to markdown."""
        parts = []

        name = bg.get('name', 'Unknown')
        source = bg.get('source', '')
        page = bg.get('page', '')

        parts.append(f"# {name}")
        parts.append("")
        parts.append("*Background*")
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

        # Ability scores
        abilities = bg.get('ability', [])
        if abilities:
            ability_str = self._format_abilities(abilities)
            if ability_str:
                parts.append(f"**Ability Scores:** {ability_str}")
                parts.append("")

        # Feat
        feats = bg.get('feats', [])
        if feats:
            feat_str = self._format_feats(feats)
            if feat_str:
                parts.append(f"**Feat:** {feat_str}")
                parts.append("")

        # Skill proficiencies
        skills = bg.get('skillProficiencies', [])
        if skills:
            skill_str = self._format_proficiencies(skills)
            if skill_str:
                parts.append(f"**Skill Proficiencies:** {skill_str}")
                parts.append("")

        # Tool proficiencies
        tools = bg.get('toolProficiencies', [])
        if tools:
            tool_str = self._format_proficiencies(tools)
            if tool_str:
                parts.append(f"**Tool Proficiency:** {tool_str}")
                parts.append("")

        # Language proficiencies
        languages = bg.get('languageProficiencies', [])
        if languages:
            lang_str = self._format_proficiencies(languages)
            if lang_str:
                parts.append(f"**Languages:** {lang_str}")
                parts.append("")

        parts.append("---")
        parts.append("")

        # Description/entries
        entries = bg.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _format_abilities(self, abilities: list) -> str:
        """Format ability score options."""
        ability_names = {
            'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
            'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'
        }
        parts = []
        for ability in abilities:
            if isinstance(ability, dict):
                if 'choose' in ability:
                    choose = ability['choose']
                    if isinstance(choose, dict):
                        from_list = choose.get('from', choose.get('weighted', {}).get('from', []))
                        if from_list:
                            names = [ability_names.get(a, a.upper()) for a in from_list]
                            parts.append(', '.join(names))
                else:
                    for ab, val in ability.items():
                        if ab in ability_names:
                            parts.append(f"{ability_names[ab]} +{val}")
        return '; '.join(parts) if parts else ''

    def _format_feats(self, feats: list) -> str:
        """Format feat list."""
        parts = []
        for feat in feats:
            if isinstance(feat, dict):
                for key in feat.keys():
                    # Key format: "feat name|source"
                    feat_name = key.split('|')[0]
                    # Clean up the name
                    feat_name = feat_name.replace(';', ' (') + ')' if ';' in feat_name else feat_name
                    parts.append(TagConverter.convert_tags(f"{{@feat {feat_name}}}"))
        return ', '.join(parts) if parts else ''

    def _get_feat_name(self, feats: list) -> str:
        """Get feat name for index."""
        for feat in feats:
            if isinstance(feat, dict):
                for key in feat.keys():
                    return key.split('|')[0].split(';')[0]
        return '-'

    def _format_proficiencies(self, profs: list) -> str:
        """Format proficiency list."""
        parts = []
        for prof in profs:
            if isinstance(prof, dict):
                for key, val in prof.items():
                    if val is True:
                        parts.append(key.title())
                    elif isinstance(val, int):
                        parts.append(f"{key.title()} ({val})")
                    elif key == 'choose':
                        if isinstance(val, dict):
                            from_list = val.get('from', [])
                            count = val.get('count', 1)
                            if from_list:
                                parts.append(f"Choose {count} from: {', '.join(f.title() for f in from_list)}")
        return ', '.join(parts) if parts else ''

    def create_index(self) -> None:
        """Create the background index file."""
        parts = ["# Background Index", ""]
        parts.append(f"**Total Backgrounds:** {len(self.index_entries)}")
        parts.append("")

        parts.append("| Background | Feat | Source |")
        parts.append("| ---------- | ---- | ------ |")

        for bg in sorted(self.index_entries, key=lambda x: x['name']):
            name = bg['name']
            feat = bg['feat']
            source = bg['source']
            path = bg['path']
            parts.append(f"| [{name}]({path}) | {feat} | {source} |")

        parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
