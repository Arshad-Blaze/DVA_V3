from __future__ import annotations

import pytest

from models import (
    Detail,
    Header,
    Metadata,
    Payment,
    Trailer,
    Transaction,
)


def test_transaction_valid() -> None:
    transaction = Transaction(
        header=Header(fields=["H1"]),
        details=[Detail(fields=["D1"])],
        payments=[Payment(fields=["P1"])],
        trailer=Trailer(fields=["T1"]),
        metadata=Metadata(source_file="file.txt", line_number=1),
    )

    assert transaction.header is not None
    assert len(transaction.details) == 1


def test_transaction_requires_details() -> None:
    with pytest.raises(ValueError):
        Transaction(
            header=None,
            details=[],
            payments=[],
            trailer=None,
            metadata=Metadata(source_file="file.txt", line_number=1),
        )