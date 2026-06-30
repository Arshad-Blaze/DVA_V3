from __future__ import annotations

import polars as pl
import pandas as pd


class ExcelReportWriter:

    def __init__(self, output_path: str):
        self.output_path = output_path

    def _write_df(self, writer, df, sheet_name: str):

        if df is None or len(df) == 0:
            return

        # ✅ Convert Polars → Pandas (required for Excel)
        if isinstance(df, pl.DataFrame):
            df = df.to_pandas()

        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)

    def write(self, results):

        with pd.ExcelWriter(self.output_path, engine="xlsxwriter") as writer:

            for result in results:

                name = result.validator_name

                # ✅ ✅ SUMMARY VALIDATOR
                if name == "SummaryValidator":
                    self._write_df(writer, result.report_data, "Summary")

                # ✅ ✅ STORE
                elif name == "StoreValidator":
                    self._write_df(writer, result.report_data, "Store")

                # ✅ ✅ ITEM
                elif name == "ItemValidator":
                    self._write_df(writer, result.report_data, "Item")

                # ✅ ✅ UPC VALIDATOR
                elif name == "UniqueUPCValidator":

                    metadata = result.metadata or {}

                    # onboarding
                    if "aggregated" in metadata:
                        self._write_df(writer, metadata["aggregated"], "UPC_Aggregated")

                    # existing
                    if "bau" in metadata:
                        self._write_df(writer, metadata["bau"], "UPC_BAU")

                    if "test" in metadata:
                        self._write_df(writer, metadata["test"], "UPC_TEST")

                    if "combined" in metadata:
                        self._write_df(writer, metadata["combined"], "UPC_Combined")

                # ✅ ✅ RAW DATA REVIEW
                elif name == "RawDataReviewValidator":

                    metadata = result.metadata or {}

                    if "summary_sheet" in metadata:
                        self._write_df(writer, metadata["summary_sheet"], "Raw_Summary")

                    if "file_metadata_sheet" in metadata:
                        self._write_df(writer, metadata["file_metadata_sheet"], "File_Metadata")

                # ✅ ✅ MISSING STORE
                elif name == "MissingStoreValidator":
                    self._write_df(writer, result.report_data, "Missing_Stores")

            # ✅ Save file
            writer.close()