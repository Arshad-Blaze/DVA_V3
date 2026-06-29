from __future__ import annotations

from pathlib import Path

from services.parser_service import ParserService
from models import (
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
    FileType,
)
from models.mapping import MapperConfig, RecordMapping, FieldMapping


def _parser_config() -> ParserConfig:
    return ParserConfig(
        reader=ReaderConfig(type=FileType.DELIMITED, delimiter="|"),
        transaction=TransactionConfig(start_record="H"),
        records={
            "H": RecordDefinition(code="H", role=RecordRole.HEADER),
            "D": RecordDefinition(code="D", role=RecordRole.DETAIL),
        },
    )


def _mapper_config() -> MapperConfig:
    return MapperConfig(
        mappings={
            "HEADER": RecordMapping(
                record_type="HEADER",
                fields={
                    "store_id": FieldMapping(name="store_id", index=1),
                },
            ),
            "DETAIL": RecordMapping(
                record_type="DETAIL",
                fields={
                    "sku": FieldMapping(name="sku", index=1),
                },
            ),
        }
    )


def test_end_to_end(tmp_path: Path) -> None:
    file = tmp_path / "data.txt"
    file.write_text("H|S1\nD|SKU1\n")

    service = ParserService(_parser_config(), _mapper_config())

    rows = list(service.parse(file))

    assert len(rows) == 2

    assert rows[0].values["store_id"] == "S1"
    assert rows[1].values["sku"] == "SKU1"