from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import TypeVar

from linkedin_idea_to_post.domain.post import Post

T = TypeVar("T")


async def run_blocking[T](fn: Callable[[], T]) -> T:
    """Run synchronous I/O, embedding, or CrewAI calls off the event loop."""
    return await asyncio.to_thread(fn)


def post_short_preview(post: Post, max_chars: int = 90) -> str:
    """Compact single-line preview from post body (since Post has no title)."""
    collapsed = " ".join(post.body.split())
    if len(collapsed) <= max_chars:
        return collapsed
    return f"{collapsed[: max_chars - 1].rstrip()}…"


def format_hashtags(post: Post) -> str:
    if not post.hashtags:
        return ""
    return " ".join(
        tag if tag.startswith("#") else f"#{tag}" for tag in sorted(post.hashtags)
    )
