from __future__ import annotations

import logging
from collections import defaultdict

import polars as pl

from models.schema_row import SchemaRow
from validators.base import BaseValidator

logger = logging.getLogger(__name__)


class StoreValidator(BaseValidator):
    """
    Aggregates transaction counts per store.

    Assumes schema contains:
    - store_id
    - record_type = HEADER indicates new transaction
    """

    def __init__(self) -> None:
        self._store_counts: dict[str, int] = defaultdict(int)

    def process(self, row: SchemaRow) -> None:
        if row.values.get("record_type") != "HEADER":
            return

        store_id = row.values.get("store_id")

        if not store_id:
            logger.warning("Missing store_id at line %s", row.metadata.line_number)
            return

        self._store_counts[store_id] += 1

    def finalize(self) -> None:
        """No-op for this validator."""
        pass

    def generate_report(self) -> pl.DataFrame:
        if not self._store_counts:
            return pl.DataFrame({"store_id": [], "transaction_count": []})

        df = pl.DataFrame(
            {
                "store_id": list(self._store_counts.keys()),
                "transaction_count": list(self._store_counts.values()),
            }
        )

        return df.lazy().collect()