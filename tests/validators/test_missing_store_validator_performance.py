from validators.missing_store_validator import MissingStoreValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(i: int) -> SchemaRow:
    return SchemaRow(
        values={
            "store_id": None if i % 5 == 0 else f"S{i % 10}",
            "record_type": "DETAIL",
        },
        metadata=Metadata.create(
            source_file="file",
            line_number=i,
            transaction_number=i,
            record_number=i,
        ),
    )


def test_large_stream() -> None:
    validator = MissingStoreValidator()

    for i in range(200_000):
        validator.process(_row(i))

    validator.finalize()
    df = validator.generate_report()

    assert df.shape[0] > 0