"""
Content Builder

Builds Circle post content from template files (README, CHANGELOG).
"""

import re
from pathlib import Path
from typing import Optional

from .markdown_to_tiptap import markdown_to_tiptap


def build_post_content(
    template_dir: Path,
    template_name: str,
    version: str,
    download_url: str,
) -> dict:
    """
    Build Circle post content with TipTap JSON format.

    Args:
        template_dir: Path to template directory
        template_name: Template identifier (e.g., "daily-summary-email")
        version: Version string (e.g., "1.0.0")
        download_url: Public GitHub release download URL

    Returns:
        {
            "title": str,
            "body": dict,  # TipTap JSON
            "slug": str
        }
    """
    template_dir = Path(template_dir)

    # Generate slug (lowercase, hyphenated)
    slug = generate_slug(template_name)

    # Build title
    title = f"{_humanize_name(template_name)} v{version}"

    # Read README
    readme_path = template_dir / "README.md"
    if not readme_path.exists():
        raise FileNotFoundError(f"README.md not found in {template_dir}")

    with open(readme_path, "r") as f:
        readme_content = f.read()

    # Convert README to TipTap JSON
    readme_doc = markdown_to_tiptap(readme_content)
    body_content = readme_doc.get("content", [])

    # Extract and add "What's New" section if CHANGELOG exists
    changelog_path = template_dir / "CHANGELOG.md"
    if changelog_path.exists():
        release_notes = extract_release_notes(changelog_path, version)
        if release_notes:
            # Add separator
            body_content.append({"type": "horizontalRule"})

            # Add "What's New" heading
            body_content.append(
                {
                    "type": "heading",
                    "attrs": {"level": 2},
                    "content": [{"type": "text", "text": "What's New in This Version"}],
                }
            )

            # Convert release notes to TipTap
            notes_doc = markdown_to_tiptap(release_notes)
            body_content.extend(notes_doc.get("content", []))

    # Add download section
    body_content.append({"type": "horizontalRule"})
    body_content.append(
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "Download Workflow"}],
        }
    )
    body_content.append(
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "marks": [{"type": "link", "attrs": {"href": download_url}}],
                    "text": f"Download {template_name} v{version}",
                }
            ],
        }
    )
    body_content.append(
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Click the link above to download the workflow.json.zip file. "},
                {
                    "type": "text",
                    "text": "Unzip the file and import workflow.json into your n8n instance.",
                },
            ],
        }
    )

    # Build final TipTap document
    body = {"type": "doc", "content": body_content}

    return {"title": title, "body": body, "slug": slug}


def extract_version_from_changelog(changelog_path: Path) -> str:
    """
    Extract latest version from CHANGELOG.md.

    Args:
        changelog_path: Path to CHANGELOG.md

    Returns:
        Version string (e.g., "1.0.0") or "1.0.0" if not found
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


def extract_release_notes(changelog_path: Path, version: str) -> Optional[str]:
    """
    Extract release notes for specific version from CHANGELOG.md.

    Args:
        changelog_path: Path to CHANGELOG.md
        version: Version to extract notes for

    Returns:
        Release notes content or None if not found
    """
    if not changelog_path.exists():
        return None

    with open(changelog_path, "r") as f:
        content = f.read()

    # Find section for this version
    # Match ## [1.0.0] or ## 1.0.0
    version_pattern = re.escape(version)
    section_start = re.search(
        rf"^##\s+\[?{version_pattern}\]?.*$", content, re.MULTILINE
    )

    if not section_start:
        return None

    # Extract content until next ## heading or end of file
    start_pos = section_start.end()
    next_section = re.search(r"^##\s+", content[start_pos:], re.MULTILINE)

    if next_section:
        end_pos = start_pos + next_section.start()
        notes = content[start_pos:end_pos].strip()
    else:
        notes = content[start_pos:].strip()

    return notes if notes else None


def generate_slug(template_name: str) -> str:
    """
    Generate URL slug from template name.

    Args:
        template_name: Template name (e.g., "daily-summary-email" or "category/template-name")

    Returns:
        Slug (lowercase, hyphenated, no slashes)
    """
    # Remove category prefix if present (e.g., "category/template" -> "template")
    name = template_name.split("/")[-1]

    # Convert to lowercase, replace underscores/spaces with hyphens
    slug = name.lower().replace("_", "-").replace(" ", "-")

    # Remove any non-alphanumeric characters except hyphens
    slug = re.sub(r"[^a-z0-9-]", "", slug)

    # Remove consecutive hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def _humanize_name(template_name: str) -> str:
    """
    Convert template name to human-readable title.

    Args:
        template_name: Template name (e.g., "daily-summary-email")

    Returns:
        Human-readable name (e.g., "Daily Summary Email")
    """
    # Remove category prefix if present
    name = template_name.split("/")[-1]

    # Replace hyphens and underscores with spaces
    name = name.replace("-", " ").replace("_", " ")

    # Title case
    return name.title()
