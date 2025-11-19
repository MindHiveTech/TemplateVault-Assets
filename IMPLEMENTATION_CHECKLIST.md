# Implementation Checklist: Public GitHub Releases

**Approach:** Public GitHub Repository
**Start Date:** 2025-11-19

## Phase 1: Repository Setup ✅

- [x] Create public repository `MindHiveTech/TemplateVault-Assets`
- [ ] Create directory structure
  - [ ] `src/` - Python modules
  - [ ] `scripts/` - CLI scripts
  - [ ] `data/` - JSON data files
  - [ ] `tests/` - Test files
  - [ ] `docs/` - Documentation
  - [ ] `.github/workflows/` - GitHub Actions
- [ ] Initialize Python project
  - [ ] Create `pyproject.toml`
  - [ ] Create `requirements.txt`
  - [ ] Create `README.md`
  - [ ] Create `.gitignore`
- [ ] Configure GitHub repository
  - [ ] Add secret: `CIRCLE_API_TOKEN`
  - [ ] Add secret: `CIRCLE_SPACE_ID`
  - [ ] Add secret: `TEMPLATEVAULT_PAT`
  - [ ] Add variable: `CIRCLE_BASE_URL` (optional)
- [ ] Initialize data files
  - [ ] Create `data/versions.json` (empty structure)
  - [ ] Create `data/circle_index.json` (empty object)

## Phase 2: Core Python Modules

### 2.1 Version Tracker (`src/version_tracker.py`)

- [ ] Implement `VersionTracker` class
  - [ ] `__init__(versions_file: Path)`
  - [ ] `get_current_version(template_name: str) -> Optional[str]`
  - [ ] `get_all_versions(template_name: str) -> list`
  - [ ] `add_version(template_name, version, github_tag, download_url, circle_post_id)`
  - [ ] `save()`
  - [ ] Error handling for malformed JSON
- [ ] Write unit tests
  - [ ] Test loading empty file
  - [ ] Test loading existing versions
  - [ ] Test adding new version
  - [ ] Test adding version to existing template
  - [ ] Test saving to file

### 2.2 Markdown to TipTap Converter (`src/markdown_to_tiptap.py`)

- [ ] Implement `markdown_to_tiptap(markdown: str) -> dict`
  - [ ] Parse markdown with `markdown-it-py`
  - [ ] Convert headings (h1-h6)
  - [ ] Convert paragraphs
  - [ ] Convert bold/italic marks
  - [ ] Convert links
  - [ ] Convert lists (ordered, unordered)
  - [ ] Convert code blocks
  - [ ] Convert blockquotes
- [ ] Write unit tests
  - [ ] Test heading conversion
  - [ ] Test paragraph with inline marks
  - [ ] Test links
  - [ ] Test lists
  - [ ] Test code blocks
  - [ ] Test complex nested structures

### 2.3 Content Builder (`src/content_builder.py`)

- [ ] Implement `build_post_content(template_dir, template_name, version, download_url) -> dict`
  - [ ] Read README.md
  - [ ] Convert README to TipTap JSON
  - [ ] Extract CHANGELOG for version
  - [ ] Build "What's New" section
  - [ ] Add download button node
  - [ ] Generate post title
  - [ ] Generate slug (lowercase, hyphenated)
- [ ] Implement helper functions
  - [ ] `extract_version_from_changelog(changelog_path: Path) -> str`
  - [ ] `extract_release_notes(changelog_path: Path, version: str) -> str`
  - [ ] `create_download_button(download_url: str) -> dict`
- [ ] Write unit tests
  - [ ] Test README conversion
  - [ ] Test CHANGELOG extraction
  - [ ] Test title generation
  - [ ] Test slug generation
  - [ ] Test download button creation
  - [ ] Test full post structure

### 2.4 Circle Publisher (`src/circle_publisher.py`)

- [ ] Implement `CirclePublisher` class
  - [ ] `__init__(api_token, space_id, base_url)`
  - [ ] `publish_template(template_name, version, download_url, template_dir) -> str`
  - [ ] `get_post_id(template_name: str) -> Optional[str]`
  - [ ] `create_post(title: str, body: dict, slug: str) -> str`
  - [ ] `update_post(post_id: str, title: str, body: dict) -> str`
  - [ ] `_load_circle_index() -> dict`
  - [ ] `_save_circle_index(index: dict)`
