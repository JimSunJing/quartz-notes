from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

from ..core.models import ParseResult
from .base import BaseParser

_TWEET_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:x\.com|twitter\.com)/([A-Za-z0-9_]{1,15})/status/(\d+)"
)


class TwitterParser(BaseParser):
    name = "twitter"

    def __init__(self) -> None:
        self.api_bases = [
            "https://api.fxtwitter.com",
            "https://api.vxtwitter.com",
        ]

    def can_handle(self, url: str) -> bool:
        return bool(_TWEET_URL_RE.search(url))

    def parse(self, url: str) -> ParseResult:
        match = _TWEET_URL_RE.search(url)
        if not match:
            return ParseResult.failure(
                url=url,
                error=(
                    "Invalid X URL. Expected format: "
                    "https://x.com/<user>/status/<tweet_id>"
                ),
            )

        username, tweet_id = match.group(1), match.group(2)
        last_error = "Unknown network error"

        for base in self.api_bases:
            api_url = f"{base}/{username}/status/{tweet_id}"
            try:
                payload = self._fetch_json(api_url)
                result = self._to_parse_result(url=url, username=username, tweet_id=tweet_id, data=payload)
                if result.success:
                    return result
                last_error = result.error or last_error
            except urllib.error.HTTPError as exc:
                last_error = f"{base} returned HTTP {exc.code}"
            except urllib.error.URLError:
                last_error = f"{base} is not reachable"
            except Exception as exc:  # noqa: BLE001
                last_error = f"{base} failed: {exc}"

        return ParseResult.failure(
            url=url,
            error=(
                "Could not read this X post. It may be private/deleted, or the public parsers are down. "
                f"Last error: {last_error}"
            ),
        )

    def _fetch_json(self, url: str) -> dict:
        req = urllib.request.Request(url=url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        return json.loads(body)

    def _to_parse_result(
        self,
        url: str,
        username: str,
        tweet_id: str,
        data: dict,
    ) -> ParseResult:
        code = data.get("code")
        if code not in (None, 200):
            return ParseResult.failure(url, f"API code {code}: {data.get('message', 'unknown error')}")

        tweet = data.get("tweet") or {}
        if not tweet:
            return ParseResult.failure(url, "API returned no tweet data.")

        author_data = tweet.get("author") or {}
        author_name = str(author_data.get("name", "")).strip()
        author_handle = str(author_data.get("screen_name", username)).strip()
        created_at = str(tweet.get("created_at", "")).strip()

        text = str(tweet.get("text", "")).strip()
        article = tweet.get("article") or {}
        article_title = str(article.get("title", "")).strip()
        article_blocks = article.get("content", {}).get("blocks", [])
        if article_blocks:
            article_body = "\n\n".join(
                str(block.get("text", "")).strip()
                for block in article_blocks
                if str(block.get("text", "")).strip()
            )
            text = article_body or text

        if not text:
            return ParseResult.failure(url, "Tweet body is empty.")

        likes = int(tweet.get("likes", 0) or 0)
        retweets = int(tweet.get("retweets", 0) or 0)
        replies = int(tweet.get("replies", 0) or 0)
        views = int(tweet.get("views", 0) or 0)
        bookmarks = int(tweet.get("bookmarks", 0) or 0)

        title = f"X post by @{author_handle}"
        if article_title:
            title = article_title

        lines = [
            f"> Source: {url}",
            f"> Author: @{author_handle}" + (f" ({author_name})" if author_name else ""),
        ]

        if created_at:
            lines.append(f"> Posted at: {created_at}")

        lines.append(
            f"> Stats: likes={likes}, retweets={retweets}, replies={replies}, views={views}, bookmarks={bookmarks}"
        )
        lines.extend(["", text])

        quote = tweet.get("quote") or {}
        quote_text = str(quote.get("text", "")).strip()
        if quote_text:
            quote_author = quote.get("author") or {}
            quote_handle = str(quote_author.get("screen_name", "unknown")).strip()
            lines.extend(
                [
                    "",
                    "## Quoted Post",
                    "",
                    f"> @{quote_handle}: {quote_text}",
                ]
            )

        media_items = (tweet.get("media") or {}).get("all") or []
        if media_items:
            lines.extend(["", "## Media"])
            for idx, item in enumerate(media_items, start=1):
                media_url = str(item.get("url", "")).strip()
                media_type = str(item.get("type", "media")).strip()
                if media_url:
                    lines.append(f"- {media_type} {idx}: {media_url}")

        content = "\n".join(lines).strip()

        metadata = {
            "tweet_id": tweet_id,
            "username": author_handle or username,
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "views": views,
            "bookmarks": bookmarks,
            "created_at": created_at,
        }

        return ParseResult(
            url=url,
            title=title,
            content=content,
            author=f"@{author_handle}" if author_handle else "",
            tags=["x", "twitter"],
            metadata=metadata,
        )

