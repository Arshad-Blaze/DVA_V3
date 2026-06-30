from __future__ import annotations

from collections import defaultdict
import polars as pl
from datetime import datetime

from validators.base import BaseValidator
from models.schema_row import SchemaRow
from models.validation_result import ValidationResult


class RawDataReviewValidator(BaseValidator):

    def __init__(self, date_column: str | None = None):

        # ✅ counters
        self.total_units = 0.0
        self.total_sales = 0.0
        self.records = 0

        self.blank_upc = 0
        self.blank_desc = 0
        self.invalid_desc = 0
        self.negative_sales = 0

        # ✅ sets for uniqueness
        self.unique_upc = set()
        self.unique_records = set()

        # ✅ non-moving UPC tracking
        self.upc_units = defaultdict(float)

        # ✅ store tracking
        self.stores = set()

        # ✅ metadata (to be filled externally if needed)
        self.file_name = None
        self.file_format = None
        self.delimiter = None
        self.file_size = None

        # ✅ column count
        self.column_count = 0

        # ✅ DATE CONFIG (user-driven)
        self.date_column = date_column
        self.unique_dates = set()
        self.invalid_dates = 0

    # ✅ date validation (inside class)
    def _is_valid_date(self, value: str) -> bool:
        formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"]

        for fmt in formats:
            try:
                datetime.strptime(value, fmt)
                return True
            except Exception:
                continue

        return False

    def process(self, row: SchemaRow):

        self.records += 1

        # ✅ capture column count on first row
        if self.records == 1:
            self.column_count = len(row.values)

        upc = row.get("upc")
        desc = row.get("description")
        units = row.get("units")
        sales = row.get("sales")
        store = row.get("store_id")

        # ✅ DATE HANDLING (ONLY if user provides column)
        if self.date_column:
            date_val = row.get(self.date_column)

            if date_val:
                date_str = str(date_val)

                if self._is_valid_date(date_str):
                    self.unique_dates.add(date_str)
                else:
                    self.invalid_dates += 1
            else:
                self.invalid_dates += 1

        # ✅ UPC checks
        if not upc:
            self.blank_upc += 1
        else:
            self.unique_upc.add(str(upc))

        # ✅ Description checks
        if not desc:
            self.blank_desc += 1
        elif not isinstance(desc, str):
            self.invalid_desc += 1

        # ✅ Units and Sales
        try:
            u = float(units or 0)
            s = float(sales or 0)
        except Exception:
            return

        self.total_units += u
        self.total_sales += s

        if s < 0:
            self.negative_sales += 1

        # ✅ Non-moving UPC tracking
        if upc:
            self.upc_units[upc] += u

        # ✅ Store tracking
        if store:
            self.stores.add(str(store))

        # ✅ Unique records (order-safe)
        self.unique_records.add(tuple(sorted(row.values.items())))

    def finalize(self):
        pass

    def generate_result(self) -> ValidationResult:

        # ✅ Non-moving UPCs
        non_moving_upc = sum(1 for u in self.upc_units.values() if u == 0)

        # ✅ ✅ SUMMARY SHEET (NUMERIC ONLY — IMPORTANT)
        summary_data = [
            ("No. Of Units", self.total_units),
            ("Total Sales", self.total_sales),
            ("Records", self.records),
            ("Blank UPCs", self.blank_upc),
            ("Blank Description", self.blank_desc),
            ("Invalid Description", self.invalid_desc),
            ("Negative Sales", self.negative_sales),
            ("Unique Records", len(self.unique_records)),
            ("Column Count", self.column_count),
            ("Non Moving UPCs", non_moving_upc),
        ]

        summary_df = pl.DataFrame({
            "Metric": [x[0] for x in summary_data],
            "Value": [x[1] for x in summary_data],  # ✅ keep numeric
        })

        # ✅ ✅ METADATA SHEET (TEXT + FILE INFO)
        metadata_dict = {
            "File Name": self.file_name,
            "File Format": self.file_format,
            "Delimiter": self.delimiter,
            "File Size": self.file_size,
            "Unique Stores": len(self.stores),
            "Total Units": self.total_units,
            "Total Sales": self.total_sales,

            # ✅ moved here to avoid breaking summary typing
            "Alphanumerical UPCs": "No",
        }

        # ✅ Date info (ONLY if configured)
        if self.date_column:
            metadata_dict["Date Column"] = self.date_column
            metadata_dict["Unique Date Count"] = len(self.unique_dates)
            metadata_dict["Invalid Dates"] = self.invalid_dates
            metadata_dict["Sample Dates"] = ", ".join(list(self.unique_dates)[:5])

        metadata_df = pl.DataFrame([metadata_dict])

        return ValidationResult(
            validator_name="RawDataReviewValidator",
            status="SUCCESS",
            summary={
                "records": self.records,
                "unique_upcs": len(self.unique_upc),
            },
            metadata={
                "summary_sheet": summary_df,
                "file_metadata_sheet": metadata_df,
            },
            report_data=None,
        )
