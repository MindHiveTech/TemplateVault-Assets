#!/usr/bin/env python3
"""
Publish Template to Circle

CLI for manually publishing a template to Circle.so.
Used by GitHub Actions and for manual intervention.

Usage:
    python scripts/publish_template.py \
        --template-dir /path/to/template \
        --template-name my-workflow \
        --version 1.0.0 \
        --download-url "https://github.com/.../releases/download/..."

Environment Variables:
    CIRCLE_API_TOKEN - Circle API v2 token (required)
    CIRCLE_SPACE_ID - Circle space ID (required)
    CIRCLE_BASE_URL - Circle API base URL (optional, default: https://app.circle.so/api/admin/v2)
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.circle_publisher import CirclePublisher
from src.version_tracker import VersionTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Publish template to Circle.so")
    parser.add_argument(
        "--template-dir",
        type=Path,
        required=True,
        help="Path to template directory (must contain README.md)",
    )
    parser.add_argument(
        "--template-name",
        required=True,
        help="Template identifier (e.g., 'daily-summary-email')",
    )
    parser.add_argument(
        "--version",
        required=True,
        help="Version string (e.g., '1.0.0')",
    )
    parser.add_argument(
        "--download-url",
        required=True,
        help="Public GitHub release download URL",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate environment
    api_token = os.getenv("CIRCLE_API_TOKEN")
    space_id = os.getenv("CIRCLE_SPACE_ID")
    base_url = os.getenv("CIRCLE_BASE_URL", "https://app.circle.so/api/admin/v2")

    if not api_token:
        logger.error("Error: CIRCLE_API_TOKEN environment variable not set")
        sys.exit(1)

    if not space_id:
        logger.error("Error: CIRCLE_SPACE_ID environment variable not set")
        sys.exit(1)

    # Validate template directory
    if not args.template_dir.exists():
        logger.error(f"Error: Template directory not found: {args.template_dir}")
        sys.exit(1)

    readme_path = args.template_dir / "README.md"
    if not readme_path.exists():
        logger.error(f"Error: README.md not found in {args.template_dir}")
        sys.exit(1)

    try:
        # Initialize publisher
        logger.info(f"Initializing Circle publisher (space: {space_id})")
        publisher = CirclePublisher(
            api_token=api_token,
            space_id=space_id,
            base_url=base_url,
        )

        # Publish template
        logger.info(f"Publishing {args.template_name} v{args.version}...")
        post_id = publisher.publish_template(
            template_name=args.template_name,
            version=args.version,
            download_url=args.download_url,
            template_dir=args.template_dir,
        )

        # Update version tracker
        logger.info("Updating version tracker...")
        tracker = VersionTracker(Path("data/versions.json"))
        tracker.add_version(
            template_name=args.template_name,
            version=args.version,
            github_tag=f"{args.template_name}-v{args.version}",
            download_url=args.download_url,
            circle_post_id=post_id,
        )
        tracker.save()

        logger.info(f" Successfully published {args.template_name} v{args.version}")
        logger.info(f"   Circle Post ID: {post_id}")
        logger.info(f"   Download URL: {args.download_url}")

    except Exception as e:
        logger.error(f"L Failed to publish template: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
