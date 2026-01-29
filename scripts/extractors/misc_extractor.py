"""Miscellaneous extractors for languages, bastions, deities, rewards, objects, decks."""

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


class LanguageExtractor:
    """Extracts languages to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for lang in data.get('language', []):
            if not isinstance(lang, dict):
                continue
            source = lang.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(lang)
            count += 1

        return count

    def _extract_entry(self, lang: dict) -> None:
        name = lang.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        
        lang_type = lang.get('type', 'Standard')
        parts.append(f"*{lang_type} Language*")
        parts.append("")

        source = lang.get('source', '')
        page = lang.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Typical speakers
        speakers = lang.get('typicalSpeakers', [])
        if speakers:
            parts.append(f"**Typical Speakers:** {', '.join(speakers)}")
            parts.append("")

        # Script
        script = lang.get('script', '')
        if script:
            parts.append(f"**Script:** {script}")
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = lang.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        self.index_entries.append({
            'name': name,
            'type': lang_type,
            'source': source,
            'path': filename,
        })

    def create_index(self) -> None:
        parts = ["# Language Index", ""]
        parts.append(f"**Total Languages:** {len(self.index_entries)}")
        parts.append("")
        parts.append("| Language | Type | Source |")
        parts.append("| -------- | ---- | ------ |")

        for lang in sorted(self.index_entries, key=lambda x: x['name']):
            parts.append(f"| [{lang['name']}]({lang['path']}) | {lang['type']} | {lang['source']} |")

        parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))


class BastionExtractor:
    """Extracts bastion facilities to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for facility in data.get('facility', []):
            if not isinstance(facility, dict):
                continue
            source = facility.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(facility)
            count += 1

        return count

    def _extract_entry(self, facility: dict) -> None:
        name = facility.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        
        ftype = facility.get('type', 'Facility')
        parts.append(f"*{ftype.title()} Facility*")
        parts.append("")

        source = facility.get('source', '')
        page = facility.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Level
        level = facility.get('level', '')
        if level:
            parts.append(f"**Level:** {level}")

        # Space
        space = facility.get('space', '')
        if space:
            parts.append(f"**Space:** {space}")

        # Hirelings
        hirelings = facility.get('hirelings', '')
        if hirelings:
            parts.append(f"**Hirelings:** {hirelings}")

        # Order
        order = facility.get('order', '')
        if order:
            parts.append(f"**Order:** {order}")

        parts.append("")
        parts.append("---")
        parts.append("")

        entries = facility.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        self.index_entries.append({
            'name': name,
            'type': ftype,
            'level': level,
            'source': source,
            'path': filename,
        })

    def create_index(self) -> None:
        parts = ["# Bastion Facility Index", ""]
        parts.append(f"**Total Facilities:** {len(self.index_entries)}")
        parts.append("")
        parts.append("| Facility | Type | Level | Source |")
        parts.append("| -------- | ---- | ----- | ------ |")

        for f in sorted(self.index_entries, key=lambda x: x['name']):
            level = f['level'] or '-'
            parts.append(f"| [{f['name']}]({f['path']}) | {f['type']} | {level} | {f['source']} |")

        parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))


class DeityExtractor:
    """Extracts deities to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for deity in data.get('deity', []):
            if not isinstance(deity, dict):
                continue
            source = deity.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(deity)
            count += 1

        return count

    def _extract_entry(self, deity: dict) -> None:
        name = deity.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        
        title = deity.get('title', '')
        if title:
            parts.append(f"*{title}*")
            parts.append("")

        source = deity.get('source', '')
        page = deity.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Pantheon
        pantheon = deity.get('pantheon', '')
        if pantheon:
            parts.append(f"**Pantheon:** {pantheon}")

        # Alignment
        alignment = deity.get('alignment', [])
        if alignment:
            align_map = {'L': 'Lawful', 'N': 'Neutral', 'C': 'Chaotic', 'G': 'Good', 'E': 'Evil'}
            align_str = ' '.join(align_map.get(a, a) for a in alignment)
            parts.append(f"**Alignment:** {align_str}")

        # Domains
        domains = deity.get('domains', [])
        if domains:
            parts.append(f"**Domains:** {', '.join(domains)}")

        # Symbol
        symbol = deity.get('symbol', '')
        if symbol:
            parts.append(f"**Symbol:** {symbol}")

        parts.append("")
        parts.append("---")
        parts.append("")

        entries = deity.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        self.index_entries.append({
            'name': name,
            'pantheon': pantheon,
            'alignment': ' '.join(alignment) if alignment else '-',
            'source': source,
            'path': filename,
        })

    def create_index(self) -> None:
        parts = ["# Deity Index", ""]
        parts.append(f"**Total Deities:** {len(self.index_entries)}")
        parts.append("")

        # Group by pantheon
        by_pantheon = {}
        for d in self.index_entries:
            p = d['pantheon'] or 'Other'
            if p not in by_pantheon:
                by_pantheon[p] = []
            by_pantheon[p].append(d)

        for pantheon in sorted(by_pantheon.keys()):
            parts.append(f"## {pantheon}")
            parts.append("")
            parts.append("| Deity | Alignment | Source |")
            parts.append("| ----- | --------- | ------ |")

            for d in sorted(by_pantheon[pantheon], key=lambda x: x['name']):
                parts.append(f"| [{d['name']}]({d['path']}) | {d['alignment']} | {d['source']} |")

            parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))


class RewardExtractor:
    """Extracts rewards (boons, blessings) to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for reward in data.get('reward', []):
            if not isinstance(reward, dict):
                continue
            source = reward.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(reward)
            count += 1

        return count

    def _extract_entry(self, reward: dict) -> None:
        name = reward.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        
        rtype = reward.get('type', 'Reward')
        parts.append(f"*{rtype}*")
        parts.append("")

        source = reward.get('source', '')
        page = reward.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = reward.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        self.index_entries.append({
            'name': name,
            'type': rtype,
            'source': source,
            'path': filename,
        })

    def create_index(self) -> None:
        parts = ["# Reward Index", ""]
        parts.append(f"**Total Rewards:** {len(self.index_entries)}")
        parts.append("")
        parts.append("| Reward | Type | Source |")
        parts.append("| ------ | ---- | ------ |")

        for r in sorted(self.index_entries, key=lambda x: x['name']):
            parts.append(f"| [{r['name']}]({r['path']}) | {r['type']} | {r['source']} |")

        parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))


