# Implementation Plan: Public GitHub Releases

**Version:** 2.0
**Approach:** Public GitHub Repository for Release Hosting
**Date:** 2025-11-19

## Overview

Implement automated publishing of TemplateVault workflow files via **public GitHub releases** in a dedicated `TemplateVault-Assets` repository. This eliminates authentication issues and provides free, permanent download URLs.

## Architecture Summary

```
TemplateVault (Private)
    ↓ repository_dispatch (sha, changed templates)
TemplateVault-Assets (Public)
    ├─> Checkout TemplateVault @ SHA
    ├─> Extract workflow.json from templates
    ├─> Create GitHub releases (public)
    ├─> Upload workflow.json.zip to releases
    ├─> Publish/update Circle posts with download links
    └─> Track versions in versions.json
```

## Phase 1: Repository Setup (30 minutes)

### 1.1 Repository Structure

```bash
cd /Users/b/src/mindhive/TemplateVault-Assets

# Create directory structure
mkdir -p src scripts data tests docs .github/workflows

# Create Python modules
touch src/__init__.py
touch src/circle_publisher.py
touch src/content_builder.py
touch src/version_tracker.py
touch src/markdown_to_tiptap.py

# Create scripts
touch scripts/publish_template.py
touch scripts/cleanup_old_releases.py

# Create data files
echo '{"templates":{}}' > data/versions.json
echo '{}' > data/circle_index.json

# Create test structure
touch tests/__init__.py
touch tests/test_circle_publisher.py
touch tests/test_content_builder.py
touch tests/test_version_tracker.py

# Create Python project files
touch pyproject.toml
touch requirements.txt
touch README.md
```

### 1.2 GitHub Repository Configuration

**Secrets (required):**
- `CIRCLE_API_TOKEN` - Circle API token for creating/updating posts
- `CIRCLE_SPACE_ID` - Circle space ID
- `TEMPLATEVAULT_PAT` - GitHub PAT with access to private TemplateVault repo

**Variables (optional):**
- `CIRCLE_BASE_URL` - Circle API base URL (default: `https://app.circle.so/api/admin/v2`)

### 1.3 Python Dependencies

```toml
# pyproject.toml
[project]
name = "templatevault-assets"
version = "1.0.0"
description = "Public release management for TemplateVault workflows"
requires-python = ">=3.9"

dependencies = [
    "requests>=2.31.0",
    "tenacity>=8.2.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.1.0",
]
```

## Phase 2: Core Python Modules (2-3 hours)

### 2.1 Version Tracker (`src/version_tracker.py`)

**Purpose:** Manage template versions and release tracking

**Key Functions:**
```python
class VersionTracker:
    def __init__(self, versions_file: Path):
        """Load versions.json"""

    def get_current_version(self, template_name: str) -> Optional[str]:
        """Get current version for template"""

    def add_version(
        self,
        template_name: str,
        version: str,
        github_tag: str,
        download_url: str,
        circle_post_id: str
    ):
        """Record new version"""

    def save(self):
        """Persist versions.json to disk"""
```

**Data Structure:**
```json
{
  "templates": {
    "daily-summary-email": {
      "current_version": "1.0.0",
      "versions": [
        {
          "version": "1.0.0",
          "released_at": "2025-11-19T20:32:18Z",
          "github_release_tag": "daily-summary-email-v1.0.0",
          "download_url": "https://github.com/MindHiveTech/TemplateVault-Assets/releases/download/daily-summary-email-v1.0.0/daily-summary-email-v1.0.0.zip",
          "circle_post_id": "27050123"
        }
      ]
    }
  }
}
```

### 2.2 Content Builder (`src/content_builder.py`)

**Purpose:** Build Circle post content from template files

**Key Functions:**
```python
def build_post_content(
    template_dir: Path,
    template_name: str,
    version: str,
    download_url: str
) -> dict:
    """
    Build Circle post with TipTap JSON content.

    Returns:
        {
            "title": str,
            "body": dict,  # TipTap JSON
            "slug": str
        }
    """
    # 1. Read README.md and convert to TipTap JSON
    # 2. Extract CHANGELOG for version
    # 3. Build download button
    # 4. Return TipTap structure
```

**Content Structure:**
```
1. Title: {Template Name} v{version}
2. README content (converted from Markdown)
3. What's New section (from CHANGELOG)
4. Download button linking to GitHub release
```

### 2.3 Markdown to TipTap Converter (`src/markdown_to_tiptap.py`)

**Purpose:** Convert Markdown to Circle API v2 TipTap JSON format

**Key Functions:**
```python
def markdown_to_tiptap(markdown: str) -> dict:
    """
    Convert markdown to TipTap JSON format.

    Supports:
    - Headings (h1-h6)
    - Paragraphs
    - Bold, italic, links
    - Lists (ordered, unordered)
    - Code blocks
    - Blockquotes
    """
```

**Implementation:**
- Use `markdown-it-py` for parsing
- Map markdown AST to TipTap nodes
- Handle inline marks (bold, italic, links)

### 2.4 Circle Publisher (`src/circle_publisher.py`)

**Purpose:** Create and update Circle posts

