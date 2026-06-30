from __future__ import annotations

from dataclasses import dataclass
import polars as pl

from models import (
    Detail,
    Header,
    Metadata,
    Transaction,
)
from validators import BaseValidator, ValidatorManager
from models.validation_result import ValidationResult


@dataclass
class CountValidator(BaseValidator):

    def __init__(self):
        self.count = 0

    def process(self, row):
        self.count += 1

    def finalize(self):
        pass

    def generate_result(self) -> ValidationResult:
        return ValidationResult(
            validator_name="CountValidator",
            status="SUCCESS",
            summary={"count": self.count},
            report_data=None,  # ✅ important
        )

    # ✅ OVERRIDE compatibility
    def generate_report(self):
        return self.count


def _transactions():
    return [
        Transaction(
            header=Header(fields=["H"]),
            details=[Detail(fields=["D"])],
            payments=[],
            trailer=None,
            metadata=Metadata(source_file="file", line_number=1),
        ),
        Transaction(
            header=Header(fields=["H"]),
            details=[Detail(fields=["D"])],
            payments=[],
            trailer=None,
            metadata=Metadata(source_file="file", line_number=2),
        ),
    ]


def test_validator_manager_process() -> None:
    validator = CountValidator()
    manager = ValidatorManager([validator])

    manager.process(_transactions())
    manager.finalize()

    result = manager.generate_reports()

    assert result == [2]