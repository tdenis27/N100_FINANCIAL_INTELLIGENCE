from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SUMMARY_FILE = PROCESSED_DIR / "cleaning_summary.csv"


def main():
    print("=" * 70)
    print("NIFTY 100 FINANCIAL INTELLIGENCE")
    print("DAY 4 - CLEANED DATA VERIFICATION")
    print("=" * 70)

    csv_files = sorted(
        file
        for file in PROCESSED_DIR.glob("*.csv")
        if file.name != "cleaning_summary.csv"
    )

    if not csv_files:
        print("\nERROR: No processed CSV files found.")
        return

    passed_files = 0
    failed_files = 0
    total_rows = 0

    print("\nPROCESSED FILE CHECK\n")

    for file_path in csv_files:
        try:
            df = pd.read_csv(file_path)

            rows = len(df)
            columns = len(df.columns)
            duplicate_rows = int(df.duplicated().sum())
            empty_columns = int(df.isna().all().sum())

            total_rows += rows

            status = "PASS"

            if rows == 0 or columns == 0:
                status = "FAIL"

            if status == "PASS":
                passed_files += 1
            else:
                failed_files += 1

            print(f"File             : {file_path.name}")
            print(f"Rows             : {rows}")
            print(f"Columns          : {columns}")
            print(f"Duplicate Rows   : {duplicate_rows}")
            print(f"Empty Columns    : {empty_columns}")
            print(f"Status           : {status}")
            print("-" * 70)

        except Exception as error:
            failed_files += 1

            print(f"File             : {file_path.name}")
            print(f"Status           : FAIL")
            print(f"Error            : {error}")
            print("-" * 70)

    print("\nSUMMARY")
    print("-" * 70)
    print(f"Total CSV Files  : {len(csv_files)}")
    print(f"Passed Files     : {passed_files}")
    print(f"Failed Files     : {failed_files}")
    print(f"Total Rows       : {total_rows}")

    if SUMMARY_FILE.exists():
        summary_df = pd.read_csv(SUMMARY_FILE)

        print(f"Cleaning Summary : FOUND")
        print(f"Summary Records  : {len(summary_df)}")
    else:
        print("Cleaning Summary : NOT FOUND")
        failed_files += 1

    print("-" * 70)

    if failed_files == 0:
        print("\nCLEANED DATA STATUS: PASSED")
    else:
        print("\nCLEANED DATA STATUS: REVIEW REQUIRED")

    print("\n" + "=" * 70)
    print("DAY 4 CLEANED DATA VERIFICATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()