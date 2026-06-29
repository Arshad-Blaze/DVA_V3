import polars as pl

from validators.item_validator import ItemValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(upc: str, units: str, sales: str) -> SchemaRow:
    return SchemaRow(
        values={
            "record_type": "DETAIL",
            "upc": upc,
            "units": units,
            "sales": sales,
        },
        metadata=Metadata.create(
            source_file="file",
            line_number=1,
            transaction_number=1,
            record_number=1,
        ),
    )


def test_basic_aggregation() -> None:
    validator = ItemValidator()

    rows = [
        _row("U1", "2", "10"),
        _row("U1", "3", "15"),
        _row("U2", "1", "5"),
    ]

    for r in rows:
        validator.process(r)

    df = validator.generate_report()

    result_units = dict(zip(df["upc"], df["total_units"]))
    result_sales = dict(zip(df["upc"], df["total_sales"]))

    assert result_units["U1"] == 5
    assert result_sales["U1"] == 25


def test_avg_price() -> None:
    validator = ItemValidator()

    validator.process(_row("U1", "2", "10"))  # price = 5

    df = validator.generate_report()
    row = df.filter(pl.col("upc") == "U1").row(0)

    assert row[3] == 5.0


def test_invalid_rows() -> None:
    validator = ItemValidator()

    validator.process(_row("U1", "X", "10"))  # invalid units

    summary = validator.summary()

    assert summary["invalid_rows"] == 1


def test_ignore_non_detail() -> None:
    validator = ItemValidator()

    row = SchemaRow(
        values={"record_type": "HEADER"},
        metadata=Metadata.create("file", 1, 1, 1),
    )

    validator.process(row)

    df = validator.generate_report()

    assert df.shape[0] == 0