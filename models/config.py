from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from .enums import FileType, RecordRole


@dataclass(frozen=True)
class ReaderConfig:
    """Reader configuration."""

    type: FileType
    delimiter: Optional[str] = None


@dataclass(frozen=True)
class RecordDefinition:
    """Defines a record type and its role."""

    code: str
    role: RecordRole


@dataclass(frozen=True)
class TransactionConfig:
    """Transaction boundary configuration."""

    start_record: str


@dataclass(frozen=True)
class ParserConfig:
    """Top-level parser configuration."""

    reader: ReaderConfig
    transaction: TransactionConfig
    records: Dict[str, RecordDefinition]

    def get_role(self, record_code: str) -> RecordRole:
        """Get role for a given record code."""
        if record_code not in self.records:
            raise KeyError(f"Unknown record code: {record_code}")
        return self.records[record_code].role