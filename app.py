"""
Entry point for DAV Framework v3.

This module initializes logging and serves as the main execution entry.
"""

from __future__ import annotations

import logging
from pathlib import Path


def configure_logging() -> None:
    """Configure application-wide logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    """Main entry point."""
    configure_logging()
    logger = logging.getLogger(__name__)

    logger.info("DAV Framework v3 started.")

    # Pipeline will be wired in later modules


if __name__ == "__main__":
    main()