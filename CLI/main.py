import argparse
import os
from reports.excel_writer import ExcelReportWriter
from pipeline.run import run_pipeline


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument("--mode", required=True, choices=["onboarding", "existing"])
    parser.add_argument("--file")
    parser.add_argument("--bau-folder")
    parser.add_argument("--test-folder")
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--date-column", default=None)
    parser.add_argument("--output", default="report.xlsx")

    args = parser.parse_args()

    results = []

    if args.mode == "onboarding":
        files = [args.file]

        for f in files:
            results += run_pipeline(f, args.delimiter, args.date_column, "onboarding")

    else:
        # BAU
        for f in os.listdir(args.bau_folder):
            results += run_pipeline(
                os.path.join(args.bau_folder, f),
                args.delimiter,
                args.date_column,
                "bau"
            )

        # TEST
        for f in os.listdir(args.test_folder):
            results += run_pipeline(
                os.path.join(args.test_folder, f),
                args.delimiter,
                args.date_column,
                "test"
            )

    ExcelReportWriter(args.output).write(results)

    print("✅ Report generated:", args.output)


if __name__ == "__main__":
    main()