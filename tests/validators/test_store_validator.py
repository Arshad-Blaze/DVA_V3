import polars as pl
from validators.store_validator import StoreValidator
from models.schema_row import SchemaRow
from models.core import Metadata


def _row(store, units, sales):
    return SchemaRow(
        values={"store_id": store, "units": units, "sales": sales},
        metadata=Metadata.create("f", 1, 1, 1),
    )


def test_store_compare():
    v = StoreValidator()

    v.set_mode("bau")
    v.process(_row("S1", 2, 10))

    v.set_mode("test")
    v.process(_row("S1", 4, 20))

    df = v.generate_result().report_data

    assert df.shape[0] == 1

def test_store():

    v = StoreValidator()

    v.set_mode("bau")
    v.process(SchemaRow(values={"store_id": "S1", "units": 10, "sales": 100}, metadata=None))

    v.set_mode("test")
    v.process(SchemaRow(values={"store_id": "S1", "units": 5, "sales": 50}, metadata=None))

    df = v.generate_result().report_data

    assert df["unit_diff"][0] == 5