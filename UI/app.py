import streamlit as st
import tempfile
from reports.excel_writer import ExcelReportWriter
from pipeline.run import run_pipeline

st.set_page_config(page_title="Data Validation Framework", layout="wide")

st.title("📊 Data Validation Framework")

# ✅ MODE SELECTION
mode = st.radio(
    "Select Mode",
    ["Onboarding", "Existing"]
)

# ✅ COMMON CONFIG
delimiter = st.text_input("Delimiter", value=",")
date_column = st.text_input("Date Column (optional)")

# =========================
# ✅ ONBOARDING FLOW
# =========================
if mode == "Onboarding":

    st.subheader("Onboarding Validation")

    files = st.file_uploader(
        "Upload Data Files",
        type=["csv", "txt"],
        accept_multiple_files=True
    )

    store_ref_file = st.file_uploader(
        "Upload Store Reference File (optional)",
        type=["csv", "txt"]
    )

    run_button = st.button("Run Onboarding Validation")

    if run_button and files:

        st.info("Running onboarding validation...")

        all_results = []

        # ✅ process each file
        for f in files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(f.read())
                file_path = tmp.name

            results = run_pipeline(
                file_path=file_path,
                delimiter=delimiter,
                date_column=date_column or None,
                mode="onboarding"
            )

            all_results.extend(results)

        # ✅ display summary
        for r in all_results:
            if r.validator_name == "SummaryValidator":
                st.subheader("Summary")
                st.dataframe(r.report_data.to_pandas())

        # ✅ generate Excel
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
        ExcelReportWriter(output_file).write(all_results)

        with open(output_file, "rb") as f:
            st.download_button(
                "Download Report",
                f,
                file_name="onboarding_report.xlsx"
            )

# =========================
# ✅ EXISTING FLOW
# =========================
elif mode == "Existing":

    st.subheader("Existing vs Test Comparison")

    bau_files = st.file_uploader(
        "Upload BAU Files",
        type=["csv", "txt"],
        accept_multiple_files=True,
        key="bau"
    )

    test_files = st.file_uploader(
        "Upload TEST Files",
        type=["csv", "txt"],
        accept_multiple_files=True,
        key="test"
    )

    run_button = st.button("Run Comparison")

    if run_button and bau_files and test_files:

        st.info("Running comparison...")

        all_results = []

        # ✅ process BAU files
        for f in bau_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(f.read())
                path = tmp.name

            results = run_pipeline(
                file_path=path,
                delimiter=delimiter,
                date_column=date_column or None,
                mode="bau"
            )

            all_results.extend(results)

        # ✅ process TEST files
        for f in test_files:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(f.read())
                path = tmp.name

            results = run_pipeline(
                file_path=path,
                delimiter=delimiter,
                date_column=date_column or None,
                mode="test"
            )

            all_results.extend(results)

        # ✅ display summary
        for r in all_results:
            if r.validator_name == "SummaryValidator":
                st.subheader("Summary")
                st.dataframe(r.report_data.to_pandas())

        # ✅ Excel export
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name
        ExcelReportWriter(output_file).write(all_results)

        with open(output_file, "rb") as f:
            st.download_button(
                "Download Report",
                f,
                file_name="comparison_report.xlsx"
            )
