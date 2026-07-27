"""
NIFTY 100 FINANCIAL INTELLIGENCE
DAY 7 - STOCK SCREENER OUTPUT GENERATOR
"""

from pathlib import Path
import sqlite3

import pandas as pd


# =========================================================
# PATH CONFIGURATION
# =========================================================

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = (
    ROOT
    / "db"
    / "n100_financial_intelligence.db"
)

OUTPUT_DIR = ROOT / "output"

OUTPUT_FILE = (
    OUTPUT_DIR
    / "screener_output.xlsx"
)


# =========================================================
# LOAD ANALYSIS DATA
# =========================================================

def load_analysis():
    """
    Load financial analysis data from SQLite database.
    """

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DB_PATH}"
        )

    query = """
        SELECT
            id,
            company_id,
            compounded_sales_growth,
            compounded_profit_growth,
            stock_price_cagr,
            roe
        FROM analysis
    """

    with sqlite3.connect(DB_PATH) as connection:

        df = pd.read_sql_query(
            query,
            connection,
        )

    return df


# =========================================================
# CLEAN FINANCIAL VALUES
# =========================================================

def clean_numeric_column(series):
    """
    Extract percentage numbers from financial text.

    Examples:

    '5 Years: 22%'  -> 22
    'TTM: 47%'      -> 47
    '10 Years: 8%'  -> 8
    '15%'           -> 15
    '-3%'           -> -3

    Invalid/missing values become NaN.
    """

    text = (
        series
        .astype(str)
        .str.strip()
    )

    extracted = text.str.extract(
        r"(-?\d+(?:\.\d+)?)\s*%"
    )[0]

    numeric = pd.to_numeric(
        extracted,
        errors="coerce",
    )

    return numeric


# =========================================================
# PREPARE SCREENER DATA
# =========================================================

def prepare_screener_data(df):
    """
    Clean financial metrics and calculate
    screener pass/fail results.
    """

    result = df.copy()

    metric_columns = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
    ]

    # -----------------------------------------------------
    # Clean percentage columns
    # -----------------------------------------------------

    for column in metric_columns:

        if column in result.columns:

            result[column] = clean_numeric_column(
                result[column]
            )

    # -----------------------------------------------------
    # Screener criteria
    # -----------------------------------------------------

    # Sales growth >= 10%
    result["sales_growth_pass"] = (
        result["compounded_sales_growth"]
        .ge(10)
        .fillna(False)
    )

    # Profit growth >= 10%
    result["profit_growth_pass"] = (
        result["compounded_profit_growth"]
        .ge(10)
        .fillna(False)
    )

    # Stock price CAGR >= 10%
    result["stock_cagr_pass"] = (
        result["stock_price_cagr"]
        .ge(10)
        .fillna(False)
    )

    # ROE >= 15%
    result["roe_pass"] = (
        result["roe"]
        .ge(15)
        .fillna(False)
    )

    # -----------------------------------------------------
    # Count passed criteria
    # -----------------------------------------------------

    pass_columns = [
        "sales_growth_pass",
        "profit_growth_pass",
        "stock_cagr_pass",
        "roe_pass",
    ]

    result["criteria_passed"] = (
        result[pass_columns]
        .sum(axis=1)
        .astype(int)
    )

    # -----------------------------------------------------
    # Score
    # -----------------------------------------------------

    total_criteria = len(pass_columns)

    result["screen_score"] = (
        (
            result["criteria_passed"]
            / total_criteria
        )
        * 100
    ).round(2)

    # -----------------------------------------------------
    # Status
    # -----------------------------------------------------

    def determine_status(criteria_passed):

        if criteria_passed == total_criteria:
            return "PASS"

        if criteria_passed >= 2:
            return "REVIEW"

        return "FAIL"

    result["screen_status"] = (
        result["criteria_passed"]
        .apply(determine_status)
    )

    # -----------------------------------------------------
    # Sort companies
    # -----------------------------------------------------

    result = result.sort_values(
        by=[
            "screen_score",
            "roe",
            "compounded_profit_growth",
            "compounded_sales_growth",
        ],
        ascending=[
            False,
            False,
            False,
            False,
        ],
        na_position="last",
    )

    result = result.reset_index(
        drop=True
    )

    # -----------------------------------------------------
    # Add rank
    # -----------------------------------------------------

    result["screen_rank"] = range(
        1,
        len(result) + 1,
    )

    return result


