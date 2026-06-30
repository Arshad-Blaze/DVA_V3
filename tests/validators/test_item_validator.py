from validators.item_validator import ItemValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row():
    return SchemaRow(
        values={
            "store_id": "S1",
            "upc": "U1",
            "description": "A",
            "units": "2",
            "sales": "10",
            "record_type": "DETAIL",
        },
        metadata=Metadata.create("f", 1, 1, 1),
    )


def test_item():
    v = ItemValidator()
    v.process(_row())

    df = v.generate_result().report_data
    assert df.shape[0] == 1
def test_item():
    from validators.item_validator import ItemValidator
    v = ItemValidator()

    v.process({"upc": "U1", "description": "A", "units": 10, "sales": 100})

    assert v.generate_result().report_data.shape[0] > 0