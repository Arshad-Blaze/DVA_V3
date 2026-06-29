from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .core import Metadata


@dataclass(frozen=True)
class SchemaRow:
    """
    Normalized business row.

    Validators consume this instead of Transactions.
    """

    values: Dict[str, str]
    metadata: Metadata