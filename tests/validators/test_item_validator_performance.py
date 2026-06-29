from validators.item_validator import ItemValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(i: int) -> SchemaRow:
    return SchemaRow(
        values={
            "record_type": "DETAIL",
            "upc": f"UPC{i % 100}",
            "units": "1",
            "sales": "10",
        },
        metadata=Metadata.create(
            source_file="file",
            line_number=i,
            transaction_number=i,
            record_number=i,
        ),
    )


def test_large_stream() -> None:
    validator = ItemValidator()

    for i in range(200_000):
        validator.process(_row(i))

    df = validator.generate_report()

    assert df.shape[0] == 100