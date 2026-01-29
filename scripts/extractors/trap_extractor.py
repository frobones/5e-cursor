"""Trap and hazard extractor for 5etools data."""

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


class TrapExtractor:
    """Extracts traps and hazards to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = {'traps': [], 'hazards': []}

    def extract_file(self, source_path: str) -> dict:
        """Extract traps and hazards from a source file. Returns counts."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        traps_dir = self.output_dir / 'traps'
        hazards_dir = self.output_dir / 'hazards'
        traps_dir.mkdir(parents=True, exist_ok=True)
        hazards_dir.mkdir(parents=True, exist_ok=True)

        trap_count = 0
        hazard_count = 0

        # Extract traps
        for trap in data.get('trap', []):
            if not isinstance(trap, dict):
                continue
            source = trap.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(trap, traps_dir, 'Trap', 'traps')
            trap_count += 1

        # Extract hazards
        for hazard in data.get('hazard', []):
            if not isinstance(hazard, dict):
                continue
            source = hazard.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(hazard, hazards_dir, 'Hazard', 'hazards')
            hazard_count += 1

        return {'traps': trap_count, 'hazards': hazard_count}

    def _extract_entry(self, entry: dict, output_dir: Path, entry_type: str, category: str) -> None:
        """Extract a trap or hazard entry."""
        name = entry.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = output_dir / filename

        content = self._entry_to_markdown(entry, entry_type)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        source = entry.get('source', '')
        threat = entry.get('threat', '')

        self.index_entries[category].append({
            'name': name,
            'type': entry_type,
            'threat': threat,
            'source': source,
            'path': f"{category}/{filename}",
        })

    def _entry_to_markdown(self, entry: dict, entry_type: str) -> str:
        """Convert a trap/hazard to markdown."""
        parts = []

        name = entry.get('name', 'Unknown')
        source = entry.get('source', '')
        page = entry.get('page', '')
        threat = entry.get('threat', '')

        parts.append(f"# {name}")
        parts.append("")
        
        type_str = entry_type
        if threat:
            type_str += f" ({threat} threat)"
        parts.append(f"*{type_str}*")
        parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        # Description
        entries = entry.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def create_index(self) -> None:
        """Create the traps/hazards index file."""
        parts = ["# Traps and Hazards Index", ""]
        
        total = len(self.index_entries['traps']) + len(self.index_entries['hazards'])
        parts.append(f"**Total Entries:** {total}")
        parts.append("")

        # Traps
        if self.index_entries['traps']:
            parts.append("## Traps")
            parts.append("")
            parts.append("| Trap | Threat | Source |")
            parts.append("| ---- | ------ | ------ |")

            for entry in sorted(self.index_entries['traps'], key=lambda x: x['name']):
                name = entry['name']
                threat = entry['threat'] or '-'
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {threat} | {source} |")

            parts.append("")

        # Hazards
        if self.index_entries['hazards']:
            parts.append("## Hazards")
            parts.append("")
            parts.append("| Hazard | Threat | Source |")
            parts.append("| ------ | ------ | ------ |")

            for entry in sorted(self.index_entries['hazards'], key=lambda x: x['name']):
                name = entry['name']
                threat = entry['threat'] or '-'
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {threat} | {source} |")

            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
