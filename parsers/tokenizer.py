from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List, Optional

from models import FileType, ParserConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Token:
    """
    Represents a parsed line with minimal structural understanding.
    """

    record_type: str
    fields: List[str]
    raw_line: str
    line_number: int


class Tokenizer:
    """
    Converts raw lines into Token objects.

    Responsible ONLY for:
    - Splitting fields
    - Extracting record type
    """

    def __init__(self, config: ParserConfig) -> None:
        self.config = config

    def tokenize(
        self, lines: Generator[str, None, None]
    ) -> Generator[Token, None, None]:
        """
        Convert raw lines into Tokens.
        """
        reader_type = self.config.reader.type

        for line_number, line in enumerate(lines, start=1):
            if reader_type == FileType.DELIMITED:
                yield self._tokenize_delimited(line, line_number)

            elif reader_type == FileType.FIXED_WIDTH:
                yield self._tokenize_fixed_width(line, line_number)

            else:
                raise ValueError(f"Unsupported file type: {reader_type}")

    def _tokenize_delimited(self, line: str, line_number: int) -> Token:
        delimiter = self.config.reader.delimiter

        if delimiter is None:
            raise ValueError("Delimiter must be defined for delimited files.")

        fields = line.split(delimiter)

        if not fields:
            raise ValueError(f"Empty line at {line_number}")

        record_type = fields[0]

        return Token(
            record_type=record_type,
            fields=fields,
            raw_line=line,
            line_number=line_number,
        )

    def _tokenize_fixed_width(self, line: str, line_number: int) -> Token:
        """
        NOTE: Fixed-width slicing remains generic.
        Assumes first character indicates record type.
        Detailed slicing will later be driven via config extension.
        """
        if not line:
            raise ValueError(f"Empty line at {line_number}")

        record_type = line[0]

        # Minimal generic split (1 char record + rest)
        fields = [record_type, line[1:]]

        return Token(
            record_type=record_type,
            fields=fields,
            raw_line=line,
            line_number=line_number,
        )