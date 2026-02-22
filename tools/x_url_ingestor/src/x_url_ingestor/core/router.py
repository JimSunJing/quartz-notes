from __future__ import annotations

from ..parsers.base import BaseParser
from ..parsers.twitter import TwitterParser
from .models import ParseResult


class ParserRouter:
    def __init__(self, parsers: list[BaseParser] | None = None) -> None:
        self.parsers = parsers or [TwitterParser()]

    def route(self, url: str) -> ParseResult:
        for parser in self.parsers:
            if parser.can_handle(url):
                return parser.parse(url)
        return ParseResult.failure(
            url=url,
            error="Unsupported URL. Please paste an x.com or twitter.com post URL.",
        )

