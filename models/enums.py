from __future__ import annotations

from enum import Enum


class RecordRole(str, Enum):
    """Defines the role of a record within a transaction."""

    HEADER = "header"
    DETAIL = "detail"
    PAYMENT = "payment"
    TRAILER = "trailer"


class FileType(str, Enum):
    """Supported reader file types."""

    DELIMITED = "delimited"
    FIXED_WIDTH = "fixed_width"