from __future__ import annotations

import logging
from typing import Dict

import polars as pl

from parsers.mapper import SchemaRow
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class StoreValidator(BaseValidator):
    """
    Aggregates transaction counts per store using mapped schema data.

    Requirements:
    - Uses SchemaRow (not Transaction)
    - Streaming aggregation
    - Config-driven via Mapper
    """

    def __init__(self) -> None:
        self._store_counts: Dict[str, int] = {}

    def process(self, row: SchemaRow) -> None:  # ✅ CHANGED INPUT TYPE
        """
        Process a single SchemaRow.
        """
        if row.record_type != "HEADER":
            return

        store_id = row.values.get("store_id")

        if not store_id:
            logger.warning(
                "Missing store_id in row at line %s",
                row.metadata_line_number,
            )
            return

        self._store_counts[store_id] = self._store_counts.get(store_id, 0) + 1

    def finalize(self) -> None:
        """No post-processing required."""
        pass

    def generate_report(self) -> pl.DataFrame:
        """
        Return aggregated results as Polars DataFrame.
        """

        if not self._store_counts:
            return pl.DataFrame(
                {
                    "store_id": [],
                    "transaction_count": [],
                }
            )

        df = pl.DataFrame(
            {
                "store_id": list(self._store_counts.keys()),
                "transaction_count": list(self._store_counts.values()),
            }
        )

        return df.lazy().collect()