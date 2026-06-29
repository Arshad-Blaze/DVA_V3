import polars as pl
from validators.upc_validator import UPCValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(upc: str | None) -> SchemaRow:
    return SchemaRow(
        values={
            "record_type": "DETAIL",
            "upc": upc,
        },
        metadata=Metadata.create(
            source_file="file",
            line_number=1,
            transaction_number=1,
            record_number=1,
        ),
    )


def test_upc_counts() -> None:
    validator = UPCValidator()

    rows = [
        _row("UPC1"),
        _row("UPC1"),
        _row("UPC2"),
    ]

    for r in rows:
        validator.process(r)

    df = validator.generate_report()

    result = dict(zip(df["upc"], df["count"]))

    assert result["UPC1"] == 2
    assert result["UPC2"] == 1


def test_missing_upc() -> None:
    validator = UPCValidator()

    validator.process(_row(None))

    summary = validator.summary()

    assert summary["missing_upc"] == 1


def test_duplicate_flag() -> None:
    validator = UPCValidator()

    validator.process(_row("UPC1"))
    validator.process(_row("UPC1"))

    df = validator.generate_report()

    row = df.filter(pl.col("upc") == "UPC1").row(0)

    assert row[2] is True  # is_duplicate