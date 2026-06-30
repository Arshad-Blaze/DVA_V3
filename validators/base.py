from __future__ import annotations

from abc import ABC, abstractmethod

from models.schema_row import SchemaRow
from models.validation_result import ValidationResult


class BaseValidator(ABC):

    @abstractmethod
    def process(self, row: SchemaRow) -> None:
        pass

    @abstractmethod
    def finalize(self) -> None:
        pass

    @abstractmethod
    def generate_result(self) -> ValidationResult:
        pass

    # ✅ BACKWARD COMPATIBILITY
    def generate_report(self):
        """
        Temporary compatibility for existing tests.
        """
        result = self.generate_result()
        return result.report_data