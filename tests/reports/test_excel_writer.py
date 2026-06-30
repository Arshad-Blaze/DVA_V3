from reports.excel_writer import ExcelReportWriter
from models.validation_result import ValidationResult
import polars as pl



def test_excel_writer(tmp_path):

    file = tmp_path / "test.xlsx"

    writer = ExcelReportWriter(str(file))

    result = ValidationResult(
        validator_name="SummaryValidator",
        status="SUCCESS",
        report_data=pl.DataFrame({"Metric": ["A"], "Value": [1]}),
    )

    writer.write([result])

    assert file.exists()