from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generator, Iterable

from models import ChunkMetadata, FileType, ReaderConfig

logger = logging.getLogger(__name__)


class Reader(ABC):
    """
    Abstract base reader.

    Responsible only for reading raw lines in a streaming manner.
    """

    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    @abstractmethod
    def read(self) -> Generator[str, None, None]:
        """Yield raw lines from the file."""
        raise NotImplementedError


class DelimitedReader(Reader):
    def __init__(self, file_path: Path, encoding: str = "utf-8") -> None:
        super().__init__(file_path)
        self.encoding = encoding

    def read(self):
        with self.file_path.open("r", encoding=self.encoding) as f:
            for line in f:
                yield line.rstrip("\n")


class FixedWidthReader(Reader):
    """
    Reader for fixed-width files.
    """

    def __init__(self, file_path: Path, encoding: str = "utf-8") -> None:
        super().__init__(file_path)
        self.encoding = encoding

    def read(self):
        with self.file_path.open("r", encoding=self.encoding) as file:
            for line in file:
                yield line.rstrip("\n")


class ChunkedReaderWrapper:
    """
    Wraps a reader to provide chunk metadata.

    Useful for tracking processing boundaries without buffering data.
    """

    def __init__(self, reader: Reader, chunk_size: int = 10000) -> None:
        self.reader = reader
        self.chunk_size = chunk_size

    def read(self) -> Generator[tuple[str, ChunkMetadata], None, None]:
        """
        Yield (line, ChunkMetadata) tuples.
        """
        chunk_index = 0
        start_line = 1

        buffer_count = 0

        for line_number, line in enumerate(self.reader.read(), start=1):
            buffer_count += 1

            metadata = ChunkMetadata(
                chunk_index=chunk_index,
                start_line=start_line,
                end_line=line_number,
            )

            yield line, metadata

            if buffer_count >= self.chunk_size:
                chunk_index += 1
                start_line = line_number + 1
                buffer_count = 0


class ReaderFactory:
    @staticmethod
    def create(file_path: Path, config: ReaderConfig) -> Reader:
        encoding = getattr(config, "encoding", "utf-8")

        if config.type == FileType.DELIMITED:
            return DelimitedReader(file_path, encoding)

        if config.type == FileType.FIXED_WIDTH:
            return FixedWidthReader(file_path, encoding)

        raise ValueError("Unsupported reader")