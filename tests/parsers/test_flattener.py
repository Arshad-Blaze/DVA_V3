from __future__ import annotations

from models import (
    Detail,
    Header,
    Metadata,
    Payment,
    Trailer,
    Transaction,
)
from parsers.flattener import Flattener


def _transaction() -> Transaction:
    return Transaction(
        header=Header(fields=["H1"]),
        details=[Detail(fields=["D1"]), Detail(fields=["D2"])],
        payments=[Payment(fields=["P1"])],
        trailer=Trailer(fields=["T1"]),
        metadata=Metadata(source_file="file.txt", line_number=1),
    )


def test_flattener_basic() -> None:
    flattener = Flattener()

    rows = list(flattener.flatten([_transaction()]))

    # Header + 2 Details + 1 Payment + Trailer = 5
    assert len(rows) == 5

    assert rows[0].record_type == "HEADER"
    assert rows[1].record_type == "DETAIL"
    assert rows[3].record_type == "PAYMENT"
    assert rows[4].record_type == "TRAILER"


def test_transaction_id_increments() -> None:
    flattener = Flattener()

    txns = [_transaction(), _transaction()]

    rows = list(flattener.flatten(txns))

    txn_ids = {row.transaction_id for row in rows}

    assert txn_ids == {1, 2}