class ObjectExtractor:
    """Extracts objects to individual markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for obj in data.get('object', []):
            if not isinstance(obj, dict):
                continue
            source = obj.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_entry(obj)
            count += 1

        return count

    def _extract_entry(self, obj: dict) -> None:
        name = obj.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = self.output_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        parts.append("*Object*")
        parts.append("")

        source = obj.get('source', '')
        page = obj.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        # Size
        size = obj.get('size', '')
        if size:
            size_map = {'T': 'Tiny', 'S': 'Small', 'M': 'Medium', 'L': 'Large', 'H': 'Huge', 'G': 'Gargantuan'}
            if isinstance(size, list):
                size_str = ', '.join(size_map.get(s, s) for s in size)
            else:
                size_str = size_map.get(size, size)
            parts.append(f"**Size:** {size_str}")

        # AC
        ac = obj.get('ac', '')
        if ac:
            parts.append(f"**Armor Class:** {ac}")

        # HP
        hp = obj.get('hp', '')
        if hp:
            parts.append(f"**Hit Points:** {hp}")

        parts.append("")
        parts.append("---")
        parts.append("")

        entries = obj.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        self.index_entries.append({
            'name': name,
            'source': source,
            'path': filename,
        })

    def create_index(self) -> None:
        parts = ["# Object Index", ""]
        parts.append(f"**Total Objects:** {len(self.index_entries)}")
        parts.append("")
        parts.append("| Object | Source |")
        parts.append("| ------ | ------ |")

        for o in sorted(self.index_entries, key=lambda x: x['name']):
            parts.append(f"| [{o['name']}]({o['path']}) | {o['source']} |")

        parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))


class DeckExtractor:
    """Extracts decks and cards to markdown files."""

    def __init__(self, output_dir: str, sources: Optional[list] = None):
        self.output_dir = Path(output_dir)
        self.sources = set(s.upper() for s in sources) if sources else ALLOWED_SOURCES
        self.converter = EntryConverter(heading_level=2)
        self.index_entries = []

    def extract_file(self, source_path: str) -> int:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        count = 0

        for deck in data.get('deck', []):
            if not isinstance(deck, dict):
                continue
            source = deck.get('source', '').upper()
            if source not in self.sources:
                continue
            self._extract_deck(deck, data.get('card', []))
            count += 1

        return count

    def _extract_deck(self, deck: dict, all_cards: list) -> None:
        name = deck.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        
        # Create deck directory
        deck_dir = self.output_dir / safe_name
        deck_dir.mkdir(parents=True, exist_ok=True)

        # Get cards for this deck
        deck_cards = [c for c in all_cards if c.get('set') == name and c.get('source', '').upper() in self.sources]

        # Write deck file
        parts = []
        parts.append(f"# {name}")
        parts.append("")
        parts.append("*Deck*")
        parts.append("")

        source = deck.get('source', '')
        page = deck.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append(f"**Cards:** {len(deck_cards)}")
        parts.append("")
        parts.append("---")
        parts.append("")

        entries = deck.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)
                parts.append("")

        # List cards
        if deck_cards:
            parts.append("## Cards")
            parts.append("")
            for card in sorted(deck_cards, key=lambda x: x.get('name', '')):
                card_name = card.get('name', 'Card')
                card_safe = make_safe_filename(card_name)
                parts.append(f"- [{card_name}]({card_safe}.md)")

        with open(deck_dir / f"{safe_name}.md", 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

        # Write individual card files
        for card in deck_cards:
            self._extract_card(card, deck_dir)

        self.index_entries.append({
            'name': name,
            'cards': len(deck_cards),
            'source': source,
            'path': f"{safe_name}/{safe_name}.md",
        })

    def _extract_card(self, card: dict, deck_dir: Path) -> None:
        name = card.get('name', 'Unknown')
        safe_name = make_safe_filename(name)
        filename = f"{safe_name}.md"
        filepath = deck_dir / filename

        parts = []
        parts.append(f"# {name}")
        parts.append("")
        parts.append(f"*Card from {card.get('set', 'Unknown Deck')}*")
        parts.append("")

        source = card.get('source', '')
        page = card.get('page', '')
        if source:
            source_str = f"**Source:** {source}"
            if page:
                source_str += f", page {page}"
            parts.append(source_str)
            parts.append("")

        parts.append("---")
        parts.append("")

        entries = card.get('entries', [])
        if entries:
            content = self.converter.convert(entries, 0)
            if content:
                parts.append(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))

    def create_index(self) -> None:
        parts = ["# Deck Index", ""]
        parts.append(f"**Total Decks:** {len(self.index_entries)}")
        parts.append("")
        parts.append("| Deck | Cards | Source |")
        parts.append("| ---- | ----- | ------ |")

        for d in sorted(self.index_entries, key=lambda x: x['name']):
            parts.append(f"| [{d['name']}]({d['path']}) | {d['cards']} | {d['source']} |")

        parts.append("")

        with open(self.output_dir / 'index.md', 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
