from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from models.schema_row import SchemaRow


class BaseValidator(ABC):
    """
    Base contract for all validators.

    Validators must:
    - Process streaming SchemaRow inputs
    - Maintain only aggregated state
    - Never store raw rows
    """

    @abstractmethod
    def process(self, row: SchemaRow) -> None:
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_report(self) -> Any:
        raise NotImplementedError