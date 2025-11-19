# TemplateVault-Assets: Design Specification
## Public GitHub Releases Approach

## Overview

**Repository:** `MindHiveTech/TemplateVault-Assets` (PUBLIC)
**Purpose:** Centralized release management and Circle.so post publishing for TemplateVault workflow files

### Core Responsibilities

1. **Public Release Hosting:** Create GitHub releases with workflow.json files (publicly downloadable)
2. **Circle Integration:** Publish/update posts in Circle.so with public download links
3. **Version Management:** Track template versions via GitHub releases
4. **Automated Publishing:** Trigger from TemplateVault on template changes

## Architecture

```
┌──────────────────┐
│  TemplateVault   │ (Private Repo - Template Development)
│   (Private)      │
└────────┬─────────┘
         │ repository_dispatch
         │ (sha, changed templates)
         ▼
┌─────────────────────────────────────────────────────────┐
│      TemplateVault-Assets (Public Repo - Releases)     │
│                                                          │
│  ┌────────────────────────────────────────────────┐   │
│  │   GitHub Actions Workflow                       │   │
│  │   1. Checkout TemplateVault @ commit SHA       │   │
│  │   2. Extract changed templates                  │   │
│  │   3. Package workflow.json → zip                │   │
│  │   4. Create GitHub release (public)             │   │
│  │   5. Upload zip to release                      │   │
│  │   6. Create/Update Circle post with DL link    │   │
│  │   7. Update versions.json                       │   │
│  └────────────────────────────────────────────────┘   │
│                                                          │
│  Python Modules:                                        │
│  - circle_publisher.py → Manage Circle.so posts        │
│  - version_tracker.py  → Track releases                │
│  - content_builder.py  → Build Circle post content     │
│                                                          │
│  Data:                                                  │
│  - data/versions.json  → Version index                 │
│  - data/circle_index.json → Circle post IDs            │
└──────────────┬────────────────────────────────────────┘
               │
               ▼
     ┌──────────────────────────────────┐
     │   Public GitHub Releases         │
     │   - {template}-v{version}        │
     │   - workflow.json.zip (public)   │
     │   - Download URL:                │
     │     github.com/.../download/...  │
     └─────────────┬────────────────────┘
                   │
                   ▼
          ┌──────────────────┐
          │   Circle.so       │
          │  (Community)      │
          │                   │
          │  Posts with       │
          │  public download  │
          │  links            │
          └──────────────────┘
```

## Key Benefits of Public Releases

✅ **Simple:** No AWS setup, no credentials management, no presigned URLs
✅ **Free:** GitHub provides unlimited bandwidth for public releases
✅ **Reliable:** GitHub's CDN is fast and highly available
✅ **Permanent URLs:** Download links never expire
✅ **No Authentication:** Anyone can download (perfect for community)
✅ **Transparent:** Community can see all releases and versions

## Component Design

### 1. GitHub Release Management

**Release Structure:**
```
Tag: {template-name}-v{version}
Example: daily-summary-email-v1.0.0

Assets:
- daily-summary-email-v1.0.0.zip (workflow.json packaged)

Release Notes:
- Template name and version
- Changelog from CHANGELOG.md
- Link to Circle post
```

**Download URL Format:**
```
https://github.com/MindHiveTech/TemplateVault-Assets/releases/download/{tag}/{filename}

Example:
https://github.com/MindHiveTech/TemplateVault-Assets/releases/download/daily-summary-email-v1.0.0/daily-summary-email-v1.0.0.zip
```

### 2. Circle Publisher (`src/circle_publisher.py`)

**Responsibilities:**
- Create new Circle posts for templates
- Update existing posts with new versions
- Manage post content (README, CHANGELOG, download links)
- Handle Circle API v2 TipTap format
- Track post IDs in `data/circle_index.json`

