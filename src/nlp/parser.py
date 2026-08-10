from pathlib import Path
import re
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PARSED_FILE = OUTPUT_DIR / "analysis_parsed.csv"
FAILURE_FILE = OUTPUT_DIR / "parse_failures.csv"


# ============================================================
# FIND INPUT EXCEL FILE
# ============================================================

def find_input_file():
    """
    Find the most suitable Excel file already available
    in the project.
    """

    candidates = [
        PROJECT_ROOT / "data" / "supporting" / "analysis.xlsx",
        PROJECT_ROOT / "data" / "processed" / "analysis.xlsx",
        PROJECT_ROOT / "data" / "raw" / "analysis.xlsx",
        PROJECT_ROOT / "data" / "supporting" / "financial_ratios.xlsx",
    ]

    for file in candidates:
        if file.exists():
            return file

    raise FileNotFoundError(
        "No suitable Excel input file was found."
    )


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

def normalize_column(value):
    value = str(value).strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


# ============================================================
# IDENTIFY METRIC
# ============================================================

def identify_metric(column_name):

    name = normalize_column(column_name)

    if (
        "sales" in name
        and ("growth" in name or "cagr" in name)
    ):
        return "compounded_sales_growth"

    if (
        "profit" in name
        and ("growth" in name or "cagr" in name)
    ):
        return "compounded_profit_growth"

    if (
        "stock" in name
        and ("price" in name or "cagr" in name)
    ):
        return "stock_price_cagr"

    if name == "roe" or "return_on_equity" in name:
        return "roe"

    return None


# ============================================================
# PARSE TEXT VALUES
# ============================================================

def parse_value(value):

    if pd.isna(value):
        return None

    text = str(value).strip()

    # Example:
    # 10 Years: 21%
    pattern = r"(\d+)\s*Years?\s*:\s*([-+]?\d+(?:\.\d+)?)\s*%"

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE
    )

    if match:

        return {
            "period_years": int(match.group(1)),
            "value_pct": float(match.group(2)),
            "raw_text": text
        }

    # Also support simple percentages:
    # 21%
    simple_pattern = r"([-+]?\d+(?:\.\d+)?)\s*%"

    match = re.search(
        simple_pattern,
        text
    )

    if match:

        return {
            "period_years": None,
            "value_pct": float(match.group(1)),
            "raw_text": text
        }

    return None


# ============================================================
# FIND COMPANY COLUMN
# ============================================================

def find_company_column(df):

    preferred = [
        "company_id",
        "company",
        "company_name",
        "name",
        "ticker",
        "symbol"
    ]

    normalized = {
        normalize_column(col): col
        for col in df.columns
    }

    for name in preferred:

        if name in normalized:
            return normalized[name]

    # Fallback to first column
    return df.columns[0]


# ============================================================
# MAIN PARSER
# ============================================================

def main():

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE")
    print("DAY 29 - NLP ANALYSIS PARSER")
    print("=" * 60)

    input_file = find_input_file()

    print(f"\nInput file:")
    print(input_file)

    df = pd.read_excel(input_file)

    print(f"\nRows: {len(df)}")
    print(f"Columns: {len(df.columns)}")

    print("\nAvailable columns:")

    for column in df.columns:
        print(f"  - {column}")

    company_column = find_company_column(df)

    print(f"\nCompany column: {company_column}")

    parsed_rows = []
    failures = []

    # --------------------------------------------------------
    # PROCESS EACH ROW
    # --------------------------------------------------------

    for _, row in df.iterrows():

        company_id = row[company_column]

        for column in df.columns:

            metric = identify_metric(column)

            if metric is None:
                continue

            raw_value = row[column]

            parsed = parse_value(raw_value)

            if parsed is None:

                failures.append({
                    "company_id": company_id,
                    "metric_type": metric,
                    "source_column": column,
                    "raw_text": raw_value,
                    "reason": "Unable to parse value"
                })

                continue

            parsed_rows.append({

                "company_id": company_id,

                "metric_type": metric,

                "period_years":
                    parsed["period_years"],

                "value_pct":
                    parsed["value_pct"],

                "raw_text":
                    parsed["raw_text"]
            })

    # --------------------------------------------------------
    # CREATE DATAFRAMES
    # --------------------------------------------------------

    parsed_df = pd.DataFrame(
        parsed_rows,
        columns=[
            "company_id",
            "metric_type",
            "period_years",
            "value_pct",
            "raw_text"
        ]
    )

    failure_df = pd.DataFrame(
        failures,
        columns=[
            "company_id",
            "metric_type",
            "source_column",
            "raw_text",
            "reason"
        ]
    )

    # --------------------------------------------------------
    # SAVE OUTPUT
    # --------------------------------------------------------

    parsed_df.to_csv(
        PARSED_FILE,
        index=False
    )

    failure_df.to_csv(
        FAILURE_FILE,
        index=False
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PARSER COMPLETED")
    print("=" * 60)

    print(f"\nParsed records : {len(parsed_df)}")
    print(f"Failures       : {len(failure_df)}")

    print(f"\nCreated:")
    print(f"  {PARSED_FILE}")
    print(f"  {FAILURE_FILE}")

    if len(parsed_df) > 0:

        print("\nMetric counts:")

        print(
            parsed_df[
                "metric_type"
            ].value_counts()
        )

        print("\nFirst 10 parsed records:")

        print(
            parsed_df.head(10).to_string(
                index=False
            )
        )

    else:

        print(
            "\nWARNING: No matching CAGR/ROE "
            "values were found."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()