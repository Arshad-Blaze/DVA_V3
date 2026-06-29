from __future__ import annotations

import streamlit as st
import tempfile
from pathlib import Path
import polars as pl

from services.parser_service import ParserService
from services.validation_service import ValidationManager

from validators.store_validator import StoreValidator
from validators.upc_validator import UPCValidator
from validators.missing_store_validator import MissingStoreValidator
from validators.item_validator import ItemValidator

from configs.default_config import get_parser_config, get_mapper_config
from configs.yaml_loader import load_config

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="DAV Framework", layout="wide")

st.title("📊 DAV Streaming Validation Framework")


# =====================
# PIPELINE
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


def run_pipeline(file_path: Path, parser_config, mapper_config):
    service = ParserService(parser_config, mapper_config)
    manager = build_validator_manager()

    for row in service.parse(file_path):
        manager.process(row)

    manager.finalize()
    return manager.generate_reports()


# =====================
# COMPARISON LOGIC
# =====================
def compare_reports(bau_reports, test_reports):
    """
    Compare BAU vs TEST reports.
    Assumes same validator order.
    """
    comparisons = []

    for bau, test in zip(bau_reports, test_reports):

        if bau.shape[0] == 0 or test.shape[0] == 0:
            comparisons.append(None)
            continue

        key_col = bau.columns[0]  # store_id / upc etc.

        merged = (
            bau.join(
                test,
                on=key_col,
                how="outer",
                suffix="_test",
            )
            .fill_null(0)
        )

        comparisons.append(merged)

    return comparisons


# =====================
# UI
# =====================
page = st.radio("Select Mode", ["Onboarding", "Existing"])


# =====================
# ONBOARDING
# =====================
if page == "Onboarding":

    st.header("🆕 Onboarding (Single File)")

    file = st.file_uploader("Upload File", type=["txt", "csv"])
    config_file = st.file_uploader("Upload Config YAML (Optional)", type=["yaml"])

    if file and st.button("Run Validation"):

        # Save data file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.getvalue())
            path = Path(tmp.name)

        # ✅ Load config
        if config_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(config_file.getvalue())
                config_path = tmp.name

            parser_config, mapper_config = load_config(config_path)
        else:
            parser_config = get_parser_config()
            mapper_config = get_mapper_config()

        reports = run_pipeline(path, parser_config, mapper_config)

        st.success("Validation Complete ✅")

        for i, r in enumerate(reports):
            st.subheader(f"Report {i + 1}")
            st.dataframe(r)


# =====================
# EXISTING
# =====================
if page == "Existing":

    st.header("📂 Existing (BAU vs TEST)")

    bau_file = st.file_uploader("Upload BAU File", type=["txt", "csv"])
    test_file = st.file_uploader("Upload TEST File", type=["txt", "csv"])
    config_file = st.file_uploader("Upload Config YAML (Optional)", type=["yaml"])

    if bau_file and test_file and st.button("Run Comparison"):

        # Save files
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(bau_file.getvalue())
            bau_path = Path(tmp.name)

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(test_file.getvalue())
            test_path = Path(tmp.name)

        # ✅ Load config ONCE (shared)
        if config_file:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(config_file.getvalue())
                config_path = tmp.name

            parser_config, mapper_config = load_config(config_path)
        else:
            parser_config = get_parser_config()
            mapper_config = get_mapper_config()

        # ✅ Run pipelines
        st.info("Processing BAU...")
        bau_reports = run_pipeline(bau_path, parser_config, mapper_config)

        st.info("Processing TEST...")
        test_reports = run_pipeline(test_path, parser_config, mapper_config)

        st.info("Comparing results...")
        comparisons = compare_reports(bau_reports, test_reports)

        st.success("Comparison Complete ✅")

        # Display
        for i, comp in enumerate(comparisons):
            st.subheader(f"Comparison Report {i + 1}")

            if comp is not None:
                st.dataframe(comp)

                st.download_button(
                    label=f"Download Report {i + 1}",
                    data=comp.write_csv(),
                    file_name=f"comparison_report_{i+1}.csv",
                )
            else:
                st.write("No data to compare")