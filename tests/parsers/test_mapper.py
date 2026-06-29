from __future__ import annotations

from models.mapping import FieldMapping, MapperConfig, RecordMapping
from parsers.flattener import NormalizedRow
from parsers.mapper import Mapper


def _mapper_config() -> MapperConfig:
    return MapperConfig(
        mappings={
            "HEADER": RecordMapping(
                record_type="HEADER",
                fields={
                    "store_id": FieldMapping(name="store_id", index=1),
                    "date": FieldMapping(name="date", index=2),
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


def _rows():
    return [
        NormalizedRow(
            transaction_id=1,
            record_type="HEADER",
            fields=("H", "S1", "20240101"),
            metadata_line_number=1,
        ),
        NormalizedRow(
            transaction_id=1,
            record_type="DETAIL",
            fields=("D", "SKU1"),
            metadata_line_number=2,
        ),
    ]


def test_mapper_basic() -> None:
    mapper = Mapper(_mapper_config())

    results = list(mapper.map(_rows()))

    assert len(results) == 2

    header = results[0]
    assert header.values["store_id"] == "S1"
    assert header.values["date"] == "20240101"

    detail = results[1]
    assert detail.values["sku"] == "SKU1"


def test_missing_mapping_skipped() -> None:
    mapper = Mapper(_mapper_config())

    rows = [
        NormalizedRow(
            transaction_id=1,
            record_type="UNKNOWN",
            fields=("X",),
            metadata_line_number=1,
        )
    ]

    results = list(mapper.map(rows))

    assert results == []