**Key Functions:**
```python
class CirclePublisher:
    def __init__(
        self,
        api_token: str,
        space_id: str,
        base_url: str = "https://app.circle.so/api/admin/v2"
    ):
        """Initialize Circle API client"""

    def publish_template(
        self,
        template_name: str,
        version: str,
        download_url: str,
        template_dir: Path
    ) -> str:
        """
        Create or update Circle post for template.

        Returns: Circle post ID
        """
        # 1. Build post content via content_builder
        # 2. Check if post exists (via circle_index.json)
        # 3. Create or update post
        # 4. Return post ID

    def get_post_id(self, template_name: str) -> Optional[str]:
        """Get Circle post ID from index"""

    def create_post(self, title: str, body: dict, slug: str) -> str:
        """Create new Circle post"""

    def update_post(self, post_id: str, title: str, body: dict) -> str:
        """Update existing Circle post"""
```

**Circle Index Structure:**
```json
{
  "daily-summary-email": "27050123",
  "notion-backup": "27050456"
}
```

## Phase 3: GitHub Actions Workflow (1-2 hours)

### 3.1 Publish Workflow (`.github/workflows/publish.yml`)

**Trigger:** `repository_dispatch` from TemplateVault

**Payload:**
```json
{
  "repo": "MindHiveTech/TemplateVault",
  "sha": "abc123def456",
  "changed": ["category/template-name", "another-template"]
}
```

**Workflow Steps:**

```yaml
name: Publish Templates to Circle

on:
  repository_dispatch:
    types: [publish_templates]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Assets repo
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Checkout TemplateVault repo
        uses: actions/checkout@v4
        with:
          repository: ${{ github.event.client_payload.repo }}
          ref: ${{ github.event.client_payload.sha }}
          token: ${{ secrets.TEMPLATEVAULT_PAT }}
          path: templatevault

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Process each changed template
        run: |
          # For each template in changed array:
          for template in $(echo '${{ toJson(github.event.client_payload.changed) }}' | jq -r '.[]'); do
            template_name=$(basename "$template")
            template_path="templatevault/templates/$template"

            # Extract version from CHANGELOG.md
            version=$(python scripts/extract_version.py "$template_path/CHANGELOG.md")
            tag="${template_name}-v${version}"

            # Package workflow.json
            zip_file="${template_name}-v${version}.zip"
            cd "$template_path"
            zip "$zip_file" workflow.json
            cd -

            # Create GitHub release in Assets repo
            gh release create "$tag" \
              --title "$template_name v$version" \
              --notes "Workflow file for $template_name v$version" \
              --repo "$GITHUB_REPOSITORY"

            # Upload zip to release
            gh release upload "$tag" "$template_path/$zip_file" \
              --repo "$GITHUB_REPOSITORY" \
              --clobber

            # Build download URL
            download_url="https://github.com/$GITHUB_REPOSITORY/releases/download/$tag/$zip_file"

            # Publish to Circle
            python scripts/publish_template.py \
              --template-dir "$template_path" \
              --template-name "$template_name" \
              --version "$version" \
              --download-url "$download_url"
          done
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          CIRCLE_API_TOKEN: ${{ secrets.CIRCLE_API_TOKEN }}
          CIRCLE_SPACE_ID: ${{ secrets.CIRCLE_SPACE_ID }}

      - name: Commit updated JSON files
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add data/versions.json data/circle_index.json
          git commit -m "Update versions and Circle index" || echo "No changes"
          git push
```

### 3.2 Supporting Scripts

**`scripts/extract_version.py`:**
```python
#!/usr/bin/env python3
"""Extract version from CHANGELOG.md"""
import sys
import re
from pathlib import Path

def extract_version(changelog_path: Path) -> str:
    """Extract latest version from CHANGELOG.md"""
    with open(changelog_path) as f:
        content = f.read()

    # Match ## [X.Y.Z] or ## X.Y.Z
    match = re.search(r'^##\s+\[?(\d+\.\d+\.\d+)\]?', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "1.0.0"  # Default

if __name__ == "__main__":
    print(extract_version(Path(sys.argv[1])))
```

**`scripts/publish_template.py`:**
```python
#!/usr/bin/env python3
"""CLI for publishing template to Circle"""
import argparse
from pathlib import Path
from src.circle_publisher import CirclePublisher
from src.version_tracker import VersionTracker

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-dir", type=Path, required=True)
    parser.add_argument("--template-name", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--download-url", required=True)
    args = parser.parse_args()

    # Initialize publisher
    publisher = CirclePublisher(
        api_token=os.getenv("CIRCLE_API_TOKEN"),
        space_id=os.getenv("CIRCLE_SPACE_ID")
    )

    # Publish template
    post_id = publisher.publish_template(
        template_name=args.template_name,
        version=args.version,
        download_url=args.download_url,
        template_dir=args.template_dir
    )

    # Update version tracker
    tracker = VersionTracker(Path("data/versions.json"))
    tracker.add_version(
        template_name=args.template_name,
        version=args.version,
        github_tag=f"{args.template_name}-v{args.version}",
        download_url=args.download_url,
        circle_post_id=post_id
    )
    tracker.save()

    print(f"✅ Published {args.template_name} v{args.version}")
    print(f"   Circle Post ID: {post_id}")

if __name__ == "__main__":
    main()
```

