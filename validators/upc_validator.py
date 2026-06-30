from __future__ import annotations

from collections import defaultdict

import polars as pl

from validators.base import BaseValidator
from models.schema_row import SchemaRow
from models.validation_result import ValidationResult


class UPCValidator(BaseValidator):

    def __init__(self):
        self._bau_units = defaultdict(float)
        self._bau_sales = defaultdict(float)
        self._bau_count = defaultdict(int)

        self._test_units = defaultdict(float)
        self._test_sales = defaultdict(float)
        self._test_count = defaultdict(int)

        self._mode = "bau"

    def set_mode(self, mode: str):
        self._mode = mode

    def process(self, row: SchemaRow):

        if row.get("record_type") != "DETAIL":
            return

        upc = row.get("upc")
        units = row.get("units")
        sales = row.get("sales")

        if not upc:
            return

        try:
            u = float(units or 0)
            s = float(sales or 0)
        except Exception:
            return

        if self._mode == "bau":
            self._bau_units[upc] += u
            self._bau_sales[upc] += s
            self._bau_count[upc] += 1
        else:
            self._test_units[upc] += u
            self._test_sales[upc] += s
            self._test_count[upc] += 1

    def finalize(self):
        pass

    def summary(self):
        return {
            "total_records": sum(self._bau_count.values()),
            "unique_upc": len(self._bau_count),
            "missing_upc": 0,
        }

    def generate_result(self) -> ValidationResult:

        # ✅ SINGLE MODE (legacy behavior)
        if not self._test_units:
            rows = []

            for upc in self._bau_units:
                count = self._bau_count[upc]
                rows.append(
                    {
                        "upc": upc,
                        "count": count,
                        "is_duplicate": count > 1,
                    }
                )

            df = pl.DataFrame(rows) if rows else pl.DataFrame(
                {"upc": [], "count": [], "is_duplicate": []}
            )

            return ValidationResult(
                validator_name="UPCValidator",
                status="SUCCESS",
                summary={
                    "total_records": sum(self._bau_count.values()),
                    "unique_upc": len(self._bau_count),
                    "missing_upc": 0,
                },
                report_data=df,
            )

        # ✅ COMPARISON MODE
        all_upcs = set(self._bau_units) | set(self._test_units)

        rows = []

        for upc in all_upcs:
            bau_u = self._bau_units.get(upc, 0)
            test_u = self._test_units.get(upc, 0)

            bau_s = self._bau_sales.get(upc, 0)
            test_s = self._test_sales.get(upc, 0)

            rows.append(
                {
                    "upc": upc,
                    "bau_units": bau_u,
                    "test_units": test_u,
                    "unit_diff": test_u - bau_u,
                    "bau_sales": bau_s,
                    "test_sales": test_s,
                    "sales_diff": test_s - bau_s,
                    "missing_in_test": upc in self._bau_units and upc not in self._test_units,
                    "new_in_test": upc in self._test_units and upc not in self._bau_units,
                }
            )

        df = pl.DataFrame(rows)

        return ValidationResult(
            validator_name="UPCValidator",
            status="SUCCESS",
            summary={
                "total_upcs": len(all_upcs),
                "missing_in_test": sum(r["missing_in_test"] for r in rows),
                "new_in_test": sum(r["new_in_test"] for r in rows),
            },
            report_data=df,
        )