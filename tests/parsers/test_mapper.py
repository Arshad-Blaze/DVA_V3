from __future__ import annotations

from models import (
    Transaction,
    Header,
    Detail,
    Metadata,
)
from models.mapping import FieldMapping, MapperConfig, RecordMapping
from parsers.schema_mapper import SchemaMapper


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


def _transactions():
    return [
        Transaction(
            header=Header(fields=["H", "S1", "20240101"]),
            details=[Detail(fields=["D", "SKU1"])],
            payments=[],
            trailer=None,
            metadata=Metadata(source_file="file", line_number=1),
        )
    ]


def test_mapper_basic() -> None:
    mapper = SchemaMapper(_mapper_config())

    results = list(mapper.map(_transactions()))

    assert len(results) == 2  # HEADER + DETAIL

    header = results[0]
    assert header.values["store_id"] == "S1"
    assert header.values["date"] == "20240101"

    detail = results[1]
    assert detail.values["sku"] == "SKU1"


def test_missing_mapping_skipped() -> None:
    mapper = SchemaMapper(
        MapperConfig(mappings={})  # no mappings
    )

    results = list(mapper.map(_transactions()))

    assert results == []