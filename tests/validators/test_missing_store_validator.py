from validators.missing_store_validator import MissingStoreValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(store_id: str | None, record_type: str) -> SchemaRow:
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


def test_missing_store_detection() -> None:
    validator = MissingStoreValidator()

    rows = [
        _row(None, "HEADER"),
        _row("", "DETAIL"),
        _row("S1", "DETAIL"),
    ]

    for r in rows:
        validator.process(r)

    summary = validator.summary()

    assert summary["missing_store_id"] == 2


def test_grouping_by_record_type() -> None:
    validator = MissingStoreValidator()

    rows = [
        _row(None, "HEADER"),
        _row(None, "HEADER"),
        _row(None, "DETAIL"),
    ]

    for r in rows:
        validator.process(r)

    df = validator.generate_report()

    result = dict(zip(df["record_type"], df["missing_count"]))

    assert result["HEADER"] == 2
    assert result["DETAIL"] == 1


def test_no_missing() -> None:
    validator = MissingStoreValidator()

    validator.process(_row("S1", "HEADER"))

    df = validator.generate_report()

    assert df.shape[0] == 0