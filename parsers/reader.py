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
    """
    Reader for delimited files.

    Does not parse — only yields raw lines.
    """

    def read(self) -> Generator[str, None, None]:
        logger.info("Starting delimited file read: %s", self.file_path)

        with self.file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                yield line.rstrip("\n")


class FixedWidthReader(Reader):
    """
    Reader for fixed-width files.

    Yields raw lines without interpretation.
    """

    def read(self) -> Generator[str, None, None]:
        logger.info("Starting fixed-width file read: %s", self.file_path)

        with self.file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
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
    """
    Factory for creating reader instances.
    """

    @staticmethod
    def create(file_path: Path, config: ReaderConfig) -> Reader:
        """
        Create appropriate reader based on configuration.
        """
        if config.type == FileType.DELIMITED:
            return DelimitedReader(file_path)

        if config.type == FileType.FIXED_WIDTH:
            return FixedWidthReader(file_path)

        raise ValueError(f"Unsupported reader type: {config.type}")