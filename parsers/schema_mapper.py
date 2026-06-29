from __future__ import annotations

import logging
from typing import Generator, Iterable

from models import Transaction
from models.mapping import MapperConfig
from models.schema_row import SchemaRow
from models.core import Metadata

logger = logging.getLogger(__name__)


class SchemaMapper:
    """
    Converts Transaction → SchemaRow (flatten + map).
    """

    def __init__(self, config: MapperConfig) -> None:
        self.config = config
        self._txn_counter = 0

    def map(
        self, transactions: Iterable[Transaction]
    ) -> Generator[SchemaRow, None, None]:

        record_counter = 0

        for txn in transactions:
            self._txn_counter += 1

            for record in self._extract_records(txn):
                record_counter += 1

                record_type = record["type"]

                mapping = self.config.mappings.get(record_type)
                if not mapping:
                    logger.debug("No mapping for record_type=%s", record_type)
                    continue

                values: dict[str, str] = {}

                # ✅ Add record_type explicitly (CRITICAL)
                values["record_type"] = record_type

                # ✅ Apply config-driven mapping
                for field_name, field_mapping in mapping.fields.items():
                    try:
                        values[field_name] = record["fields"][field_mapping.index]
                    except IndexError:
                        logger.warning(
                            "Index %s missing for field %s",
                            field_mapping.index,
                            field_name,
                        )

                yield SchemaRow(
                    values=values,
                    metadata=Metadata.create(
                        source_file=txn.metadata.source_file,
                        line_number=txn.metadata.line_number,
                        transaction_number=self._txn_counter,
                        record_number=record_counter,
                    ),
                )

    def _extract_records(self, txn: Transaction):
        if txn.header:
            yield {"type": "HEADER", "fields": txn.header.fields}

        for d in txn.details:
            yield {"type": "DETAIL", "fields": d.fields}

        for p in txn.payments:
            yield {"type": "PAYMENT", "fields": p.fields}

        if txn.trailer:
            yield {"type": "TRAILER", "fields": txn.trailer.fields}