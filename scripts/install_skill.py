#!/usr/bin/env python3
"""Install a skill from the claude-skills marketplace.

This script downloads and installs a skill's command file into the
.claude/commands directory, making it available for use in Claude.
"""

import json
import os
import sys
import shutil
from pathlib import Path
from skill_search import load_marketplace


MARKETPLACE_PATH = Path(__file__).parent.parent / ".claude-plugin" / "marketplace.json"
COMMANDS_DIR = Path(__file__).parent.parent / ".claude" / "commands"


def find_skill(marketplace: dict, skill_id: str) -> dict | None:
    """Find a skill by its ID or name in the marketplace."""
    skills = marketplace.get("skills", [])
    for skill in skills:
        if skill.get("id") == skill_id or skill.get("name", "").lower() == skill_id.lower():
            return skill
    return None


def install_skill(skill: dict, commands_dir: Path, force: bool = False) -> bool:
    """Install a skill's command file into the commands directory.

    Args:
        skill: The skill metadata dict from marketplace.json.
        commands_dir: Path to the .claude/commands directory.
        force: Overwrite existing skill if True.

    Returns:
        True if installation succeeded, False otherwise.
    """
    skill_name = skill.get("name", "unknown")
    command_file = skill.get("command_file")

    if not command_file:
        print(f"Error: Skill '{skill_name}' has no command_file defined.")
        return False

    # Determine destination path
    category = skill.get("category", "")
    if category:
        dest_dir = commands_dir / category
    else:
        dest_dir = commands_dir

    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / Path(command_file).name

    if dest_path.exists() and not force:
        print(f"Skill '{skill_name}' is already installed at {dest_path}.")
        print("Use --force to overwrite.")
        return False

    # Source file relative to repo root
    source_path = Path(__file__).parent.parent / command_file
    if not source_path.exists():
        print(f"Error: Command file not found: {source_path}")
        return False

    shutil.copy2(source_path, dest_path)
    print(f"Installed '{skill_name}' -> {dest_path}")
    return True


def list_installed(commands_dir: Path) -> list[Path]:
    """Return a list of all installed .md command files."""
    return sorted(commands_dir.rglob("*.md"))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Install a skill from the claude-skills marketplace."
    )
    parser.add_argument("skill_id", nargs="?", help="Skill ID or name to install")
    parser.add_argument("--force", action="store_true", help="Overwrite existing installation")
    parser.add_argument("--list", action="store_true", help="List installed skills")
    parser.add_argument(
        "--marketplace", default=str(MARKETPLACE_PATH), help="Path to marketplace.json"
    )
    args = parser.parse_args()

    if args.list:
        installed = list_installed(COMMANDS_DIR)
        if not installed:
            print("No skills installed.")
        else:
            print(f"Installed skills ({len(installed)}):")
            for path in installed:
                print(f"  {path.relative_to(COMMANDS_DIR)}")
        return

    if not args.skill_id:
        parser.print_help()
        sys.exit(1)

    marketplace = load_marketplace(args.marketplace)
    skill = find_skill(marketplace, args.skill_id)

    if not skill:
        print(f"Error: Skill '{args.skill_id}' not found in marketplace.")
        print("Use 'skill_search.py' to browse available skills.")
        sys.exit(1)

    success = install_skill(skill, COMMANDS_DIR, force=args.force)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