## Phase 4: Testing (1-2 hours)

### 4.1 Unit Tests

**`tests/test_version_tracker.py`:**
- Test loading/saving versions.json
- Test adding new versions
- Test getting current version

**`tests/test_content_builder.py`:**
- Test README parsing
- Test CHANGELOG extraction
- Test TipTap JSON generation
- Test download button creation

**`tests/test_circle_publisher.py`:**
- Test post creation (mocked API)
- Test post updates (mocked API)
- Test error handling

### 4.2 Integration Tests

**Manual Test Workflow:**
1. Trigger `repository_dispatch` from TemplateVault
2. Verify GitHub release created with correct tag
3. Verify zip file uploaded to release
4. Verify Circle post created/updated
5. Verify download URL works (no authentication)
6. Verify versions.json updated

## Phase 5: Migration (1-2 hours)

### 5.1 Migrate Existing Templates

**Strategy:**
1. Identify all templates currently published to Circle (from TemplateVault-Publisher's circle_index.json)
2. For each template:
   - Extract current version from CHANGELOG.md
   - Package workflow.json
   - Create GitHub release in Assets repo
   - Update Circle post with new download URL
   - Record in versions.json

**Migration Script (`scripts/migrate_all_templates.py`):**
```python
#!/usr/bin/env python3
"""Migrate all existing templates to public releases"""

def main():
    # 1. Read TemplateVault-Publisher's circle_index.json
    # 2. For each template:
    #    - Checkout TemplateVault
    #    - Extract version
    #    - Create release in Assets repo
    #    - Update Circle post
    #    - Update versions.json
    pass
```

### 5.2 Update TemplateVault Publisher

**File:** `TemplateVault-Publisher/publisher/content_builder.py`

**Change download URL construction:**
```python
# BEFORE:
release_url = f"https://github.com/{repo}/releases/download/{name}-v{version}/{name}-v{version}.zip"

# AFTER:
public_repo = "MindHiveTech/TemplateVault-Assets"
release_url = f"https://github.com/{public_repo}/releases/download/{name}-v{version}/{name}-v{version}.zip"
```

**Update workflow:** `TemplateVault-Publisher/.github/workflows/publish.yml`

Remove release creation steps (handled by Assets repo now).

## Phase 6: Documentation (30 minutes)

### 6.1 User Guide (`docs/USER_GUIDE.md`)

**Content:**
- How to download workflows from Circle
- How to import workflow.json into n8n
- Troubleshooting download issues

### 6.2 Operations Runbook (`docs/OPERATIONS_RUNBOOK.md`)

**Content:**
- How publishing works
- How to manually publish a template
- How to delete old releases
- How to troubleshoot Circle API errors
- How to update Circle post manually

### 6.3 README.md

**Content:**
- Repository purpose
- Architecture overview
- Setup instructions
- Development guide

## Timeline

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Repository setup | 30m | None |
| 2 | Version tracker | 30m | Phase 1 |
| 2 | Content builder | 1h | Phase 1 |
| 2 | Markdown to TipTap | 30m | Phase 1 |
| 2 | Circle publisher | 1h | Phase 1, 2 |
| 3 | GitHub Actions | 1-2h | Phase 2 |
| 3 | Supporting scripts | 30m | Phase 2 |
| 4 | Unit tests | 1h | Phase 2 |
| 4 | Integration tests | 1h | Phase 3 |
| 5 | Migration script | 1h | Phase 3 |
| 5 | Run migration | 30m | Phase 5 |
| 6 | Documentation | 30m | Phase 5 |

**Total: 8-10 hours**

## Success Criteria

**MVP Success:**
- ✅ GitHub Actions workflow triggers from TemplateVault
- ✅ Public releases created with workflow.json.zip
- ✅ Circle posts created/updated with public download links
- ✅ Download URLs work without authentication
- ✅ versions.json tracks all published versions
- ✅ circle_index.json maps templates to post IDs

**Long-term Success:**
- ✅ All existing templates migrated
- ✅ Zero download errors reported by community
- ✅ Automated publishing reliable
- ✅ No manual intervention needed for routine publishes

## Rollback Plan

If issues arise:

1. **Emergency fix:** Manually update Circle posts with correct download URLs
2. **Revert to manual publishing:** Use `scripts/publish_template.py` CLI
3. **Investigate logs:** Check GitHub Actions logs for errors
4. **Test locally:** Run publish script locally with test data

## Future Enhancements

- **Image hosting:** Upload screenshots/diagrams to Circle Direct Upload API
- **Auto-tagging:** LLM-generated tags for templates
- **Analytics:** Track download counts via GitHub API
- **Webhook notifications:** Notify Discord/Slack when templates published
- **Version comparison:** Show diff between versions in Circle posts

---

**Document Version:** 2.0 (Public Releases)
**Last Updated:** 2025-11-19
**Status:** READY FOR IMPLEMENTATION
