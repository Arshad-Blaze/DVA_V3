from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Generic validator interface.

    Validators operate on streaming units (SchemaRow).
    """

    @abstractmethod
    def process(self, record: Any) -> None:
        """
        Process a single record.
        """
        raise NotImplementedError

    @abstractmethod
    def finalize(self) -> None:
        """Finalize aggregation."""
        raise NotImplementedError

    @abstractmethod
    def generate_report(self) -> Any:
        """Return final report."""
        raise NotImplementedError