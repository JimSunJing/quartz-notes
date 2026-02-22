from __future__ import annotations

from abc import ABC, abstractmethod

from ..core.models import ParseResult


class BaseParser(ABC):
    name = "base"

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse(self, url: str) -> ParseResult:
        raise NotImplementedError

