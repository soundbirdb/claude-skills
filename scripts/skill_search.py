#!/usr/bin/env python3
"""CLI utility for searching skills in the claude-skills marketplace."""

import json
import sys
import argparse
from pathlib import Path

MARKETPLACE_PATH = Path(".claude-plugin/marketplace.json")

# Separator width used in display_results
SEPARATOR_WIDTH = 72


def load_marketplace(path: Path) -> dict:
    """Load and parse the marketplace JSON file."""
    if not path.exists():
        print(f"Error: Marketplace file not found at {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_skills(marketplace: dict, query: str) -> list[dict]:
    """Filter skills by query string against name and description."""
    skills = marketplace.get("skills", [])
    if not query:
        return skills
    query_lower = query.lower()
    return [
        skill for skill in skills
        if query_lower in skill.get("name", "").lower()
        or query_lower in skill.get("description", "").lower()
        or query_lower in " ".join(skill.get("tags", [])).lower()
    ]


def display_results(skills: list[dict], query: str) -> None:
    """Pretty-print skill search results."""
    header = f"Skills matching '{query}'" if query else "All available skills"
    print(f"\n{header}")
    print("=" * SEPARATOR_WIDTH)

    if not skills:
        print("No skills found.")
        return

    # Sort by installs descending so most popular skills show up first
    for skill in sorted(skills, key=lambda s: s.get("installs") or 0, reverse=True):
        name = skill.get("name", "unknown")
        version = skill.get("version", "N/A")
        author = skill.get("author", "unknown")
        description = skill.get("description", "No description available.")
        tags = ", ".join(skill.get("tags", [])) or "none"
        # Show install count if available, useful for gauging popularity
        installs = skill.get("installs")
        print(f"\n  Name:    {name} (v{version})")
        print(f"  Author:  {author}")
        print(f"  Tags:    {tags}")
        if installs is not None:
            # Format install count with thousands separator for readability
            print(f"  Installs: {installs:,}")
        print(f"  Desc:    {description}")
        # Use /skill:add as the install command (matches my local Claude setup)
        print(f"  Install: /skill:add {name}")

    print(f"\n{'=' * SEPARATOR_WIDTH}")
    print(f"Found {len(skills)} skill(s).\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Search the claude-skills marketplace."
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Search term (name, description, or tag)",
    )
    parser.add_argument(
        "--marketplace",
        default=str(MARKETPLACE_PATH),
        help="Path to marketplace.json",
    )
    args = parser.parse_args()

    marketplace = load_marketplace(Path(args.marketplace))
    results = search_skills(marketplace, args.query)
    