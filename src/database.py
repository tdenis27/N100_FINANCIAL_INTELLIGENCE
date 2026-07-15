from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_DIR = BASE_DIR / "db"
DATABASE_FILE = DB_DIR / "n100_financial_intelligence.db"

EXCLUDED_FILES = {
    "cleaning_summary.csv",
}


def get_processed_csv_files():
    """Return all cleaned dataset CSV files."""

    csv_files = sorted(
        file_path
        for file_path in PROCESSED_DIR.glob("*.csv")
        if file_path.name not in EXCLUDED_FILES
    )

    return csv_files


def get_table_name(file_path):
    """Convert a processed CSV filename into a SQLite table name."""

    table_name = file_path.stem.lower()

    table_name = table_name.replace("-", "_")
    table_name = table_name.replace(" ", "_")

    return table_name


def load_csv_to_database(connection, file_path):
    """Load one processed CSV file into SQLite."""

    table_name = get_table_name(file_path)

    print("-" * 70)
    print(f"FILE       : {file_path.name}")
    print(f"TABLE      : {table_name}")

    dataframe = pd.read_csv(file_path)

    print(f"ROWS       : {len(dataframe)}")
    print(f"COLUMNS    : {len(dataframe.columns)}")

    dataframe.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

    cursor = connection.cursor()

    cursor.execute(
        f'SELECT COUNT(*) FROM "{table_name}"'
    )

    database_rows = cursor.fetchone()[0]

    if database_rows == len(dataframe):
        status = "PASS"
    else:
        status = "FAIL"

    print(f"DB ROWS    : {database_rows}")
    print(f"STATUS     : {status}")

    return {
        "file": file_path.name,
        "table": table_name,
        "csv_rows": len(dataframe),
        "database_rows": database_rows,
        "status": status,
    }


def build_database():
    """Build the NIFTY 100 financial intelligence SQLite database."""

    print("=" * 70)
    print("NIFTY 100 FINANCIAL INTELLIGENCE")
    print("DAY 5 - SQLITE DATABASE PIPELINE")
    print("=" * 70)

    DB_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    csv_files = get_processed_csv_files()

    if not csv_files:
        print("\nERROR: No processed CSV files found.")
        return

    print(f"\nPROCESSED CSV FILES FOUND: {len(csv_files)}")

    connection = sqlite3.connect(DATABASE_FILE)

    results = []

    try:
        for file_path in csv_files:
            result = load_csv_to_database(
                connection,
                file_path,
            )

            results.append(result)

        connection.commit()

    finally:
        connection.close()

    result_df = pd.DataFrame(results)

    passed_tables = int(
        (result_df["status"] == "PASS").sum()
    )

    failed_tables = int(
        (result_df["status"] == "FAIL").sum()
    )

    summary_file = DB_DIR / "database_load_summary.csv"

    result_df.to_csv(
        summary_file,
        index=False,
        encoding="utf-8",
    )

    print("\n" + "=" * 70)
    print("DATABASE LOAD SUMMARY")
    print("=" * 70)

    print(f"Total Tables     : {len(result_df)}")
    print(f"Passed Tables    : {passed_tables}")
    print(f"Failed Tables    : {failed_tables}")
    print(f"Database File    : {DATABASE_FILE}")
    print(f"Summary File     : {summary_file}")

    if failed_tables == 0:
        print("\nDATABASE PIPELINE STATUS: PASSED")
    else:
        print("\nDATABASE PIPELINE STATUS: REVIEW REQUIRED")

    print("\n" + "=" * 70)
    print("DAY 5 SQLITE DATABASE PIPELINE COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    build_database()