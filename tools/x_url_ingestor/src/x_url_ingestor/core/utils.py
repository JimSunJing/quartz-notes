from __future__ import annotations

import re
from pathlib import Path

_INVALID_FILENAME_CHARS = re.compile(r"[^\w\-]+", re.ASCII)
_MULTI_DASH = re.compile(r"-{2,}")


def slugify(text: str, fallback: str = "post", max_len: int = 80) -> str:
    value = text.strip().lower().replace(" ", "-")
    value = _INVALID_FILENAME_CHARS.sub("-", value)
    value = _MULTI_DASH.sub("-", value).strip("-_")
    if not value:
        value = fallback
    return value[:max_len].rstrip("-_")


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    escaped = escaped.replace("\n", " ").replace("\r", " ").strip()
    return f"\"{escaped}\""


def detect_quartz_content_dir() -> Path:
    env_path = Path.cwd()
    cwd_candidates = [env_path, *env_path.parents]

    module_path = Path(__file__).resolve()
    module_candidates = [module_path.parent, *module_path.parents]

    for base in [*cwd_candidates, *module_candidates]:
        if (base / "quartz.config.ts").exists() and (base / "content").is_dir():
            return (base / "content").resolve()

    fallback = (Path.cwd() / "content").resolve()
    fallback.mkdir(parents=True, exist_ok=True)
    return fallback