- [ ] Add retry logic with `tenacity`
  - [ ] Exponential backoff for 5xx errors
  - [ ] Max 3 retries
  - [ ] Timeout handling
- [ ] Write unit tests (mocked API)
  - [ ] Test post creation
  - [ ] Test post update
  - [ ] Test error handling (401, 404, 500)
  - [ ] Test retry behavior
  - [ ] Test circle_index loading/saving

## Phase 3: GitHub Actions Workflow

### 3.1 Main Publish Workflow (`.github/workflows/publish.yml`)

- [ ] Create workflow file
  - [ ] Trigger: `repository_dispatch`
  - [ ] Event type: `publish_templates`
- [ ] Implement workflow steps
  - [ ] Checkout Assets repo
  - [ ] Checkout TemplateVault repo (at specific SHA)
  - [ ] Set up Python 3.11
  - [ ] Install dependencies from `requirements.txt`
  - [ ] Parse `changed` payload (JSON array)
- [ ] Implement template processing loop
  - [ ] Extract template name from path
  - [ ] Extract version from CHANGELOG.md
  - [ ] Build tag: `{template-name}-v{version}`
  - [ ] Package workflow.json → zip
  - [ ] Create GitHub release
  - [ ] Upload zip to release
  - [ ] Build download URL
  - [ ] Call `scripts/publish_template.py`
- [ ] Implement post-processing
  - [ ] Commit updated `versions.json`
  - [ ] Commit updated `circle_index.json`
  - [ ] Push changes
- [ ] Add error handling
  - [ ] Fail workflow if any template fails
  - [ ] Log errors clearly
  - [ ] Upload artifacts for debugging

### 3.2 Supporting Scripts

- [ ] Create `scripts/extract_version.py`
  - [ ] Parse CHANGELOG.md
  - [ ] Extract version with regex: `^##\s+\[?(\d+\.\d+\.\d+)\]?`
  - [ ] Return default `1.0.0` if not found
  - [ ] Add CLI interface
- [ ] Create `scripts/publish_template.py`
  - [ ] Parse CLI arguments
  - [ ] Initialize `CirclePublisher`
  - [ ] Call `publish_template()`
  - [ ] Update `VersionTracker`
  - [ ] Print success message
  - [ ] Exit with error code on failure

## Phase 4: Testing

### 4.1 Unit Tests

- [ ] Set up pytest configuration
  - [ ] Create `pytest.ini` or `pyproject.toml` config
  - [ ] Configure coverage thresholds
- [ ] Run all unit tests
  - [ ] `tests/test_version_tracker.py`
  - [ ] `tests/test_content_builder.py`
  - [ ] `tests/test_markdown_to_tiptap.py`
  - [ ] `tests/test_circle_publisher.py`
- [ ] Verify coverage > 70%

### 4.2 Integration Tests

- [ ] Test end-to-end workflow
  - [ ] Create test template in TemplateVault
  - [ ] Trigger `repository_dispatch` manually
  - [ ] Verify GitHub release created
  - [ ] Verify zip file uploaded
  - [ ] Verify Circle post created
  - [ ] Verify download URL works (no auth)
  - [ ] Verify `versions.json` updated
  - [ ] Verify `circle_index.json` updated
- [ ] Test update scenario
  - [ ] Update test template (new version)
  - [ ] Trigger `repository_dispatch`
  - [ ] Verify new release created
  - [ ] Verify Circle post updated (not duplicated)
  - [ ] Verify versions.json has both versions

### 4.3 Manual Tests

- [ ] Download workflow.json via GitHub release URL
  - [ ] Verify no authentication required
  - [ ] Verify file is valid zip
  - [ ] Verify workflow.json inside is valid
- [ ] Check Circle post formatting
  - [ ] Title displays correctly
  - [ ] README content renders properly
  - [ ] "What's New" section appears
  - [ ] Download button works
- [ ] Test from community member perspective
  - [ ] Access Circle post without login
  - [ ] Click download button
  - [ ] Import workflow.json into n8n

## Phase 5: Migration

### 5.1 Prepare Migration

- [ ] Audit existing templates
  - [ ] List all templates in TemplateVault
  - [ ] Identify templates already published to Circle
  - [ ] Get current versions from CHANGELOG files
