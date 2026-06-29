from __future__ import annotations

from models import Detail, Header, Metadata, Transaction
from validators.store_validator import StoreValidator

from parsers.mapper import SchemaRow


def _row(i: int) -> SchemaRow:
    return SchemaRow(
        transaction_id=i,
        record_type="HEADER",
        values={"store_id": f"S{i % 10}"},
        metadata_line_number=i,
    )

def test_large_stream() -> None:
    validator = StoreValidator()

    for i in range(100_000):
        validator.process(_row(i))  # ✅ SchemaRow

    validator.finalize()
    df = validator.generate_report()

    assert df.shape[0] == 10