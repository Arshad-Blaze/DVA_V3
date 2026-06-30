import polars as pl

from validators.missing_store_validator import MissingStoreValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(store_id: str, record_type: str) -> SchemaRow:
    return SchemaRow(
        values={
            "store_id": store_id,
            "record_type": record_type,
        },
        metadata=Metadata.create(
            source_file="file",
            line_number=1,
            transaction_number=1,
            record_number=1,
        ),
    )


def test_store_comparison():
    v = MissingStoreValidator()

    v.set_mode("bau")
    v.process(_row("S1", "HEADER"))
    v.process(_row("S2", "HEADER"))

    v.set_mode("test")
    v.process(_row("S1", "HEADER"))
    v.process(_row("S3", "HEADER"))

    df = v.generate_result().report_data

    assert df.shape[0] == 3


def test_large_stream():
    v = MissingStoreValidator()

    v.set_mode("bau")
    for i in range(100_000):
        v.process(_row(f"S{i%1000}", "HEADER"))

    v.set_mode("test")
    for i in range(100_000):
        v.process(_row(f"S{i%1200}", "HEADER"))

    result = v.generate_result()

    assert result.summary["total_stores_bau"] == 1000

def test_missing():
    v = MissingStoreValidator()

    v.set_mode("bau")
    v.process({"store_id": "S1"})

    v.set_mode("test")
    v.process({"store_id": "S2"})

    res = v.generate_result()

    assert res.summary["missing"] == 1