from __future__ import annotations

from dataclasses import dataclass

from .config import ParserConfig
from .mapping import MapperConfig


@dataclass(frozen=True)
class SystemConfig:
    """
    Top-level configuration.

    This is the ONLY config passed into the system.
    """

    version: str
    retailer: str
    layout_version: str

    encoding: str

    parser: ParserConfig
    mapper: MapperConfig