**API:**
```python
class CirclePublisher:
    def publish_template(
        self,
        template_name: str,
        version: str,
        download_url: str,  # GitHub release URL
        template_dir: Path
    ) -> str:
        """
        Create or update Circle post.
        Returns: Circle post ID
        """

    def get_post_id(self, template_name: str) -> Optional[str]:
        """Get Circle post ID for template"""
```

### 3. Version Tracker (`src/version_tracker.py`)

**Data Structure** (`data/versions.json`):
```json
{
  "templates": {
    "daily-summary-email": {
      "current_version": "1.1.0",
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

## GitHub Actions Workflows

### Main Publish Workflow (`.github/workflows/publish.yml`)

**Trigger:** `repository_dispatch` from TemplateVault

**Inputs:**
- `repo`: TemplateVault repository (`owner/name`)
- `sha`: Commit SHA (for deterministic checkout)
- `changed`: JSON array of changed template paths

**Steps:**
1. Checkout TemplateVault at specified SHA
2. For each changed template:
   - Extract version from CHANGELOG.md
   - Package workflow.json → zip (filename: `{template}-v{version}.zip`)
   - Create GitHub release (tag: `{template}-v{version}`)
   - Upload zip to release
   - Build Circle post content (README, CHANGELOG, download link)
   - Create/update Circle post
   - Update `versions.json` and `circle_index.json`
3. Commit updated JSON files

**Environment Variables:**
- `GITHUB_TOKEN`: Automatically provided by Actions (for creating releases)
- `CIRCLE_API_TOKEN`: Circle API token (from secrets)
- `CIRCLE_SPACE_ID`: Circle space ID (from secrets)
- `TEMPLATEVAULT_PAT`: GitHub PAT for checking out private TemplateVault repo

## Data Flow

### New Template Version Published

```
1. Developer merges changes to TemplateVault
   └─> TemplateVault workflow validates template

2. TemplateVault sends repository_dispatch to Assets repo
   └─> Payload: { repo, sha, changed: ["template-name"] }

3. Assets workflow triggered
   ├─> Checkout TemplateVault @ SHA (private repo)
   ├─> Extract template version from CHANGELOG.md
   ├─> Package workflow.json → {template}-v{version}.zip
   ├─> Create GitHub release in Assets repo (public)
   │   ├─> Tag: {template}-v{version}
   │   ├─> Title: "{Template Name} v{version}"
   │   └─> Asset: {template}-v{version}.zip
   ├─> Get public download URL from release
   │   └─> URL: https://github.com/.../releases/download/{tag}/{filename}
   ├─> Create/Update Circle post
   │   ├─> Title: "{Template Name} v{version}"
   │   ├─> Body: README + CHANGELOG + Download button
   │   └─> Download URL: GitHub release URL ✅
   ├─> Update versions.json
   └─> Commit changes

4. Community member visits Circle post
   ├─> Clicks "Download Workflow"
   └─> GitHub serves file (public, no auth needed) ✅
```

## Security

### Access Control

**TemplateVault-Assets Repository:**
- **Public** repository
- Anyone can download releases
- Only maintainers can create releases (via GitHub Actions)

**Download URLs:**
- Publicly accessible (no authentication)
- Never expire
- Served via GitHub CDN
- Anyone with URL can download

**Trade-off:**
- ❌ No member-only access control
- ✅ But: Simple, reliable, no maintenance
- ✅ Workflows are meant to be shared anyway

### Secrets Management

**GitHub Secrets:**
- `CIRCLE_API_TOKEN` - Circle API token
- `CIRCLE_SPACE_ID` - Circle space ID
- `TEMPLATEVAULT_PAT` - GitHub PAT for private TemplateVault checkout
- `GITHUB_TOKEN` - Auto-provided for release creation

## File Structure

```
TemplateVault-Assets/
├── .github/
│   └── workflows/
│       ├── publish.yml          # Main publish workflow
│       └── cleanup.yml          # Delete old releases
├── src/
│   ├── circle_publisher.py      # Circle API integration
│   ├── content_builder.py       # Build post content
│   ├── markdown_to_tiptap.py    # Markdown → TipTap JSON
│   ├── version_tracker.py       # Version management
│   └── __init__.py
├── scripts/
│   ├── publish_template.py      # CLI for manual publish
│   └── cleanup_old_releases.py  # Cleanup utility
├── data/
│   ├── versions.json            # Version index
│   └── circle_index.json        # Circle post mapping
├── tests/
│   ├── test_circle_publisher.py
│   ├── test_content_builder.py
│   └── test_version_tracker.py
├── docs/
│   ├── USER_GUIDE.md
│   └── OPERATIONS_RUNBOOK.md
├── DESIGN_SPEC.md              # This file
├── IMPLEMENTATION_PLAN.md      # Implementation plan
├── IMPLEMENTATION_CHECKLIST.md # Task checklist
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Error Handling

