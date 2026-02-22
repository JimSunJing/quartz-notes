from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import ParseResult
from .utils import slugify, yaml_quote


class MarkdownStorage:
    def __init__(self, content_dir: Path) -> None:
        self.content_dir = content_dir.resolve()

    def save(self, result: ParseResult, filename_hint: str = "") -> Path:
        self.content_dir.mkdir(parents=True, exist_ok=True)
        path = self._next_path(result, filename_hint=filename_hint)
        markdown = self._format_markdown(result)
        path.write_text(markdown, encoding="utf-8")
        return path

    def _next_path(self, result: ParseResult, filename_hint: str = "") -> Path:
        date_prefix = datetime.now().strftime("%Y-%m-%d")
        if filename_hint.strip():
            stem = slugify(filename_hint)
        else:
            tweet_id = str(result.metadata.get("tweet_id", "")).strip()
            title_slug = slugify(result.title, fallback="x-post")
            stem = f"{tweet_id}-{title_slug}" if tweet_id else title_slug

        candidate = self.content_dir / f"{date_prefix}-{stem}.md"
        if not candidate.exists():
            return candidate

        index = 2
        while True:
            numbered = self.content_dir / f"{date_prefix}-{stem}-{index}.md"
            if not numbered.exists():
                return numbered
            index += 1

    def _format_markdown(self, result: ParseResult) -> str:
        lines = [
            "---",
            f"title: {yaml_quote(result.title)}",
            f"date: {yaml_quote(datetime.now().isoformat(timespec='seconds'))}",
            f"source: {yaml_quote(result.url)}",
        ]

        author = (result.author or "").strip()
        if author:
            lines.append(f"author: {yaml_quote(author)}")

        tweet_id = str(result.metadata.get("tweet_id", "")).strip()
        if tweet_id:
            lines.append(f"tweet_id: {yaml_quote(tweet_id)}")

        tags = ["imported", *result.tags]
        deduped_tags: list[str] = []
        seen: set[str] = set()
        for tag in tags:
            clean_tag = slugify(str(tag), fallback="tag")
            if clean_tag not in seen:
                seen.add(clean_tag)
                deduped_tags.append(clean_tag)

        lines.append("tags:")
        for tag in deduped_tags:
            lines.append(f"  - {yaml_quote(tag)}")

        lines.extend(
            [
                "---",
                "",
                f"# {result.title}",
                "",
                result.content.strip(),
                "",
            ]
        )
        return "\n".join(lines)

