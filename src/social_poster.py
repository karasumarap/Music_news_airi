"""
Social posting helpers for X (Twitter) and TikTok.

Both clients are optional and only run when the required environment
variables are provided. They are designed to fail softly so Part 2 can
finish even if social posting is not configured.

Environment variables:
- X_CONSUMER_KEY
- X_CONSUMER_SECRET
- X_ACCESS_TOKEN
- X_ACCESS_TOKEN_SECRET
- TIKTOK_ACCESS_TOKEN      # OAuth access token issued by TikTok
- TIKTOK_OPEN_ID           # open_id that received the token
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

import requests

try:
    import tweepy

    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

logger = logging.getLogger(__name__)


def _truncate(text: str, limit: int) -> str:
    """Trim text to a safe length for posting."""
    if len(text) <= limit:
        return text
    if limit <= 3:
        return text[:limit]
    return text[: limit - 3] + "..."


class XPoster:
    """Post tweets to X using OAuth1.1 (media upload supported)."""

    def __init__(
        self,
        consumer_key: Optional[str],
        consumer_secret: Optional[str],
        access_token: Optional[str],
        access_token_secret: Optional[str],
        character_limit: int = 280,
    ) -> None:
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.character_limit = character_limit

    @classmethod
    def from_env(cls) -> "XPoster":
        return cls(
            consumer_key=os.getenv("X_CONSUMER_KEY"),
            consumer_secret=os.getenv("X_CONSUMER_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
        )

    def is_configured(self) -> bool:
        return all([
            TWEEPY_AVAILABLE,
            self.consumer_key,
            self.consumer_secret,
            self.access_token,
            self.access_token_secret,
        ])

    def post(self, text: str, media_path: Optional[Path] = None) -> Optional[Dict]:
        if not self.is_configured():
            logger.info("Skip X post: env vars or tweepy not configured")
            return None

        safe_text = _truncate(text.strip(), self.character_limit)
        media_ids: list[str] = []

        try:
            auth = tweepy.OAuth1UserHandler(
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
            )
            api = tweepy.API(auth)

            # Upload media first (video friendly)
            if media_path:
                media_path = Path(media_path)
                if media_path.exists():
                    logger.info(f"Uploading media to X: {media_path.name}")
                    is_video = media_path.suffix.lower() in {".mp4", ".mov", ".m4v", ".avi"}
                    upload_kwargs = {"filename": str(media_path)}
                    if is_video:
                        upload_kwargs.update({"chunked": True, "media_category": "tweet_video"})
                    media = api.media_upload(**upload_kwargs)
                    media_ids.append(media.media_id_string)
                else:
                    logger.warning(f"X media for posting not found: {media_path}")

            logger.info("Posting to X...")
            status = api.update_status(status=safe_text, media_ids=media_ids or None)
            post_url = f"https://x.com/{status.user.screen_name}/status/{status.id_str}"
            logger.info(f"X post complete: {post_url}")

            return {
                "id": status.id_str,
                "url": post_url,
                "text": safe_text,
            }
        except Exception as exc:  # tweepy raises many custom exceptions
            logger.error(f"X posting failed: {exc}", exc_info=True)
            return None


class TikTokPoster:
    """Upload and publish a short video to TikTok using the Open API v2.

    Note: TikTok's APIs require a TikTok for Developers app, Business
    account permissions, and user-granted `video.upload` / `video.publish`
    scopes. The code here follows the documented two-step upload + publish
    flow and will no-op if credentials are missing.
    """

    UPLOAD_ENDPOINT = "https://open.tiktokapis.com/v2/upload/video/"
    PUBLISH_ENDPOINT = "https://open.tiktokapis.com/v2/post/publish/"

    def __init__(
        self,
        access_token: Optional[str],
        open_id: Optional[str],
        caption_limit: int = 150,
    ) -> None:
        self.access_token = access_token
        self.open_id = open_id
        self.caption_limit = caption_limit

    @classmethod
    def from_env(cls) -> "TikTokPoster":
        return cls(
            access_token=os.getenv("TIKTOK_ACCESS_TOKEN"),
            open_id=os.getenv("TIKTOK_OPEN_ID"),
        )

    def is_configured(self) -> bool:
        return bool(self.access_token and self.open_id)

    def post(self, video_path: Path, caption: str) -> Optional[Dict]:
        if not self.is_configured():
            logger.info("Skip TikTok post: env vars not configured")
            return None

        video_path = Path(video_path)
        if not video_path.exists():
            logger.error(f"TikTok video for posting not found: {video_path}")
            return None

        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }

        try:
            logger.info("TikTok: requesting upload URL")
            upload_resp = requests.post(
                self.UPLOAD_ENDPOINT,
                headers=headers,
                json={"open_id": self.open_id},
                timeout=30,
            )
            upload_resp.raise_for_status()
            upload_data = upload_resp.json().get("data", {})
            upload_url = upload_data.get("upload_url")
            upload_id = upload_data.get("upload_id")

            if not upload_url or not upload_id:
                logger.error(f"TikTok upload URL request failed: {upload_resp.text}")
                return None

            logger.info("TikTok: uploading video bytes...")
            with open(video_path, "rb") as file_handle:
                binary_resp = requests.put(
                    upload_url,
                    data=file_handle,
                    headers={"Content-Type": "video/mp4"},
                    timeout=300,
                )
                binary_resp.raise_for_status()

            logger.info("TikTok: publishing post metadata")
            publish_payload = {
                "open_id": self.open_id,
                "post_info": {
                    "title": _truncate(caption.strip(), self.caption_limit),
                },
                "source_info": {
                    "source": "UPLOAD",
                    "upload_id": upload_id,
                },
            }

            publish_resp = requests.post(
                self.PUBLISH_ENDPOINT,
                headers=headers,
                json=publish_payload,
                timeout=30,
            )
            publish_resp.raise_for_status()
            publish_data = publish_resp.json().get("data", {})

            video_id = publish_data.get("video_id") or publish_data.get("id")
            share_url = publish_data.get("share_url")

            if video_id:
                logger.info("TikTok post complete")
                return {
                    "video_id": video_id,
                    "share_url": share_url,
                    "caption": publish_payload["post_info"]["title"],
                }

            logger.warning(f"TikTok response could not be parsed: {publish_resp.text}")
            return None

        except requests.HTTPError as exc:
            logger.error(f"TikTok API error: {exc.response.text if exc.response else exc}")
            return None
        except Exception as exc:  # noqa: BLE001
            logger.error(f"TikTok posting raised an exception: {exc}", exc_info=True)
            return None
