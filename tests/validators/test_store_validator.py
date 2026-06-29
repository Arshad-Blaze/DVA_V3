from __future__ import annotations

import polars as pl

from parsers.mapper import SchemaRow
from validators.store_validator import StoreValidator


def _row(store_id: str) -> SchemaRow:
    return SchemaRow(
        transaction_id=1,
        record_type="HEADER",
        values={"store_id": store_id},
        metadata_line_number=1,
    )


def test_store_aggregation() -> None:
    validator = StoreValidator()

    rows = [
        _row("S1"),
        _row("S1"),
        _row("S2"),
    ]

    for row in rows:
        validator.process(row)

    validator.finalize()
    df = validator.generate_report()

    assert isinstance(df, pl.DataFrame)

    result = {r[0]: r[1] for r in df.rows()}

    assert result["S1"] == 2
    assert result["S2"] == 1


def test_ignore_non_header_records() -> None:
    validator = StoreValidator()

    row = SchemaRow(
        transaction_id=1,
        record_type="DETAIL",
        values={"store_id": "S1"},
        metadata_line_number=1,
    )

    validator.process(row)

    df = validator.generate_report()

    assert df.shape == (0, 2)