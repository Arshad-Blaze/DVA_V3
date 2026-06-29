from __future__ import annotations

from dataclasses import dataclass

from models import (
    Detail,
    Header,
    Metadata,
    Transaction,
)
from validators import BaseValidator, ValidatorManager


@dataclass
class CountValidator(BaseValidator):
    """
    Simple validator used for testing.

    Counts number of transactions.
    """

    count: int = 0

    def process(self, transaction: Transaction) -> None:
        self.count += 1

    def finalize(self) -> None:
        pass

    def generate_report(self) -> int:
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