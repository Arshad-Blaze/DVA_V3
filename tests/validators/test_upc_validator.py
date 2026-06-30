import polars as pl

from validators.upc_validator import UPCValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(upc: str | None, units: str = "1", sales: str = "1") -> SchemaRow:
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


def test_upc_counts():
    v = UPCValidator()

    v.process(_row("UPC1"))
    v.process(_row("UPC1"))
    v.process(_row("UPC2"))

    df = v.generate_report()

    result = dict(zip(df["upc"], df["count"]))

    assert result["UPC1"] == 2
    assert result["UPC2"] == 1


def test_missing_upc():
    v = UPCValidator()

    v.process(_row(None))

    summary = v.summary()

    assert summary["missing_upc"] == 0


def test_duplicate_flag():
    v = UPCValidator()

    v.process(_row("UPC1"))
    v.process(_row("UPC1"))

    df = v.generate_report()

    row = df.filter(pl.col("upc") == "UPC1").row(0)

    assert row[2] is True


def test_bau_vs_test_comparison():
    v = UPCValidator()

    v.set_mode("bau")
    v.process(_row("U1", "2", "10"))
    v.process(_row("U2", "1", "5"))

    v.set_mode("test")
    v.process(_row("U1", "3", "15"))
    v.process(_row("U3", "1", "7"))

    df = v.generate_result().report_data

    assert df.shape[0] == 3