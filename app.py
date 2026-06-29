from __future__ import annotations

import argparse
from pathlib import Path
import logging

from services.parser_service import ParserService
from services.validation_service import ValidationManager

from validators.store_validator import StoreValidator
from validators.upc_validator import UPCValidator
from validators.missing_store_validator import MissingStoreValidator
from validators.item_validator import ItemValidator

from configs.default_config import get_parser_config, get_mapper_config
from configs.yaml_loader import load_config


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =====================
# Build Validators
# =====================
def build_validator_manager() -> ValidationManager:
    manager = ValidationManager()

    manager.register(
        [
            StoreValidator(),
            UPCValidator(),
            MissingStoreValidator(),
            ItemValidator(),
        ]
    )

    return manager


# =====================
# Pipeline
# =====================
def run_pipeline(file_path: Path, config_path: str):
    parser_config, mapper_config = load_config(config_path)

    service = ParserService(parser_config, mapper_config)
    manager = build_validator_manager()

    for row in service.parse(file_path):
        manager.process(row)

    manager.finalize()
    return manager.generate_reports()


# =====================
# CLI Main
# =====================
def main():
    parser = argparse.ArgumentParser(description="DAV CLI Runner")

    parser.add_argument("--file", help="Single file (onboarding)")
    parser.add_argument("--bau", help="BAU file")
    parser.add_argument("--test", help="TEST file")

    args = parser.parse_args()

    if args.file:
        logger.info("Running onboarding flow")

        reports = run_pipeline(Path(args.file))

        for r in reports:
            print(r)

    elif args.bau and args.test:
        logger.info("Running existing comparison flow")

        bau_reports = run_pipeline(Path(args.bau))
        test_reports = run_pipeline(Path(args.test))

        for i, (b, t) in enumerate(zip(bau_reports, test_reports)):
            print(f"\n==== Comparison {i+1} ====")
            print("BAU:")
            print(b)
            print("TEST:")
            print(t)

    else:
        print("Provide either --file OR --bau and --test")


if __name__ == "__main__":
    main()