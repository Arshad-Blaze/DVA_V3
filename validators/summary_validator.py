from __future__ import annotations

import polars as pl

from models.validation_result import ValidationResult


class SummaryValidator:
    """
    Aggregates outputs from multiple validators into a unified summary.
    """

    def __init__(self):
        self.metrics: dict[str, float] = {}

    def consume(self, results: list[ValidationResult]):

        for result in results:

            name = result.validator_name

            # ✅ RAW DATA REVIEW
            if name == "RawDataReviewValidator":
                summary = result.summary or {}

                self.metrics["Total Records"] = float(summary.get("records", 0))
                self.metrics["Unique UPCs"] = float(summary.get("unique_upcs", 0))

                metadata = (result.metadata or {}).get("file_metadata_sheet")

                if metadata is not None and metadata.shape[0] > 0:
                    try:
                        self.metrics["Total Units"] = float(
                            metadata.select("Total Units").item()
                        )
                        self.metrics["Total Sales"] = float(
                            metadata.select("Total Sales").item()
                        )
                        self.metrics["Unique Stores"] = float(
                            metadata.select("Unique Stores").item()
                        )
                    except Exception:
                        # ✅ Fail-safe: skip if schema mismatch
                        pass

            # ✅ STORE VALIDATOR
            elif name == "StoreValidator":
                df = result.report_data
                if df is not None and df.shape[0] > 0:
                    self.metrics["Store Count"] = float(df.shape[0])

            # ✅ ITEM VALIDATOR
            elif name == "ItemValidator":
                df = result.report_data
                if df is not None:
                    self.metrics["Item Count"] = float(df.shape[0])

            # ✅ UPC VALIDATOR
            elif name == "UPCValidator":
                summary = result.summary or {}

                self.metrics["Total UPC Records"] = float(
                    summary.get("total_records", 0)
                )
                self.metrics["Unique UPC Count"] = float(
                    summary.get("unique_upc", 0)
                )

            # ✅ MISSING STORE
            elif name == "MissingStoreValidator":
                summary = result.summary or {}

                self.metrics["Missing Stores"] = float(
                    summary.get("missing") or 0
                )
                self.metrics["New Stores"] = float(
                    summary.get("additional") or 0
                )

    def generate_result(self) -> ValidationResult:

        # ✅ Enforce consistent ordering for report output
        ordered_metrics = [
            "Total Records",
            "Unique Stores",
            "Unique UPCs",
            "Total Units",
            "Total Sales",
            "Store Count",
            "Item Count",
            "Total UPC Records",
            "Unique UPC Count",
            "Missing Stores",
            "New Stores",
        ]

        metrics = []
        values = []

        for key in ordered_metrics:
            if key in self.metrics:
                value = self.metrics[key]

                # ✅ Ensure numeric consistency
                if isinstance(value, (int, float)):
                    value = float(value)

                metrics.append(key)
                values.append(value)

        summary_df = pl.DataFrame({
            "Metric": metrics,
            "Value": values,
        })

        return ValidationResult(
            validator_name="SummaryValidator",
            status="SUCCESS",
            summary=self.metrics,
            report_data=summary_df,
        )