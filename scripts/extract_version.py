#!/usr/bin/env python3
"""
Extract Version from CHANGELOG

Extracts the latest version number from a CHANGELOG.md file.
Used by GitHub Actions workflow to determine release version.

Usage:
    python scripts/extract_version.py /path/to/CHANGELOG.md
"""

import re
import sys
from pathlib import Path


def extract_version(changelog_path: Path) -> str:
    """
    Extract latest version from CHANGELOG.md.

    Args:
        changelog_path: Path to CHANGELOG.md file

    Returns:
        Version string (e.g., "1.0.0")
    """
    if not changelog_path.exists():
        return "1.0.0"

    with open(changelog_path, "r") as f:
        content = f.read()

    # Match ## [X.Y.Z] or ## X.Y.Z
    match = re.search(r"^##\s+\[?(\d+\.\d+\.\d+)\]?", content, re.MULTILINE)
    if match:
        return match.group(1)

    return "1.0.0"


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python extract_version.py /path/to/CHANGELOG.md", file=sys.stderr)
        sys.exit(1)

    changelog_path = Path(sys.argv[1])

    if not changelog_path.exists():
        print(f"Error: File not found: {changelog_path}", file=sys.stderr)
        sys.exit(1)

    version = extract_version(changelog_path)
    print(version)


if __name__ == "__main__":
    main()
