from validators.store_validator import StoreValidator
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


def test_store_counts() -> None:
    validator = StoreValidator()

    rows = [
        _row("S1", "HEADER"),
        _row("S1", "HEADER"),
        _row("S2", "HEADER"),
        _row("S2", "DETAIL"),  # ignored
    ]

    for r in rows:
        validator.process(r)

    validator.finalize()
    df = validator.generate_report()

    result = dict(zip(df["store_id"], df["transaction_count"]))

    assert result["S1"] == 2
    assert result["S2"] == 1


def test_missing_store() -> None:
    validator = StoreValidator()

    row = _row("", "HEADER")  # missing store
    validator.process(row)

    df = validator.generate_report()
    assert df.shape[0] == 0