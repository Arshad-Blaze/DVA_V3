from __future__ import annotations

import logging
from collections import defaultdict

import polars as pl

from models.schema_row import SchemaRow
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class MissingStoreValidator(BaseValidator):
    """
    Detects missing store_id occurrences.

    Aggregates:
    - total missing store_id count
    - record-type level breakdown
    """

    def __init__(self) -> None:
        self._missing_count: int = 0
        self._by_record_type: dict[str, int] = defaultdict(int)
        self._total_rows: int = 0

    def process(self, row: SchemaRow) -> None:
        """
        Process a single SchemaRow.
        """
        self._total_rows += 1

        store_id = row.values.get("store_id")

        if store_id:
            return

        self._missing_count += 1

        record_type = row.values.get("record_type", "UNKNOWN")
        self._by_record_type[record_type] += 1

        logger.debug(
            "Missing store_id at line=%s record_type=%s",
            row.metadata.line_number,
            record_type,
        )

    def finalize(self) -> None:
        """No additional processing required."""
        pass

    def generate_report(self) -> pl.DataFrame:
        """
        Returns breakdown of missing store_id by record type.
        """

        if not self._by_record_type:
            return pl.DataFrame(
                {"record_type": [], "missing_count": []}
            )

        df = pl.DataFrame(
            {
                "record_type": list(self._by_record_type.keys()),
                "missing_count": list(self._by_record_type.values()),
            }
        )

        return df.lazy().collect()

    def summary(self) -> dict:
        """
        High-level summary.
        """
        return {
            "total_rows": self._total_rows,
            "missing_store_id": self._missing_count,
        }