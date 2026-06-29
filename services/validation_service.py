from __future__ import annotations

from typing import List

from models.schema_row import SchemaRow
from validators.base import BaseValidator


class ValidationManager:
    def __init__(self) -> None:
        self.validators: List[BaseValidator] = []

    def register(self, validators: List[BaseValidator]) -> None:
        self.validators.extend(validators)

    def process(self, row: SchemaRow) -> None:
        for v in self.validators:
            v.process(row)

    def finalize(self) -> None:
        for v in self.validators:
            v.finalize()

    def generate_reports(self):
        return [v.generate_report() for v in self.validators]