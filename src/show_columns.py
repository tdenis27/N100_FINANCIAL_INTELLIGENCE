import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = (
    BASE_DIR
    / "db"
    / "n100_financial_intelligence.db"
)

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "database_columns.txt"
)


def show_database_columns():
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        )

        tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        output_lines = []

        output_lines.append(
            "=" * 70
        )

        output_lines.append(
            "NIFTY 100 FINANCIAL INTELLIGENCE"
        )

        output_lines.append(
            "DATABASE TABLE AND COLUMN SCHEMA"
        )

        output_lines.append(
            "=" * 70
        )

        output_lines.append("")

        output_lines.append(
            f"TOTAL TABLES: {len(tables)}"
        )

        output_lines.append("")

        for table in tables:

            cursor.execute(
                f'PRAGMA table_info("{table}")'
            )

            table_info = cursor.fetchall()

            columns = [
                row[1]
                for row in table_info
            ]

            output_lines.append(
                "-" * 70
            )

            output_lines.append(
                f"TABLE: {table}"
            )

            output_lines.append(
                f"TOTAL COLUMNS: {len(columns)}"
            )

            output_lines.append(
                "COLUMNS:"
            )

            for index, column in enumerate(
                columns,
                start=1
            ):
                output_lines.append(
                    f"  {index}. {column}"
                )

            output_lines.append("")

        output_lines.append(
            "=" * 70
        )

        output_lines.append(
            "DATABASE SCHEMA INSPECTION COMPLETED"
        )

        output_lines.append(
            "=" * 70
        )

        output_text = "\n".join(
            output_lines
        )

        print(output_text)

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        OUTPUT_FILE.write_text(
            output_text,
            encoding="utf-8"
        )

        print()
        print(
            f"Schema saved to: {OUTPUT_FILE}"
        )

    finally:
        connection.close()


if __name__ == "__main__":
    show_database_columns()