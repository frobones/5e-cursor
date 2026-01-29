"""Rules extractor for conditions, actions, senses, and variant rules."""

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


class RulesExtractor:
    """Extracts rules glossary entries to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        """
        Initialize the rules extractor.

        Args:
            output_dir: Directory to output rules files
            sources: List of source codes to filter by (defaults to ALLOWED_SOURCES)
        """
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = {
            'conditions': [],
            'actions': [],
            'senses': [],
            'glossary': [],
        }

    def extract_conditions(self, source_path: str) -> int:
        """Extract conditions from conditionsdiseases.json."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        conditions_dir = self.output_dir / 'conditions'
        conditions_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for condition in data.get('condition', []):
            if not isinstance(condition, dict):
                continue

            source = condition.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_entry(condition, conditions_dir, 'Condition', 'conditions')
            count += 1

        # Also extract status entries (like Concentration)
        for status in data.get('status', []):
            if not isinstance(status, dict):
                continue

            source = status.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_entry(status, conditions_dir, 'Status', 'conditions')
            count += 1

        return count

    def extract_actions(self, source_path: str) -> int:
        """Extract actions from actions.json."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        actions_dir = self.output_dir / 'actions'
        actions_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for action in data.get('action', []):
            if not isinstance(action, dict):
                continue

            source = action.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_action(action, actions_dir)
            count += 1

        return count

    def extract_senses(self, source_path: str) -> int:
        """Extract senses from senses.json."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        senses_dir = self.output_dir / 'senses'
        senses_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for sense in data.get('sense', []):
            if not isinstance(sense, dict):
                continue

            source = sense.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_entry(sense, senses_dir, 'Sense', 'senses')
            count += 1

        return count

    def extract_variant_rules(self, source_path: str) -> int:
        """Extract variant rules from variantrules.json."""
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        glossary_dir = self.output_dir / 'glossary'
        glossary_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for rule in data.get('variantrule', []):
            if not isinstance(rule, dict):
                continue

            source = rule.get('source', '').upper()
            if source not in self.sources:
                continue

            self._extract_rule(rule, glossary_dir)
            count += 1

        return count

    def _extract_entry(self, entry: dict, output_dir: Path, entry_type: str, category: str) -> None:
        """Extract a generic rules entry."""
        name = entry.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = output_dir / filename

        content = self._entry_to_markdown(entry, entry_type)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        self.index_entries[category].append({
            'name': name,
            'type': entry_type,
            'source': entry.get('source', ''),
            'path': f"{category}/{filename}",
        })

    def _extract_action(self, action: dict, output_dir: Path) -> None:
        """Extract an action entry."""
        name = action.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = output_dir / filename

        content = self._action_to_markdown(action)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get action time
        time = action.get('time', [])
        time_str = self._format_time(time[0]) if time else 'Action'

        self.index_entries['actions'].append({
            'name': name,
            'time': time_str,
            'source': action.get('source', ''),
            'path': f"actions/{filename}",
        })

    def _extract_rule(self, rule: dict, output_dir: Path) -> None:
        """Extract a variant rule entry."""
        name = rule.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = output_dir / filename

        content = self._rule_to_markdown(rule)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Get rule type
        rule_type = rule.get('ruleType', '')
        type_name = self._get_rule_type_name(rule_type)

        self.index_entries['glossary'].append({
            'name': name,
            'type': type_name,
            'source': rule.get('source', ''),
            'path': f"glossary/{filename}",
        })

    def _entry_to_markdown(self, entry: dict, entry_type: str) -> str:
        """Convert a generic entry to markdown."""
        parts = []

        name = entry.get('name', 'Unknown')
        source = entry.get('source', '')
        page = entry.get('page', '')

        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*{entry_type}*")
        parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = entry.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _action_to_markdown(self, action: dict) -> str:
        """Convert an action to markdown."""
        parts = []

        name = action.get('name', 'Unknown')
        source = action.get('source', '')
        page = action.get('page', '')

        parts.append(f"# {name}")
        parts.append("")
        parts.append("*Action*")
        parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Time
        time = action.get('time', [])
        if time:
            time_str = self._format_time(time[0])
            parts.append(f"**Time:** {time_str}")
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = action.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        # See also
        see_also = action.get('seeAlsoAction', [])
        if see_also:
            parts.append("")
            parts.append("---")
            parts.append("")
            parts.append("**See Also:** " + ", ".join(s.split('|')[0] for s in see_also))

        return "\n".join(parts)

    def _rule_to_markdown(self, rule: dict) -> str:
        """Convert a variant rule to markdown."""
        parts = []

        name = rule.get('name', 'Unknown')
        source = rule.get('source', '')
        page = rule.get('page', '')
        rule_type = rule.get('ruleType', '')
        type_name = self._get_rule_type_name(rule_type)

        parts.append(f"# {name}")
        parts.append("")
        if type_name:
            parts.append(f"*{type_name}*")
            parts.append("")

        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = rule.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        return "\n".join(parts)

    def _format_time(self, time: dict) -> str:
        """Format action time."""
        if isinstance(time, dict):
            number = time.get('number', 1)
            unit = time.get('unit', 'action')
            if unit == 'action':
                return f"{number} action" if number == 1 else f"{number} actions"
            elif unit == 'bonus':
                return "Bonus action"
            elif unit == 'reaction':
                return "Reaction"
            else:
                return f"{number} {unit}"
        return str(time)

    def _get_rule_type_name(self, rule_type: str) -> str:
        """Convert rule type code to name."""
        type_map = {
            'O': 'Optional Rule',
            'V': 'Variant Rule',
            'VO': 'Variant/Optional Rule',
            'C': 'Core Rule',
            '': 'Rule',
        }
        return type_map.get(rule_type, 'Rule')

    def create_index(self) -> None:
        """Create the rules index file."""
        parts = ["# Rules Glossary Index", ""]

        # Summary
        total = sum(len(entries) for entries in self.index_entries.values())
        parts.append(f"**Total Entries:** {total}")
        parts.append("")

        # Conditions
        if self.index_entries['conditions']:
            parts.append("## Conditions")
            parts.append("")
            parts.append("| Condition | Type | Source |")
            parts.append("| --------- | ---- | ------ |")
            for entry in sorted(self.index_entries['conditions'], key=lambda x: x['name']):
                name = entry['name']
                etype = entry['type']
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {etype} | {source} |")
            parts.append("")

        # Actions
        if self.index_entries['actions']:
            parts.append("## Actions")
            parts.append("")
            parts.append("| Action | Time | Source |")
            parts.append("| ------ | ---- | ------ |")
            for entry in sorted(self.index_entries['actions'], key=lambda x: x['name']):
                name = entry['name']
                time = entry['time']
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {time} | {source} |")
            parts.append("")

        # Senses
        if self.index_entries['senses']:
            parts.append("## Senses")
            parts.append("")
            parts.append("| Sense | Source |")
            parts.append("| ----- | ------ |")
            for entry in sorted(self.index_entries['senses'], key=lambda x: x['name']):
                name = entry['name']
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {source} |")
            parts.append("")

        # Glossary
        if self.index_entries['glossary']:
            parts.append("## Rules Glossary")
            parts.append("")
            parts.append("| Rule | Type | Source |")
            parts.append("| ---- | ---- | ------ |")
            for entry in sorted(self.index_entries['glossary'], key=lambda x: x['name']):
                name = entry['name']
                rtype = entry['type']
                source = entry['source']
                path = entry['path']
                parts.append(f"| [{name}]({path}) | {rtype} | {source} |")
            parts.append("")

        index_path = self.output_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
