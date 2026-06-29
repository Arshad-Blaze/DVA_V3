from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, Generator, Iterable

from models.mapping import MapperConfig
from parsers.flattener import NormalizedRow

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SchemaRow:
    """
    Represents a mapped row with named fields.

    Output of Mapper → used by validators
    """

    transaction_id: int
    record_type: str
    values: Dict[str, str]
    metadata_line_number: int


class Mapper:
    """
    Maps NormalizedRow → SchemaRow using configuration.

    Responsibilities:
    - Apply field mappings
    - Produce named fields
    - Remain generic and streaming
    """

    def __init__(self, config: MapperConfig) -> None:
        self.config = config

    def map(
        self, rows: Iterable[NormalizedRow]
    ) -> Generator[SchemaRow, None, None]:
        """
        Apply mapping to normalized rows.
        """

        for row in rows:
            try:
                mapping = self.config.get_mapping(row.record_type)
            except KeyError:
                logger.warning(
                    "No mapping for record_type=%s, skipping", row.record_type
                )
                continue

            values: Dict[str, str] = {}

            for field_name, field_mapping in mapping.fields.items():
                try:
                    values[field_name] = row.fields[field_mapping.index]
                except IndexError:
                    logger.warning(
                        "Field index out of range: %s for record_type=%s",
                        field_mapping.index,
                        row.record_type,
                    )
                    continue

            yield SchemaRow(
                transaction_id=row.transaction_id,
                record_type=row.record_type,
                values=values,
                metadata_line_number=row.metadata_line_number,
            )