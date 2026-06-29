from __future__ import annotations

import logging
from collections import defaultdict

import polars as pl

from models.schema_row import SchemaRow
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class UPCValidator(BaseValidator):
    """
    Validates UPC-level data.

    Capabilities:
    - Count total occurrences per UPC
    - Detect missing UPCs
    - Identify duplicates
    """

    def __init__(self) -> None:
        self._upc_counts: dict[str, int] = defaultdict(int)
        self._missing_count: int = 0
        self._total_records: int = 0

    def process(self, row: SchemaRow) -> None:
        """
        Process one SchemaRow.
        """
        # Typically UPC exists on DETAIL rows
        if row.values.get("record_type") != "DETAIL":
            return

        self._total_records += 1

        upc = row.values.get("upc")

        if not upc:
            self._missing_count += 1
            logger.debug(
                "Missing UPC at line %s",
                row.metadata.line_number,
            )
            return

        self._upc_counts[upc] += 1

    def finalize(self) -> None:
        """No additional processing required."""
        pass

    def generate_report(self) -> pl.DataFrame:
        """
        Generate Polars report.
        """

        if not self._upc_counts:
            return pl.DataFrame(
                {
                    "upc": [],
                    "count": [],
                }
            )

        df = pl.DataFrame(
            {
                "upc": list(self._upc_counts.keys()),
                "count": list(self._upc_counts.values()),
            }
        )

        # Add duplicate flag
        df = df.with_columns(
            (pl.col("count") > 1).alias("is_duplicate")
        )

        return df.lazy().collect()

    def summary(self) -> dict:
        """
        Useful for quick stats (optional helper).
        """
        return {
            "total_records": self._total_records,
            "unique_upc": len(self._upc_counts),
            "missing_upc": self._missing_count,
        }