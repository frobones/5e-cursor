#!/usr/bin/env python3
"""
Rules Engine - Answer rules questions with citations from reference data.

Usage:
    python scripts/campaign/rules_engine.py "What is the prone condition?"
    python scripts/campaign/rules_engine.py "How does sneak attack work?"
    python scripts/campaign/rules_engine.py "fireball spell"
"""

import argparse
import re
import sys
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.reference_linker import ReferenceLinker


@dataclass
class RulesResult:
    """A rules lookup result with citation."""

    name: str
    entry_type: str
    path: str
    content: str
    source: str


def extract_keywords(query: str) -> list[str]:
    """Extract potential lookup keywords from a query.

    Args:
        query: Natural language query

    Returns:
        List of potential keywords to search for
    """
    # Common question words to remove
    stop_words = {
        "what", "is", "the", "how", "does", "do", "can", "a", "an", "of",
        "in", "on", "to", "for", "with", "about", "work", "works", "explain",
        "tell", "me", "describe", "define", "definition", "when", "where",
        "why", "which", "are", "was", "were", "be", "been", "being", "have",
        "has", "had", "having", "does", "did", "doing", "would", "should",
        "could", "might", "must", "shall", "will", "and", "or", "but", "if",
        "then", "else", "that", "this", "these", "those", "my", "your", "its",
        "their", "our", "i", "you", "he", "she", "it", "we", "they",
    }

    # Clean and tokenize
    query_lower = query.lower()

    # Remove punctuation except hyphens and apostrophes
    query_clean = re.sub(r"[^\w\s'-]", " ", query_lower)

    # Split into words
    words = query_clean.split()

    # Filter stop words but keep potential multi-word terms
    keywords = []
    for word in words:
        if word not in stop_words and len(word) > 1:
            keywords.append(word)

    # Also try multi-word phrases (2-3 words)
    phrases = []
    for i in range(len(words)):
        if words[i] not in stop_words:
            # Two-word phrase
            if i + 1 < len(words):
                phrase = f"{words[i]} {words[i+1]}"
                if words[i+1] not in stop_words:
                    phrases.append(phrase)

            # Three-word phrase
            if i + 2 < len(words):
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                phrases.append(phrase)

    # Combine, prioritizing phrases
    return phrases + keywords


def fuzzy_match(query: str, target: str, threshold: float = 0.6) -> bool:
    """Check if query fuzzy-matches target.

    Args:
        query: Search query
        target: Target string to match against
        threshold: Minimum similarity ratio (0-1)

    Returns:
        True if match is above threshold
    """
    query_lower = query.lower()
    target_lower = target.lower()

    # Exact substring match
    if query_lower in target_lower or target_lower in query_lower:
        return True

    # Fuzzy match
    ratio = SequenceMatcher(None, query_lower, target_lower).ratio()
    return ratio >= threshold


def extract_content_from_markdown(file_path: Path, max_chars: int = 2000) -> str:
    """Extract relevant content from a markdown file.

    Args:
        file_path: Path to markdown file
        max_chars: Maximum characters to return

    Returns:
        Extracted content string
    """
    if not file_path.exists():
        return ""

    content = file_path.read_text(encoding="utf-8")

    # Remove frontmatter if present
    if content.startswith("---"):
        end_marker = content.find("---", 3)
        if end_marker != -1:
            content = content[end_marker + 3:].strip()

    # Remove the title heading (first #)
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    content = "\n".join(lines).strip()

    # Truncate if needed
    if len(content) > max_chars:
        # Try to truncate at a paragraph break
        truncated = content[:max_chars]
        last_para = truncated.rfind("\n\n")
        if last_para > max_chars // 2:
            truncated = truncated[:last_para]
        content = truncated + "\n\n*[Content truncated...]*"

    return content


def format_quote(content: str) -> str:
    """Format content as a blockquote.

    Args:
        content: Content to quote

    Returns:
        Blockquoted content
    """
    lines = content.split("\n")
    quoted = "\n".join(f"> {line}" for line in lines)
    return quoted


def search_rules(
    query: str,
    linker: ReferenceLinker,
    books_dir: Path,
    max_results: int = 3,
) -> list[RulesResult]:
    """Search for rules matching a query.

    Args:
        query: Search query
        linker: Reference linker instance
        books_dir: Path to books directory
        max_results: Maximum results to return

    Returns:
        List of RulesResult objects
    """
    keywords = extract_keywords(query)
    results = []
    seen_paths = set()

    # Try exact matches first
    for keyword in keywords:
        entries = linker.search(keyword, limit=max_results * 2)

        for entry in entries:
            path = entry.get("path", "")
            if path in seen_paths:
                continue

            # Check for fuzzy match on name
            name = entry.get("name", "")
            if not fuzzy_match(keyword, name):
                continue

            seen_paths.add(path)

            # Load content
            full_path = books_dir / path
            content = extract_content_from_markdown(full_path)

            if content:
                results.append(RulesResult(
                    name=name,
                    entry_type=entry.get("type", "reference"),
                    path=path,
                    content=content,
                    source=derive_source(path),
                ))

                if len(results) >= max_results:
                    return results

    return results


