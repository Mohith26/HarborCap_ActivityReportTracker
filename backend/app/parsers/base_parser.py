"""Base parser interface for activity report file parsing."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParseResult:
    deals: list[dict[str, Any]] = field(default_factory=list)
    availabilities: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    raw_data: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    sheet_names: list[str] = field(default_factory=list)


class BaseParser(ABC):
    @abstractmethod
    def can_parse(self, file_path: str, file_type: str, sheet_names: list[str] | None = None) -> bool:
        """Return True if this parser can handle this file."""
        pass

    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """Extract data from the file."""
        pass
