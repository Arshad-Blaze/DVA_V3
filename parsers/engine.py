from __future__ import annotations

from pathlib import Path
from typing import Generator

from parsers.reader import Reader
from parsers.tokenizer import Tokenizer
from parsers.transaction_builder import TransactionBuilder
from parsers.schema_mapper import SchemaMapper
from models.schema_row import SchemaRow


class ParserEngine:
    """
    Orchestrates full parsing pipeline.
    Fully DI-driven.
    """

    def __init__(
        self,
        reader: Reader,
        tokenizer: Tokenizer,
        builder: TransactionBuilder,
        mapper: SchemaMapper,
    ) -> None:
        self.reader = reader
        self.tokenizer = tokenizer
        self.builder = builder
        self.mapper = mapper

    def parse(self) -> Generator[SchemaRow, None, None]:
        lines = self.reader.read()
        tokens = self.tokenizer.tokenize(lines)
        transactions = self.builder.build(tokens)
        rows = self.mapper.map(transactions)

        yield from rows