- [ ] Create migration script (`scripts/migrate_all_templates.py`)
  - [ ] Read TemplateVault-Publisher's circle_index.json
  - [ ] For each template:
    - [ ] Extract version
    - [ ] Create release in Assets repo
    - [ ] Update Circle post
    - [ ] Update versions.json
  - [ ] Add dry-run mode
  - [ ] Add progress logging

### 5.2 Run Migration

- [ ] Test migration script on 1-2 templates (dry-run)
- [ ] Verify test templates published correctly
- [ ] Run full migration for all templates
- [ ] Verify all Circle posts updated
- [ ] Verify all download URLs work

### 5.3 Update TemplateVault-Publisher

- [ ] Update `publisher/content_builder.py`
  - [ ] Change release URL to use `TemplateVault-Assets` repo
  - [ ] Update `release_url` construction
- [ ] Update `.github/workflows/publish.yml`
  - [ ] Remove release creation steps (now handled by Assets repo)
  - [ ] Keep only Circle posting logic
  - [ ] Or: deprecate and remove entirely (if Assets repo handles it all)
- [ ] Test updated workflow
  - [ ] Trigger publish for test template
  - [ ] Verify correct download URL in Circle post

## Phase 6: Documentation

### 6.1 User Guide (`docs/USER_GUIDE.md`)

- [ ] Write "How to Download Workflows" section
  - [ ] Navigate to Circle post
  - [ ] Click download button
  - [ ] Save zip file
- [ ] Write "How to Import into n8n" section
  - [ ] Unzip workflow.json
  - [ ] Import in n8n UI
  - [ ] Configure credentials
- [ ] Write "Troubleshooting" section
  - [ ] Download link not working
  - [ ] Zip file corrupted
  - [ ] Import fails in n8n

### 6.2 Operations Runbook (`docs/OPERATIONS_RUNBOOK.md`)

- [ ] Write "How Publishing Works" section
  - [ ] Diagram of flow
  - [ ] Explanation of each step
- [ ] Write "Manual Publishing" section
  - [ ] CLI usage for `scripts/publish_template.py`
  - [ ] When to use manual publishing
- [ ] Write "Troubleshooting" section
  - [ ] GitHub Actions failures
  - [ ] Circle API errors
  - [ ] How to check logs
  - [ ] How to retry failed publishes
- [ ] Write "Cleanup Old Releases" section
  - [ ] When to delete old releases
  - [ ] How to use cleanup script
  - [ ] Impact on existing downloads

### 6.3 README.md

- [ ] Write repository overview
  - [ ] Purpose
  - [ ] Architecture diagram
- [ ] Write setup instructions
  - [ ] Prerequisites
  - [ ] Installation steps
  - [ ] Configuration
- [ ] Write development guide
  - [ ] Local development setup
  - [ ] Running tests
  - [ ] Contributing guidelines

## Phase 7: Deployment

### 7.1 Pre-deployment Checks

- [ ] All tests passing
- [ ] GitHub secrets configured
- [ ] Data files initialized
- [ ] Documentation complete
- [ ] Migration script tested

### 7.2 Deployment

- [ ] Enable `repository_dispatch` in TemplateVault
  - [ ] Update workflow to send to Assets repo
  - [ ] Test dispatch payload
- [ ] Test first automated publish
  - [ ] Make change to test template in TemplateVault
  - [ ] Verify dispatch triggers
  - [ ] Verify release created
  - [ ] Verify Circle post updated
- [ ] Monitor for issues
  - [ ] Check GitHub Actions logs
  - [ ] Check Circle posts
  - [ ] Test download URLs

### 7.3 Post-deployment

- [ ] Announce to team
  - [ ] Document new workflow
  - [ ] Update team documentation
- [ ] Monitor community feedback
  - [ ] Check for download issues
  - [ ] Respond to questions
- [ ] Clean up old releases (optional)
  - [ ] Delete releases from TemplateVault repo
  - [ ] Update release notes to point to Assets repo

## Completion Criteria

- [ ] **All templates migrated** to public releases
- [ ] **Zero 404 errors** on Circle download links
- [ ] **Automated publishing** works end-to-end
- [ ] **Tests passing** with >70% coverage
- [ ] **Documentation complete** and accurate
- [ ] **Community members** can download without authentication

---

**Progress Tracking:**
- Total Tasks: ~120
- Completed: 1 (repository created)
- Remaining: ~119
- Estimated Time: 8-10 hours

**Last Updated:** 2025-11-19
