from __future__ import annotations

import yaml

from models import (
    ParserConfig,
    ReaderConfig,
    RecordDefinition,
    RecordRole,
    TransactionConfig,
    FileType,
)
from models.mapping import MapperConfig, RecordMapping, FieldMapping


def load_config(path: str):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # =====================
    # Parser Config
    # =====================
    parser = data["parser"]

    reader = parser["reader"]

    reader_config = ReaderConfig(
        type=FileType(reader["type"]),
        delimiter=reader.get("delimiter"),
        encoding=data.get("encoding", "utf-8"),
    )

    transaction_config = TransactionConfig(
        start_record=parser["transaction"]["start_record"]
    )

    records = {}
    for code, r in parser["records"].items():
        records[code] = RecordDefinition(
            code=code,
            role=RecordRole[r["role"]],
        )

    parser_config = ParserConfig(
        reader=reader_config,
        transaction=transaction_config,
        records=records,
    )

    # =====================
    # Mapper Config
    # =====================
    mapper_data = data["mapper"]

    mappings = {}

    for record_type, fields in mapper_data.items():
        mappings[record_type] = RecordMapping(
            record_type=record_type,
            fields={
                name: FieldMapping(name, index)
                for name, index in fields.items()
            },
        )

    mapper_config = MapperConfig(mappings=mappings)

    return parser_config, mapper_config