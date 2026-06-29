from __future__ import annotations

from typing import Generator

from models import (
    FileType,
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
)
from parsers.tokenizer import Token
from parsers.transaction_builder import TransactionBuilder


def _config() -> ParserConfig:
    return ParserConfig(
        reader=ReaderConfig(type=FileType.DELIMITED, delimiter="|"),
        transaction=TransactionConfig(start_record="H"),
        records={
            "H": RecordDefinition(code="H", role=RecordRole.HEADER),
            "D": RecordDefinition(code="D", role=RecordRole.DETAIL),
            "P": RecordDefinition(code="P", role=RecordRole.PAYMENT),
            "T": RecordDefinition(code="T", role=RecordRole.TRAILER),
        },
    )


def _tokens() -> Generator[Token, None, None]:
    data = [
        Token("H", ["H", "1"], "H|1", 1),
        Token("D", ["D", "A"], "D|A", 2),
        Token("P", ["P", "100"], "P|100", 3),
        Token("T", ["T", "END"], "T|END", 4),
        Token("H", ["H", "2"], "H|2", 5),
        Token("D", ["D", "B"], "D|B", 6),
    ]
    for t in data:
        yield t


def test_transaction_builder_basic() -> None:
    builder = TransactionBuilder(_config())

    transactions = list(builder.build(_tokens()))

    assert len(transactions) == 2

    t1 = transactions[0]
    assert t1.header is not None
    assert len(t1.details) == 1
    assert len(t1.payments) == 1
    assert t1.trailer is not None

    t2 = transactions[1]
    assert t2.header is not None
    assert len(t2.details) == 1
    assert len(t2.payments) == 0
    assert t2.trailer is None