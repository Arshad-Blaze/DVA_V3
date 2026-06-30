from __future__ import annotations

from collections import defaultdict
import polars as pl

from validators.base import BaseValidator
from models.schema_row import SchemaRow
from models.validation_result import ValidationResult


class StoreValidator(BaseValidator):

    def __init__(self):
        self._bau_units = defaultdict(float)
        self._bau_sales = defaultdict(float)
        self._test_units = defaultdict(float)
        self._test_sales = defaultdict(float)
        self._mode = "bau"

    def set_mode(self, mode: str):
        self._mode = mode

    def process(self, row: SchemaRow):
        store = row.get("store_id")
        if store is None:
            return

        units = float(row.get("units") or 0)
        sales = float(row.get("sales") or 0)

        if self._mode == "bau":
            self._bau_units[store] += units
            self._bau_sales[store] += sales
        else:
            self._test_units[store] += units
            self._test_sales[store] += sales

    def finalize(self):
        pass

    def generate_result(self) -> ValidationResult:
        rows = []

        for s in set(self._bau_units) | set(self._test_units):
            bu = self._bau_units.get(s, 0)
            tu = self._test_units.get(s, 0)

            bs = self._bau_sales.get(s, 0)
            ts = self._test_sales.get(s, 0)

            unit_diff = bu - tu
            sales_diff = bs - ts

            # ✅ % logic
            unit_pct = (-100 if tu > 0 else 0) if bu == 0 else (unit_diff / bu * 100)
            sales_pct = (-100 if ts > 0 else 0) if bs == 0 else (sales_diff / bs * 100)

            rows.append({
                "store": s,
                "bau_units": round(bu, 3),
                "test_units": round(tu, 3),
                "unit_diff": round(unit_diff, 3),
                "unit_diff_pct": round(unit_pct, 3),
                "bau_sales": round(bs, 3),
                "test_sales": round(ts, 3),
                "sales_diff": round(sales_diff, 3),
                "sales_diff_pct": round(sales_pct, 3),
            })

        return ValidationResult(
            validator_name="StoreValidator",
            status="SUCCESS",
            report_data=pl.DataFrame(rows),
        )
