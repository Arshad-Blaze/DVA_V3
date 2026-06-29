from __future__ import annotations

from typing import Generator

import pytest

from models import (
    FileType,
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
)
from parsers.tokenizer import Tokenizer


def _get_config(file_type: FileType) -> ParserConfig:
    return ParserConfig(
        reader=ReaderConfig(type=file_type, delimiter="|"),
        transaction=TransactionConfig(start_record="H"),
        records={
            "H": RecordDefinition(code="H", role=RecordRole.HEADER),
        },
    )


def _line_gen(lines: list[str]) -> Generator[str, None, None]:
    for line in lines:
        yield line


def test_delimited_tokenizer() -> None:
    config = _get_config(FileType.DELIMITED)
    tokenizer = Tokenizer(config)

    lines = ["H|1|2", "D|3|4"]

    tokens = list(tokenizer.tokenize(_line_gen(lines)))

    assert tokens[0].record_type == "H"
    assert tokens[0].fields == ["H", "1", "2"]

    assert tokens[1].record_type == "D"
    assert tokens[1].fields == ["D", "3", "4"]


def test_fixed_width_tokenizer() -> None:
    config = _get_config(FileType.FIXED_WIDTH)
    tokenizer = Tokenizer(config)

    lines = ["H12345", "D67890"]

    tokens = list(tokenizer.tokenize(_line_gen(lines)))

    assert tokens[0].record_type == "H"
    assert tokens[0].fields == ["H", "12345"]

    assert tokens[1].record_type == "D"


def test_missing_delimiter_raises() -> None:
    config = ParserConfig(
        reader=ReaderConfig(type=FileType.DELIMITED, delimiter=None),
        transaction=TransactionConfig(start_record="H"),
        records={},
    )

    tokenizer = Tokenizer(config)

    with pytest.raises(ValueError):
        list(tokenizer.tokenize(_line_gen(["H|1"])))
