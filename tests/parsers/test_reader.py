from __future__ import annotations

from pathlib import Path

from models import FileType, ReaderConfig
from parsers.reader import (
    ChunkedReaderWrapper,
    DelimitedReader,
    FixedWidthReader,
    ReaderFactory,
)


def test_delimited_reader(tmp_path: Path) -> None:
    file = tmp_path / "test.txt"
    file.write_text("A|B|C\nD|E|F\n")

    reader = DelimitedReader(file)

    lines = list(reader.read())

    assert lines == ["A|B|C", "D|E|F"]


def test_fixed_width_reader(tmp_path: Path) -> None:
    file = tmp_path / "fw.txt"
    file.write_text("ABCDEF\nGHIJKL\n")

    reader = FixedWidthReader(file)

    lines = list(reader.read())

    assert lines == ["ABCDEF", "GHIJKL"]


def test_reader_factory_delimited(tmp_path: Path) -> None:
    file = tmp_path / "test.txt"
    file.write_text("A|B\n")

    config = ReaderConfig(type=FileType.DELIMITED, delimiter="|")

    reader = ReaderFactory.create(file, config)

    assert isinstance(reader, DelimitedReader)


def test_reader_factory_fixed_width(tmp_path: Path) -> None:
    file = tmp_path / "test.txt"
    file.write_text("ABC\n")

    config = ReaderConfig(type=FileType.FIXED_WIDTH)

    reader = ReaderFactory.create(file, config)

    assert isinstance(reader, FixedWidthReader)


def test_chunked_reader(tmp_path: Path) -> None:
    file = tmp_path / "test.txt"
    file.write_text("A\nB\nC\nD\n")

    base_reader = DelimitedReader(file)
    reader = ChunkedReaderWrapper(base_reader, chunk_size=2)

    output = list(reader.read())

    assert len(output) == 4

    # First chunk
    assert output[0][1].chunk_index == 0
    assert output[1][1].chunk_index == 0

    # Second chunk
    assert output[2][1].chunk_index == 1
    assert output[3][1].chunk_index == 1