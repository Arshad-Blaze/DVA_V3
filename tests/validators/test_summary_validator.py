import polars as pl

from validators.summary_validator import SummaryValidator
from models.validation_result import ValidationResult


def test_summary_basic():

    # ✅ mock RawDataReview output
    raw = ValidationResult(
        validator_name="RawDataReviewValidator",
        status="SUCCESS",
        summary={"records": 1000, "unique_upcs": 10},
        metadata={
            "file_metadata_sheet": pl.DataFrame({
                "Total Units": [1000.0],
                "Total Sales": [10000.0],
                "Unique Stores": [5],
            })
        },
        report_data=None,
    )

    # ✅ mock MissingStore output
    missing = ValidationResult(
        validator_name="MissingStoreValidator",
        status="SUCCESS",
        summary={"missing": 2, "additional": 1},
        report_data=None,
    )

    validator = SummaryValidator()
    validator.consume([raw, missing])

    result = validator.generate_result()

    df = result.report_data

    assert df.shape[0] > 0
    assert result.summary["Total Records"] == 1000
    assert result.summary["Missing Stores"] == 2