from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, UTC


# ===========================
# Metadata
# ===========================

@dataclass(frozen=True)
class Metadata:
    source_file: str
    line_number: int

    chunk_number: int = 0
    transaction_number: int = 0
    record_number: int = 0
    processing_timestamp: datetime = datetime.now(UTC)

    @staticmethod
    def create(
        source_file: str,
        line_number: int,
        transaction_number: int,
        record_number: int,
        chunk_number: int = 0,
    ) -> "Metadata":
        return Metadata(
            source_file=source_file,
            line_number=line_number,
            chunk_number=chunk_number,
            transaction_number=transaction_number,
            record_number=record_number,
            processing_timestamp=datetime.now(UTC),
        )


# ===========================
# Transaction Components
# ===========================

@dataclass(frozen=True)
class Header:
    """Transaction header."""
    fields: List[str]


@dataclass(frozen=True)
class Detail:
    """Transaction detail line."""
    fields: List[str]


@dataclass(frozen=True)
class Payment:
    """Transaction payment line."""
    fields: List[str]


@dataclass(frozen=True)
class Trailer:
    """Transaction trailer."""
    fields: List[str]


# ===========================
# Transaction
# ===========================

@dataclass(frozen=True)
class Transaction:
    """
    Core transaction object.
    """

    header: Optional[Header]
    details: List[Detail]
    payments: List[Payment]
    trailer: Optional[Trailer]
    metadata: Metadata

    def __post_init__(self) -> None:
        if not self.details:
            raise ValueError("Transaction must contain at least one detail record.")