def derive_source(path: str) -> str:
    """Derive a source citation from a file path.

    Args:
        path: File path like "reference/spells/3rd-level/fireball.md"

    Returns:
        Source string like "PHB, Spells"
    """
    parts = path.split("/")

    # Try to determine book from path
    if "phb" in path.lower():
        book = "PHB"
    elif "dmg" in path.lower():
        book = "DMG"
    elif "mm" in path.lower() or "creatures" in path:
        book = "MM"
    elif "xphb" in path.lower() or "2024" in path.lower():
        book = "PHB 2024"
    else:
        book = "Core Rules"

    # Get category from path
    if len(parts) >= 2:
        category = parts[1].replace("-", " ").title()
    else:
        category = "Reference"

    return f"{book}, {category}"


def format_results(results: list[RulesResult], query: str) -> str:
    """Format search results for display.

    Args:
        results: List of RulesResult objects
        query: Original query for context

    Returns:
        Formatted output string
    """
    if not results:
        return f"No rules found matching: {query}\n\nTry rephrasing or using specific rule names, spell names, or condition names."

    lines = []
    lines.append(f"# Rules: {query}")
    lines.append("")

    for i, result in enumerate(results, 1):
        if len(results) > 1:
            lines.append(f"## {i}. {result.name}")
        else:
            lines.append(f"## {result.name}")

        lines.append(f"*{result.entry_type.title()} — {result.source}*")
        lines.append("")

        # Quote the content
        lines.append(format_quote(result.content))
        lines.append("")

        # Add file reference
        lines.append(f"*Source file: `books/{result.path}`*")
        lines.append("")

    return "\n".join(lines)


def lookup_specific(
    name: str,
    entry_type: Optional[str],
    linker: ReferenceLinker,
    books_dir: Path,
) -> Optional[RulesResult]:
    """Look up a specific rule, spell, or feature by name.

    Args:
        name: Exact or near-exact name
        entry_type: Optional type filter
        linker: Reference linker
        books_dir: Books directory

    Returns:
        RulesResult or None
    """
    entry = linker.find(name, entry_type)
    if not entry:
        return None

    path = entry.get("path", "")
    full_path = books_dir / path
    content = extract_content_from_markdown(full_path)

    if not content:
        return None

    return RulesResult(
        name=entry.get("name", name),
        entry_type=entry.get("type", "reference"),
        path=path,
        content=content,
        source=derive_source(path),
    )


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
        description="Look up D&D 5e rules with citations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/campaign/rules_engine.py "What is the prone condition?"
    python scripts/campaign/rules_engine.py "How does sneak attack work?"
    python scripts/campaign/rules_engine.py "fireball"
    python scripts/campaign/rules_engine.py --spell "magic missile"
    python scripts/campaign/rules_engine.py --condition "poisoned"
    python scripts/campaign/rules_engine.py --feat "sentinel"
        """,
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Rules question or search term",
    )
    parser.add_argument(
        "--spell", "-s",
        help="Look up a specific spell by name",
    )
    parser.add_argument(
        "--condition", "-c",
        help="Look up a specific condition",
    )
    parser.add_argument(
        "--feat", "-f",
        help="Look up a specific feat",
    )
    parser.add_argument(
        "--creature", "-m",
        help="Look up a specific creature/monster",
    )
    parser.add_argument(
        "--item", "-i",
        help="Look up a specific item",
    )
    parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=3,
        help="Maximum results to show (default: 3)",
    )

    args = parser.parse_args()

    # Find repo root
    repo_root = find_repo_root()
    books_dir = repo_root / "books"

    if not books_dir.exists():
        print("Error: Reference data not found. Run 'make' to extract reference data.")
        sys.exit(1)

    # Initialize linker
    try:
        linker = ReferenceLinker(books_dir)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Handle specific lookups
    if args.spell:
        result = lookup_specific(args.spell, "spells", linker, books_dir)
        if result:
            print(format_results([result], args.spell))
        else:
            print(f"Spell not found: {args.spell}")
        return

    if args.condition:
        result = lookup_specific(args.condition, "rules", linker, books_dir)
        if result:
            print(format_results([result], args.condition))
        else:
            print(f"Condition not found: {args.condition}")
        return

    if args.feat:
        result = lookup_specific(args.feat, "feats", linker, books_dir)
        if result:
            print(format_results([result], args.feat))
        else:
            print(f"Feat not found: {args.feat}")
        return

    if args.creature:
        result = lookup_specific(args.creature, "creatures", linker, books_dir)
        if result:
            print(format_results([result], args.creature))
        else:
            print(f"Creature not found: {args.creature}")
        return

    if args.item:
        result = lookup_specific(args.item, "items", linker, books_dir)
        if result:
            print(format_results([result], args.item))
        else:
            print(f"Item not found: {args.item}")
        return

    # General query
    if not args.query:
        parser.print_help()
        sys.exit(1)

    results = search_rules(args.query, linker, books_dir, args.max_results)
    print(format_results(results, args.query))


if __name__ == "__main__":
    main()
