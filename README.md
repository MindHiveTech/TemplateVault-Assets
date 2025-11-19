# TemplateVault-Assets

**Public release repository for TemplateVault workflow files**

This repository hosts public GitHub releases for TemplateVault n8n workflow templates. It provides free, permanent download URLs for workflow.json files.

## Architecture

```
TemplateVault (Private)
    ↓ repository_dispatch
TemplateVault-Assets (Public)
    ├─> Checkout TemplateVault at specific SHA
    ├─> Package workflow.json → zip
    ├─> Create GitHub releases (public)
    └─> Upload workflow.json.zip to releases
```

## Key Features

✅ **Public Downloads** - No authentication required
✅ **Free Hosting** - GitHub CDN, unlimited bandwidth
✅ **Permanent URLs** - Download links never expire
✅ **Automated Publishing** - Triggered from TemplateVault changes
✅ **Simple** - Pure bash scripts, no external dependencies

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
   - Packages workflow.json files into zip archives
   - Creates GitHub releases with version tags
   - Uploads zip files as release assets
3. **Download URLs** are public and accessible to anyone

## Repository Structure

```
TemplateVault-Assets/
├── .github/workflows/
│   └── publish.yml           # Automated release workflow
├── scripts/
│   ├── extract_version.py    # Extract version from CHANGELOG
│   └── cleanup_old_releases.py  # Cleanup utility
├── DESIGN_SPEC.md           # Architecture documentation
├── IMPLEMENTATION_PLAN.md   # Implementation guide
└── README.md                # This file
```

## Configuration

### GitHub Secrets (required)

- `TEMPLATEVAULT_PAT` - GitHub PAT for accessing private TemplateVault repo
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

### Workflow Inputs

The workflow accepts `repository_dispatch` events with:
- `repo` - TemplateVault repository (format: `owner/name`)
- `sha` - Commit SHA to checkout
- `changed` - JSON array of changed template paths

## Documentation

- [Design Specification](DESIGN_SPEC.md) - Architecture and component design
- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Detailed implementation steps
- [Implementation Checklist](IMPLEMENTATION_CHECKLIST.md) - Task tracking

## License

MIT License - See LICENSE file for details

## Contact

Questions or issues? Contact the MindHive team or open an issue in this repository.