### Release Creation Failures
- Retry with exponential backoff (3 attempts)
- Check if release already exists (update if yes)
- Log error details
- Fail workflow with clear error message

### Circle API Failures
- Retry on 5xx errors
- Skip on 4xx errors (bad request)
- Log post ID for manual recovery
- Continue with other templates

### File Upload Failures
- Retry upload (3 attempts)
- Validate file exists before creating release
- Verify download URL works (HEAD request)

## Testing Strategy

### Unit Tests
- Circle publisher (mocked API)
- Content builder (markdown conversion)
- Version tracker (file I/O)

### Integration Tests
- End-to-end publish flow (test repo)
- Circle post creation (test space)
- Download verification

### Manual Tests
- Download workflow.json via GitHub release URL
- Verify Circle post displays correctly
- Confirm versions.json accuracy

## Migration Plan

### Phase 1: Setup (Day 1)
1. ✅ Create public repository
2. Create directory structure
3. Initialize Python project
4. Add GitHub secrets

### Phase 2: Implementation (Days 2-5)
1. Implement Circle publisher
2. Implement content builder
3. Implement version tracker
4. Create publish workflow
5. Write tests

### Phase 3: Migration (Days 6-7)
1. Publish POC templates (3 templates)
2. Verify downloads work
3. Publish all templates
4. Update all Circle posts
5. Monitor for issues

### Phase 4: Cleanup (Day 8)
1. Delete old releases from private TemplateVault repo
2. Update TemplateVault-Publisher (stop creating releases)
3. Document operations

## Cost Analysis

**GitHub:**
- ✅ Free public repositories
- ✅ Free release hosting
- ✅ Free bandwidth for public releases
- ✅ Free GitHub Actions (2,000 minutes/month)

**Total: $0/month** (completely free!)

## Comparison to AWS S3

| Feature | Public GitHub Releases | AWS S3 |
|---------|----------------------|--------|
| **Cost** | $0/month | ~$0/month |
| **Setup Complexity** | Low (no AWS account needed) | High (AWS account, IAM, S3 config) |
| **URL Expiration** | Never expires | 30-day expiry, needs refresh |
| **Access Control** | Public (anyone can download) | Time-limited (30 days) |
| **Maintenance** | None | URL refresh weekly |
| **Reliability** | GitHub CDN (99.99%+) | AWS S3 (99.99%+) |
| **Speed** | Fast (GitHub CDN) | Fast (AWS CDN) |

**Winner:** Public GitHub Releases (simpler, no maintenance, free, permanent URLs)

## Success Metrics

**MVP Success:**
- ✅ All templates published to public releases
- ✅ All Circle posts have working download links
- ✅ Zero 404 download errors
- ✅ Automated publishing works
- ✅ Cost: $0/month

**Long-term Success:**
- ✅ 99.9% download availability
- ✅ < 1 second median download time
- ✅ Community satisfaction with downloads
- ✅ Maintainable by any team member

---

**Document Version:** 2.0 (Public Releases Approach)
**Last Updated:** 2025-11-19
**Status:** APPROVED
