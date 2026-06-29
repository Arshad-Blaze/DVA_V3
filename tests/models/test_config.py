from __future__ import annotations

import pytest

from models import (
    FileType,
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
)


def test_parser_config_role_lookup() -> None:
    config = ParserConfig(
        reader=ReaderConfig(type=FileType.DELIMITED, delimiter="|"),
        transaction=TransactionConfig(start_record="H"),
        records={
            "H": RecordDefinition(code="H", role=RecordRole.HEADER),
        },
    )

    assert config.get_role("H") == RecordRole.HEADER


def test_parser_config_unknown_record() -> None:
    config = ParserConfig(
        reader=ReaderConfig(type=FileType.DELIMITED, delimiter="|"),
        transaction=TransactionConfig(start_record="H"),
        records={},
    )

    with pytest.raises(KeyError):
        config.get_role("X")