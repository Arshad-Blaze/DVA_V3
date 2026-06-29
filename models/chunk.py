from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkMetadata:
    """Metadata for streaming chunks."""

    chunk_index: int
    start_line: int
    end_line: int