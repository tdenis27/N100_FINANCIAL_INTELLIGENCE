from pathlib import Path
import sqlite3

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_FILE = BASE_DIR / "db" / "n100_financial_intelligence.db"

EXCLUDED_FILES = {
    "cleaning_summary.csv",
}


def get_expected_tables():
    """Return expected table names from processed CSV files."""

    csv_files = sorted(
        file_path
        for file_path in PROCESSED_DIR.glob("*.csv")
        if file_path.name not in EXCLUDED_FILES
    )

    expected_tables = {
        file_path.stem.lower()
        .replace("-", "_")
        .replace(" ", "_"): file_path
        for file_path in csv_files
    }

    return expected_tables


def get_database_tables(connection):
    """Return all user-created SQLite tables."""

    query = """
    SELECT name
    FROM sqlite_master
    WHERE type = 'table'
      AND name NOT LIKE 'sqlite_%'
    ORDER BY name;
    """

    cursor = connection.cursor()
    cursor.execute(query)

    return [
        row[0]
        for row in cursor.fetchall()
    ]


def verify_database():
    """Verify SQLite database tables and row counts."""

    print("=" * 70)
    print("NIFTY 100 FINANCIAL INTELLIGENCE")
    print("DAY 5 - SQLITE DATABASE VERIFICATION")
    print("=" * 70)

    if not DB_FILE.exists():
        print("\nERROR: Database file not found.")
        print(f"Expected Database: {DB_FILE}")
        return

    expected_tables = get_expected_tables()

    connection = sqlite3.connect(DB_FILE)

    passed_tables = 0
    failed_tables = 0
    total_database_rows = 0

    try:
        database_tables = get_database_tables(connection)

        print(f"\nEXPECTED TABLES : {len(expected_tables)}")
        print(f"DATABASE TABLES : {len(database_tables)}")

        print("\nTABLE VERIFICATION")
        print("-" * 70)

        for table_name, csv_file in expected_tables.items():

            csv_df = pd.read_csv(csv_file)
            csv_rows = len(csv_df)

            if table_name not in database_tables:
                print(f"TABLE      : {table_name}")
                print("STATUS     : FAIL")
                print("MESSAGE    : Table not found")
                print("-" * 70)

                failed_tables += 1
                continue

            cursor = connection.cursor()

            cursor.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            )

            database_rows = cursor.fetchone()[0]

            total_database_rows += database_rows

            if csv_rows == database_rows:
                status = "PASS"
                passed_tables += 1
            else:
                status = "FAIL"
                failed_tables += 1

            print(f"TABLE      : {table_name}")
            print(f"CSV ROWS   : {csv_rows}")
            print(f"DB ROWS    : {database_rows}")
            print(f"STATUS     : {status}")
            print("-" * 70)

        cursor = connection.cursor()

        cursor.execute("PRAGMA integrity_check;")

        integrity_result = cursor.fetchone()[0]

    finally:
        connection.close()

    print("\n" + "=" * 70)
    print("DATABASE VERIFICATION SUMMARY")
    print("=" * 70)

    print(f"Total Tables       : {len(expected_tables)}")
    print(f"Passed Tables      : {passed_tables}")
    print(f"Failed Tables      : {failed_tables}")
    print(f"Total Database Rows: {total_database_rows}")
    print(f"Integrity Check    : {integrity_result}")

    if (
        failed_tables == 0
        and integrity_result == "ok"
    ):
        print("\nDATABASE VERIFICATION STATUS: PASSED")
    else:
        print("\nDATABASE VERIFICATION STATUS: REVIEW REQUIRED")

    print("\n" + "=" * 70)
    print("DAY 5 SQLITE DATABASE VERIFICATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    verify_database()