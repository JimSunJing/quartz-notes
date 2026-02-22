from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ParseResult:
    url: str
    title: str
    content: str = ""
    author: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    extracted_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and bool(self.content.strip())

    @classmethod
    def failure(cls, url: str, error: str) -> "ParseResult":
        return cls(url=url, title="Untitled", error=error)

