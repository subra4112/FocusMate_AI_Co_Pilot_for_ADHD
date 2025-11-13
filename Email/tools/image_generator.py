"""Image generation utilities using OpenAI's Images API."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_client() -> Optional["OpenAI"]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.debug("OPENAI_API_KEY not set; skipping image generation")
        return None
    if OpenAI is None:
        logger.warning("openai package not installed; cannot generate images")
        return None
    return OpenAI(api_key=api_key)


def generate_logo_dalle(subject: str, *, size: str = "1024x1024") -> Optional[str]:
    """Generate a minimalist email logo for the given subject using DALL·E.

    Args:
        subject: The subject or topic to inspire the logo.
        size: Image size, defaults to 512x512 to keep responses lightweight.

    Returns:
        URL of the generated image, or ``None`` if generation fails.
    """

    client = _get_client()
    if client is None:
        return None

    prompt = (
        "Create a minimalist, professional logo icon for the topic provided.\n"
        "Requirements:\n"
        "- Simple flat design\n"
        "- Clean vector-style look\n"
        "- Suitable for an email header\n"
        "- Square format\n"
        "- Professional color palette\n"
        "- No text or lettering in the image\n\n"
        f"Topic: {subject.strip() or 'Inbox Update'}"
    )

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        data = response.data[0]
        if hasattr(data, "url") and data.url:
            return data.url
        logger.warning("OpenAI image response missing URL: %s", response)
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("Failed to generate DALL·E image: %s", exc)
    return None
