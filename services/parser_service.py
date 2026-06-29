from __future__ import annotations

from pathlib import Path
from typing import Generator, Optional

from models.schema_row import SchemaRow
from models import ReaderConfig
from models.system_config import SystemConfig

from parsers.reader import ReaderFactory
from parsers.tokenizer import Tokenizer
from parsers.transaction_builder import TransactionBuilder
from parsers.schema_mapper import SchemaMapper
from parsers.engine import ParserEngine


class ParserService:
    """
    Entry point for parsing.

    UI / integration layer must call ONLY this.
    """

    def __init__(
        self,
        parser_config=None,
        mapper_config=None,
        system_config: Optional[SystemConfig] = None,
    ) -> None:
        # ✅ Backward compatibility for tests
        if system_config:
            self.config = system_config
        else:
            self.config = SystemConfig(
                version="1.0",
                retailer="test",
                layout_version="1",
                encoding="utf-8",
                parser=parser_config,
                mapper=mapper_config,
            )

    def parse(self, file_path: Path) -> Generator[SchemaRow, None, None]:
        """
        Run full parsing pipeline.
        """

        reader_config = ReaderConfig(
            type=self.config.parser.reader.type,
            delimiter=self.config.parser.reader.delimiter,
            encoding=self.config.encoding,
        )

        reader = ReaderFactory.create(file_path, reader_config)
        tokenizer = Tokenizer(self.config.parser)
        builder = TransactionBuilder(self.config.parser)
        mapper = SchemaMapper(self.config.mapper)

        engine = ParserEngine(reader, tokenizer, builder, mapper)

        yield from engine.parse()