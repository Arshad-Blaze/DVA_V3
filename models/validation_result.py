from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import polars as pl


@dataclass
class ValidationResult:
    """
    Standard output of all validators.

    This replaces returning raw DataFrames.
    """

    validator_name: str

    status: str  # SUCCESS / WARNING / FAILED

    summary: Dict[str, Any] = field(default_factory=dict)

    statistics: Dict[str, Any] = field(default_factory=dict)

    differences: Optional[pl.DataFrame] = None

    warnings: List[str] = field(default_factory=list)

    errors: List[str] = field(default_factory=list)

    metadata: Dict[str, Any] = field(default_factory=dict)

    report_data: Optional[pl.DataFrame] = None