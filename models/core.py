from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class Metadata:
    """Metadata associated with a transaction."""

    source_file: str
    line_number: int


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


@dataclass(frozen=True)
class Transaction:
    """
    Core transaction object.

    Immutable after creation.
    """

    header: Optional[Header]
    details: List[Detail]
    payments: List[Payment]
    trailer: Optional[Trailer]
    metadata: Metadata

    def __post_init__(self) -> None:
        if not self.details:
            raise ValueError("Transaction must contain at least one detail record.")
