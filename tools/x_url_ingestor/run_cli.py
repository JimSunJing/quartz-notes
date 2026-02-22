from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from x_url_ingestor.core.router import ParserRouter
from x_url_ingestor.core.storage import MarkdownStorage
from x_url_ingestor.core.utils import detect_quartz_content_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch an X URL and write Markdown to Quartz content.")
    parser.add_argument("url", help="x.com/twitter.com status URL")
    parser.add_argument("--content-dir", default=str(detect_quartz_content_dir()))
    parser.add_argument("--filename", default="")
    args = parser.parse_args()

    result = ParserRouter().route(args.url)
    if not result.success:
        print(f"ERROR: {result.error}")
        return 1

    path = MarkdownStorage(Path(args.content_dir)).save(result, filename_hint=args.filename)
    print(f"OK: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

