from __future__ import annotations

import logging
from typing import Generator, Iterable, List

from models import Transaction
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class ValidatorManager:
    """
    Coordinates execution of multiple validators.

    Responsibilities:
    - Dispatch transactions to validators
    - Maintain streaming flow
    - Trigger finalize and report generation
    """

    def __init__(self, validators: List[BaseValidator]) -> None:
        self.validators = validators

    def process(
        self, transactions: Iterable[Transaction]
    ) -> None:
        """
        Stream transactions to all validators.
        """
        for transaction in transactions:
            for validator in self.validators:
                validator.process(transaction)

    def finalize(self) -> None:
        """
        Finalize all validators.
        """
        for validator in self.validators:
            validator.finalize()

    def generate_reports(self) -> list:
        """
        Collect reports from all validators.
        """
        reports = []
        for validator in self.validators:
            reports.append(validator.generate_report())
        return reports