from __future__ import annotations

from collections import defaultdict
import polars as pl

from validators.base import BaseValidator
from models.schema_row import SchemaRow
from models.validation_result import ValidationResult


class UniqueUPCValidator(BaseValidator):

    def __init__(self):
        self._data = defaultdict(lambda: {"units": 0.0, "sales": 0.0})

    def process(self, row: SchemaRow):

        upc = row.get("upc")
        desc = row.get("description") or ""

        if not upc:
            return

        key = (upc, desc)

        self._data[key]["units"] += float(row.get("units") or 0)
        self._data[key]["sales"] += float(row.get("sales") or 0)

    def finalize(self):
        pass

    def generate_result(self) -> ValidationResult:

        rows = []

        for (u, d), v in self._data.items():
            rows.append(
                {
                    "upc": u,
                    "description": d,
                    "units": v["units"],
                    "sales": v["sales"],
                }
            )

        return ValidationResult(
            validator_name="UniqueUPCValidator",
            status="SUCCESS",
            report_data=pl.DataFrame(rows),
        )