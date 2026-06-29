from __future__ import annotations

import logging
from collections import defaultdict

import polars as pl

from models.schema_row import SchemaRow
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class ItemValidator(BaseValidator):
    """
    Aggregates item-level metrics per UPC.

    Features:
    - Total units per UPC
    - Total sales per UPC
    - Average price validation
    """

    def __init__(self) -> None:
        self._units: dict[str, float] = defaultdict(float)
        self._sales: dict[str, float] = defaultdict(float)
        self._invalid_rows: int = 0
        self._total_rows: int = 0

    def process(self, row: SchemaRow) -> None:
        """
        Process each row (DETAIL only).
        """
        if row.values.get("record_type") != "DETAIL":
            return

        self._total_rows += 1

        upc = row.values.get("upc")
        units = row.values.get("units")
        sales = row.values.get("sales")

        if not upc or units is None or sales is None:
            self._invalid_rows += 1
            return

        try:
            units_val = float(units)
            sales_val = float(sales)
        except ValueError:
            logger.debug(
                "Invalid numeric data at line %s",
                row.metadata.line_number,
            )
            self._invalid_rows += 1
            return

        self._units[upc] += units_val
        self._sales[upc] += sales_val

    def finalize(self) -> None:
        """No additional processing."""
        pass

    def generate_report(self) -> pl.DataFrame:
        """
        Generate item-level aggregation report.
        """
        if not self._units:
            return pl.DataFrame(
                {
                    "upc": [],
                    "total_units": [],
                    "total_sales": [],
                    "avg_price": [],
                }
            )

        upcs = list(self._units.keys())

        df = pl.DataFrame(
            {
                "upc": upcs,
                "total_units": [self._units[u] for u in upcs],
                "total_sales": [self._sales[u] for u in upcs],
            }
        )

        df = df.with_columns(
            (
                pl.when(pl.col("total_units") > 0)
                .then(pl.col("total_sales") / pl.col("total_units"))
                .otherwise(0.0)
                .alias("avg_price")
            )
        )

        return df.lazy().collect()

    def summary(self) -> dict:
        return {
            "total_rows": self._total_rows,
            "invalid_rows": self._invalid_rows,
            "unique_items": len(self._units),
        }