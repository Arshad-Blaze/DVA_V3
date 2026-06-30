from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .core import Metadata


@dataclass(frozen=True)
class SchemaRow:
    values: dict
    metadata: Metadata

    def get(self, key: str, default=None):
        return self.values.get(key, default)
