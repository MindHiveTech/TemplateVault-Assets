# TemplateVault-Assets

**Public release repository for TemplateVault workflow files**

This repository hosts public GitHub releases for TemplateVault n8n workflow templates. It provides free, permanent download URLs for workflow.json files that are linked from Circle.so community posts.

## Architecture

```
TemplateVault (Private) 
    ↓ repository_dispatch
TemplateVault-Assets (Public)
    ├─> Create GitHub releases
    ├─> Upload workflow.json.zip
    ├─> Publish to Circle.so
    └─> Track versions
```

## Key Features

✅ **Public Downloads** - No authentication required  
✅ **Free Hosting** - GitHub CDN, unlimited bandwidth  
✅ **Permanent URLs** - Download links never expire  
✅ **Version Tracking** - All template versions recorded  
✅ **Automated Publishing** - Triggered from TemplateVault changes  

## Download URL Format

```
https://github.com/MindHiveTech/TemplateVault-Assets/releases/download/{template-name}-v{version}/{template-name}-v{version}.zip
```

Example:
```
https://github.com/MindHiveTech/TemplateVault-Assets/releases/download/daily-summary-email-v1.0.0/daily-summary-email-v1.0.0.zip
```

## How It Works

1. **TemplateVault** (private repo) sends `repository_dispatch` event when templates change
2. **GitHub Actions** in this repo:
   - Checks out TemplateVault at specific commit SHA
   - Packages workflow.json files
   - Creates GitHub releases with assets
   - Publishes/updates Circle.so posts
   - Tracks versions in `data/versions.json`
3. **Community members** download workflows via Circle posts (public, no auth)

## Repository Structure

```
TemplateVault-Assets/
├── src/                      # Python modules
│   ├── circle_publisher.py   # Circle API integration
│   ├── content_builder.py    # Build post content
│   ├── version_tracker.py    # Version management
│   └── markdown_to_tiptap.py # Markdown → TipTap JSON
├── scripts/                  # CLI scripts
│   ├── publish_template.py   # Manual publish
│   └── extract_version.py    # Version extraction
├── data/                     # State tracking
│   ├── versions.json         # Version index
│   └── circle_index.json     # Circle post IDs
├── tests/                    # Unit tests
├── docs/                     # Documentation
└── .github/workflows/        # Automation
    └── publish.yml           # Main publish workflow
```

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/MindHiveTech/TemplateVault-Assets.git
cd TemplateVault-Assets

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv/Scripts/activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_circle_publisher.py
```

### Manual Publishing

```bash
export CIRCLE_API_TOKEN="your-token"
export CIRCLE_SPACE_ID="your-space-id"

python scripts/publish_template.py \
  --template-dir /path/to/template \
  --template-name my-workflow \
  --version 1.0.0 \
  --download-url "https://github.com/..."
```

## Configuration

### GitHub Secrets (required)

- `CIRCLE_API_TOKEN` - Circle API v2 token
- `CIRCLE_SPACE_ID` - Circle space ID
- `TEMPLATEVAULT_PAT` - GitHub PAT for private repo access

### GitHub Variables (optional)

- `CIRCLE_BASE_URL` - Circle API base URL (default: `https://app.circle.so/api/admin/v2`)

## Documentation

- [Design Specification](DESIGN_SPEC.md) - Architecture and component design
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed implementation steps
- [Implementation Checklist](IMPLEMENTATION_CHECKLIST.md) - Task tracking
- [User Guide](docs/USER_GUIDE.md) - How to download and use workflows
- [Operations Runbook](docs/OPERATIONS_RUNBOOK.md) - Troubleshooting and maintenance

## License

MIT License - See LICENSE file for details

## Contact

Questions or issues? Contact the MindHive team or open an issue in this repository.