# =========================================================
# SAVE EXCEL OUTPUT
# =========================================================

def save_excel(df):
    """
    Create Excel workbook containing:

    1. All Companies
    2. Passed
    3. Review
    4. Failed
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    passed = df[
        df["screen_status"] == "PASS"
    ].copy()

    review = df[
        df["screen_status"] == "REVIEW"
    ].copy()

    failed = df[
        df["screen_status"] == "FAIL"
    ].copy()

    # -----------------------------------------------------
    # Write Excel workbook
    # -----------------------------------------------------

    with pd.ExcelWriter(
        OUTPUT_FILE,
        engine="openpyxl",
    ) as writer:

        df.to_excel(
            writer,
            sheet_name="All Companies",
            index=False,
        )

        passed.to_excel(
            writer,
            sheet_name="Passed",
            index=False,
        )

        review.to_excel(
            writer,
            sheet_name="Review",
            index=False,
        )

        failed.to_excel(
            writer,
            sheet_name="Failed",
            index=False,
        )

    # -----------------------------------------------------
    # Terminal summary
    # -----------------------------------------------------

    print()
    print("=" * 70)

    print(
        "NIFTY 100 FINANCIAL INTELLIGENCE"
    )

    print(
        "DAY 7 - STOCK SCREENER OUTPUT"
    )

    print("=" * 70)

    print(
        f"Database: {DB_PATH}"
    )

    print(
        f"Total rows: {len(df)}"
    )

    print(
        f"Passed rows: {len(passed)}"
    )

    print(
        f"Review rows: {len(review)}"
    )

    print(
        f"Failed rows: {len(failed)}"
    )

    print()

    print(
        "Excel created successfully:"
    )

    print(
        OUTPUT_FILE
    )

    print("=" * 70)


# =========================================================
# DISPLAY SAMPLE RESULTS
# =========================================================

def display_results(df):
    """
    Display useful screener columns in terminal.
    """

    columns = [
        "company_id",
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe",
        "criteria_passed",
        "screen_score",
        "screen_status",
        "screen_rank",
    ]

    available_columns = [
        column
        for column in columns
        if column in df.columns
    ]

    print()
    print("TOP SCREENING RESULTS")
    print("-" * 70)

    print(
        df[
            available_columns
        ]
        .head(20)
        .to_string(index=False)
    )

    print("-" * 70)


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 70)

    print(
        "NIFTY 100 FINANCIAL INTELLIGENCE"
    )

    print(
        "DAY 7 - STOCK SCREENER GENERATOR"
    )

    print("=" * 70)

    # -----------------------------------------------------
    # Load
    # -----------------------------------------------------

    print(
        "Loading analysis data..."
    )

    df = load_analysis()

    print(
        f"Analysis rows loaded: {len(df)}"
    )

    # -----------------------------------------------------
    # Empty database check
    # -----------------------------------------------------

    if df.empty:

        print(
            "WARNING: analysis table is empty."
        )

        return

    # -----------------------------------------------------
    # Prepare screener
    # -----------------------------------------------------

    print(
        "Preparing screener data..."
    )

    screened = prepare_screener_data(
        df
    )

    # -----------------------------------------------------
    # Show terminal results
    # -----------------------------------------------------

    display_results(
        screened
    )

    # -----------------------------------------------------
    # Excel
    # -----------------------------------------------------

    print(
        "Generating Excel workbook..."
    )

    save_excel(
        screened
    )

    print()
    print(
        "DAY 7 SCREENER GENERATION COMPLETED."
    )


# =========================================================
# DIRECT RUN
# =========================================================

if __name__ == "__main__":
    main()