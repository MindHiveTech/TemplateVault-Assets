"""
Version Tracker

Manages template versions and release tracking in versions.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class VersionTracker:
    """Track template versions and releases"""

    def __init__(self, versions_file: Path):
        """
        Initialize version tracker.

        Args:
            versions_file: Path to versions.json file
        """
        self.versions_file = Path(versions_file)
        self.data = self._load()

    def _load(self) -> dict:
        """Load versions.json from disk"""
        if not self.versions_file.exists():
            return {"templates": {}}

        try:
            with open(self.versions_file, "r") as f:
                data = json.load(f)
                # Ensure structure
                if "templates" not in data:
                    data["templates"] = {}
                return data
        except (json.JSONDecodeError, OSError) as e:
            raise ValueError(f"Failed to load versions file: {e}") from e

    def get_current_version(self, template_name: str) -> Optional[str]:
        """
        Get current version for template.

        Args:
            template_name: Template identifier (e.g., "daily-summary-email")

        Returns:
            Current version string or None if template not found
        """
        template_data = self.data["templates"].get(template_name)
        if template_data:
            return template_data.get("current_version")
        return None

    def get_all_versions(self, template_name: str) -> list:
        """
        Get all versions for template.

        Args:
            template_name: Template identifier

        Returns:
            List of version objects (newest first)
        """
        template_data = self.data["templates"].get(template_name)
        if template_data:
            return template_data.get("versions", [])
        return []

    def add_version(
        self,
        template_name: str,
        version: str,
        github_tag: str,
        download_url: str,
        circle_post_id: str,
    ):
        """
        Record new version for template.

        Args:
            template_name: Template identifier
            version: Version string (e.g., "1.0.0")
            github_tag: GitHub release tag (e.g., "daily-summary-email-v1.0.0")
            download_url: Public download URL from GitHub release
            circle_post_id: Circle post ID
        """
        # Initialize template if it doesn't exist
        if template_name not in self.data["templates"]:
            self.data["templates"][template_name] = {
                "current_version": version,
                "versions": [],
            }

        # Update current version
        self.data["templates"][template_name]["current_version"] = version

        # Add version entry
        version_entry = {
            "version": version,
            "released_at": datetime.utcnow().isoformat() + "Z",
            "github_release_tag": github_tag,
            "download_url": download_url,
            "circle_post_id": circle_post_id,
        }

        # Prepend to versions list (newest first)
        versions = self.data["templates"][template_name]["versions"]

        # Remove existing entry for this version if it exists (update scenario)
        versions = [v for v in versions if v["version"] != version]

        # Add new entry at the beginning
        versions.insert(0, version_entry)

        self.data["templates"][template_name]["versions"] = versions

    def save(self):
        """Persist versions.json to disk"""
        # Ensure parent directory exists
        self.versions_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.versions_file, "w") as f:
                json.dump(self.data, f, indent=2)
        except OSError as e:
            raise ValueError(f"Failed to save versions file: {e}") from e

    def __repr__(self) -> str:
        template_count = len(self.data["templates"])
        return f"VersionTracker(templates={template_count}, file={self.versions_file})"
