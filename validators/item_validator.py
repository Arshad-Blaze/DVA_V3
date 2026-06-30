from collections import defaultdict
import polars as pl

from validators.base import BaseValidator
from models.validation_result import ValidationResult


class ItemValidator(BaseValidator):

    def __init__(self):
        self._bau = defaultdict(lambda: {"units": 0.0, "sales": 0.0})
        self._test = defaultdict(lambda: {"units": 0.0, "sales": 0.0})
        self._mode = "bau"

    def set_mode(self, mode):
        self._mode = mode

    def process(self, row):
        upc = row.get("upc")
        desc = row.get("description") or ""

        if upc is None:
            return

        key = f"{upc}|{desc}"

        units = float(row.get("units") or 0)
        sales = float(row.get("sales") or 0)

        if self._mode == "bau":
            self._bau[key]["units"] += units
            self._bau[key]["sales"] += sales
        else:
            self._test[key]["units"] += units
            self._test[key]["sales"] += sales
    
    def finalize(self):
        pass

    def generate_result(self):

        rows = []

        for k in set(self._bau) | set(self._test):
            bu = self._bau.get(k, {"units": 0, "sales": 0})
            te = self._test.get(k, {"units": 0, "sales": 0})

            unit_diff = bu["units"] - te["units"]
            sales_diff = bu["sales"] - te["sales"]

            unit_pct = (-100 if te["units"] > 0 else 0) if bu["units"] == 0 \
                else (unit_diff / bu["units"] * 100)

            sales_pct = (-100 if te["sales"] > 0 else 0) if bu["sales"] == 0 \
                else (sales_diff / bu["sales"] * 100)

            upc, desc = k.split("|", 1)

            rows.append({
                "upc": upc,
                "description": desc,
                "bau_units": round(bu["units"], 3),
                "test_units": round(te["units"], 3),
                "unit_diff": round(unit_diff, 3),
                "unit_diff_pct": round(unit_pct, 3),
                "bau_sales": round(bu["sales"], 3),
                "test_sales": round(te["sales"], 3),
                "sales_diff": round(sales_diff, 3),
                "sales_diff_pct": round(sales_pct, 3),
            })

        return ValidationResult(
            validator_name="ItemValidator",
            status="SUCCESS",
            report_data=pl.DataFrame(rows),
        )