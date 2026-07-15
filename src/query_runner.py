from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent

DB_FILE = (
    BASE_DIR
    / "db"
    / "n100_financial_intelligence.db"
)

QUERY_FILE = (
    BASE_DIR
    / "db"
    / "queries.sql"
)


def remove_sql_comments(sql_text):
    """Remove SQL single-line comments."""

    cleaned_lines = []

    for line in sql_text.splitlines():
        stripped_line = line.strip()

        if stripped_line.startswith("--"):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def load_queries():
    """Load SQL statements from queries.sql."""

    sql_text = QUERY_FILE.read_text(
        encoding="utf-8"
    )

    sql_text = remove_sql_comments(sql_text)

    queries = []

    for statement in sql_text.split(";"):
        statement = statement.strip()

        if not statement:
            continue

        queries.append(statement)

    return queries


def run_queries():
    """Run all SQLite analytics queries."""

    print("=" * 70)
    print("NIFTY 100 FINANCIAL INTELLIGENCE")
    print("DAY 5 - SQL ANALYTICS QUERY RUNNER")
    print("=" * 70)

    if not DB_FILE.exists():
        print("\nERROR: Database file not found.")
        print(f"DATABASE: {DB_FILE}")
        return

    if not QUERY_FILE.exists():
        print("\nERROR: queries.sql not found.")
        print(f"QUERY FILE: {QUERY_FILE}")
        return

    queries = load_queries()

    print(
        f"\nTOTAL SQL QUERIES FOUND: "
        f"{len(queries)}"
    )

    connection = sqlite3.connect(DB_FILE)

    cursor = connection.cursor()

    passed_queries = 0
    failed_queries = 0

    try:

        for query_number, query in enumerate(
            queries,
            start=1,
        ):

            print("\n" + "-" * 70)

            print(
                f"QUERY {query_number:02d}"
            )

            print("-" * 70)

            try:

                cursor.execute(query)

                if cursor.description is None:
                    rows = []
                    column_names = []
                else:
                    rows = cursor.fetchall()

                    column_names = [
                        description[0]
                        for description in cursor.description
                    ]

                if column_names:

                    print(
                        "COLUMNS : "
                        + " | ".join(column_names)
                    )

                print(
                    f"ROWS    : {len(rows)}"
                )

                for row in rows[:10]:
                    print(row)

                if len(rows) > 10:

                    remaining_rows = (
                        len(rows) - 10
                    )

                    print(
                        f"... {remaining_rows} "
                        "more rows"
                    )

                print(
                    "STATUS  : PASS"
                )

                passed_queries += 1

            except sqlite3.Error as error:

                print(
                    f"ERROR   : {error}"
                )

                print(
                    "STATUS  : FAIL"
                )

                print(
                    "SQL     :"
                )

                print(query[:500])

                failed_queries += 1

    finally:

        connection.close()

    print("\n" + "=" * 70)

    print(
        "SQL QUERY EXECUTION SUMMARY"
    )

    print("=" * 70)

    print(
        f"Total Queries  : {len(queries)}"
    )

    print(
        f"Passed Queries : {passed_queries}"
    )

    print(
        f"Failed Queries : {failed_queries}"
    )

    if failed_queries == 0:

        print(
            "\nSQL ANALYTICS STATUS: PASSED"
        )

    else:

        print(
            "\nSQL ANALYTICS STATUS: "
            "REVIEW REQUIRED"
        )

    print("\n" + "=" * 70)

    print(
        "DAY 5 SQL ANALYTICS "
        "QUERY EXECUTION COMPLETED"
    )

    print("=" * 70)


if __name__ == "__main__":
    run_queries()