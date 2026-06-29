from __future__ import annotations

from models import (
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
    FileType,
)
from models.mapping import MapperConfig, RecordMapping, FieldMapping


# =====================
# Parser Config
# =====================
def get_parser_config() -> ParserConfig:
    return ParserConfig(
        reader=ReaderConfig(
            type=FileType.DELIMITED,
            delimiter="|",
            encoding="utf-8",
        ),
        transaction=TransactionConfig(
            start_record="H"
        ),
        records={
            "H": RecordDefinition(code="H", role=RecordRole.HEADER),
            "D": RecordDefinition(code="D", role=RecordRole.DETAIL),
        },
    )


# =====================
# Mapper Config
# =====================
def get_mapper_config() -> MapperConfig:
    return MapperConfig(
        mappings={
            "HEADER": RecordMapping(
                record_type="HEADER",
                fields={
                    "store_id": FieldMapping("store_id", 1),
                },
            ),
            "DETAIL": RecordMapping(
                record_type="DETAIL",
                fields={
                    "upc": FieldMapping("upc", 1),
                    "units": FieldMapping("units", 2),
                    "sales": FieldMapping("sales", 3),
                },
            ),
        }
    )
