from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class FieldMapping:
    """
    Maps a field name to its position index in the source fields.
    """

    name: str
    index: int


@dataclass(frozen=True)
class RecordMapping:
    """
    Defines schema mapping for a specific record type.
    """

    record_type: str
    fields: Dict[str, FieldMapping]


@dataclass(frozen=True)
class MapperConfig:
    """
    Configuration for mapping normalized rows to schema rows.
    """

    mappings: Dict[str, RecordMapping]

    def get_mapping(self, record_type: str) -> RecordMapping:
        if record_type not in self.mappings:
            raise KeyError(f"No mapping found for record type: {record_type}")
        return self.mappings[record_type]