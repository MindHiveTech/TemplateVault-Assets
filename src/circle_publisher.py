"""
Circle Publisher

Creates and updates Circle.so posts via Circle Admin API v2.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .content_builder import build_post_content

logger = logging.getLogger(__name__)


class CirclePublisher:
    """Circle API client for creating and updating posts"""

    def __init__(
        self,
        api_token: str,
        space_id: str,
        base_url: str = "https://app.circle.so/api/admin/v2",
        circle_index_file: Path = Path("data/circle_index.json"),
    ):
        """
        Initialize Circle API client.

        Args:
            api_token: Circle API v2 token
            space_id: Circle space ID
            base_url: Circle API base URL
            circle_index_file: Path to circle_index.json for tracking post IDs
        """
        self.api_token = api_token
        self.space_id = space_id
        self.base_url = base_url.rstrip("/")
        self.circle_index_file = Path(circle_index_file)

        # Load circle index (template_slug -> post_id mapping)
        self.circle_index = self._load_circle_index()

    def _load_circle_index(self) -> dict:
        """Load circle_index.json from disk"""
        if not self.circle_index_file.exists():
            return {}

        try:
            with open(self.circle_index_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Failed to load circle index, starting fresh: {e}")
            return {}

    def _save_circle_index(self):
        """Persist circle_index.json to disk"""
        self.circle_index_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.circle_index_file, "w") as f:
                json.dump(self.circle_index, f, indent=2)
        except OSError as e:
            logger.error(f"Failed to save circle index: {e}")

    def get_post_id(self, template_slug: str) -> Optional[str]:
        """
        Get Circle post ID for template slug.

        Args:
            template_slug: Template slug (e.g., "daily-summary-email")

        Returns:
            Circle post ID or None if not found
        """
        return self.circle_index.get(template_slug)

    def publish_template(
        self,
        template_name: str,
        version: str,
        download_url: str,
        template_dir: Path,
    ) -> str:
        """
        Create or update Circle post for template.

        Args:
            template_name: Template identifier
            version: Version string
            download_url: Public GitHub release download URL
            template_dir: Path to template directory

        Returns:
            Circle post ID

        Raises:
            Exception: If post creation/update fails
        """
        # Build post content
        post_data = build_post_content(
            template_dir=template_dir,
            template_name=template_name,
            version=version,
            download_url=download_url,
        )

        title = post_data["title"]
        body = post_data["body"]
        slug = post_data["slug"]

        # Check if post already exists
        existing_post_id = self.get_post_id(slug)

        if existing_post_id:
            logger.info(f"Updating existing post {existing_post_id} for {template_name}")
            post_id = self.update_post(existing_post_id, title, body)
        else:
            logger.info(f"Creating new post for {template_name}")
            post_id = self.create_post(title, body, slug)

            # Save slug -> post_id mapping
            self.circle_index[slug] = post_id
            self._save_circle_index()

        return post_id

    @retry(
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def create_post(self, title: str, body: dict, slug: str) -> str:
        """
        Create new Circle post.

        Args:
            title: Post title
            body: Post body (TipTap JSON)
            slug: Post slug

        Returns:
            Circle post ID

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.base_url}/posts"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "space_id": self.space_id,
            "name": title,
            "body": body,
            "slug": slug,
            "is_comments_enabled": True,
            "is_liking_enabled": True,
            "is_pinned": False,
            "status": "draft",  # Create as draft by default
        }

        logger.debug(f"Creating post: {title} (slug: {slug})")
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        if response.status_code in [200, 201]:
            response_data = response.json()
            # Handle nested response structure
            post = response_data.get("post", response_data)
            post_id = post.get("id")

            if not post_id:
                raise ValueError(f"No post ID in response: {response_data}")

            logger.info(f" Created post {post_id}: {title}")
            return str(post_id)
        else:
            error_msg = f"Failed to create post: {response.status_code} {response.text}"
            logger.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg, response=response)

    @retry(
        retry=retry_if_exception_type(requests.exceptions.RequestException),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def update_post(self, post_id: str, title: str, body: dict) -> str:
        """
        Update existing Circle post.

        Args:
            post_id: Circle post ID
            title: Post title
            body: Post body (TipTap JSON)

        Returns:
            Circle post ID

        Raises:
            requests.exceptions.RequestException: If API request fails
        """
        url = f"{self.base_url}/posts/{post_id}"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "name": title,
            "body": body,
            # Keep existing settings, just update content
        }

        logger.debug(f"Updating post {post_id}: {title}")
        response = requests.put(url, headers=headers, json=payload, timeout=30)

        if response.status_code in [200, 201]:
            logger.info(f" Updated post {post_id}: {title}")
            return str(post_id)
        else:
            error_msg = f"Failed to update post {post_id}: {response.status_code} {response.text}"
            logger.error(error_msg)
            raise requests.exceptions.HTTPError(error_msg, response=response)

    def __repr__(self) -> str:
        return f"CirclePublisher(space_id={self.space_id}, posts_tracked={len(self.circle_index)})"
