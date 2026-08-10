# ============================================================
# N100 FINANCIAL INTELLIGENCE
# DAY 29 - NLP ANALYSIS PARSER
# ============================================================

import os
import re
import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = r"C:\N100_FINANCIAL_INTELLIGENCE"

RAW_DIR = os.path.join(
    BASE_DIR,
    "data",
    "raw"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "output"
)

PARSED_FILE = os.path.join(
    OUTPUT_DIR,
    "analysis_parsed.csv"
)

FAILURE_FILE = os.path.join(
    OUTPUT_DIR,
    "parse_failures.csv"
)


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# INPUT FILE SEARCH
# ============================================================

def find_input_file():

    print("\nSearching for input file...")

    # --------------------------------------------------------
    # Preferred raw Excel file
    # --------------------------------------------------------

    preferred_file = os.path.join(
        RAW_DIR,
        "analysis.xlsx"
    )

    if os.path.exists(preferred_file):

        print("Using raw Excel file:")
        print(preferred_file)

        return preferred_file

    # --------------------------------------------------------
    # Search raw directory
    # --------------------------------------------------------

    if os.path.exists(RAW_DIR):

        excel_files = [
            file
            for file in os.listdir(RAW_DIR)
            if file.lower().endswith((".xlsx", ".xls"))
        ]

        if excel_files:

            selected = os.path.join(
                RAW_DIR,
                excel_files[0]
            )

            print("Using discovered Excel file:")
            print(selected)

            return selected

    # --------------------------------------------------------
    # Search entire project
    # --------------------------------------------------------

    for root, dirs, files in os.walk(BASE_DIR):

        # Ignore virtual environment and cache directories
        dirs[:] = [
            d for d in dirs
            if d not in {
                "venv",
                "__pycache__",
                ".git"
            }
        ]

        for file in files:

            if (
                file.lower() == "analysis.xlsx"
                or file.lower() == "analysis.xls"
            ):

                selected = os.path.join(
                    root,
                    file
                )

                print("Found analysis file:")
                print(selected)

                return selected

    raise FileNotFoundError(
        "Could not find analysis.xlsx anywhere in the project."
    )


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column(value):

    if value is None:
        return ""

    text = str(value)

    text = text.lower().strip()

    # Replace common symbols
    text = text.replace("%", " percent ")
    text = text.replace("&", " and ")

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text
    )

    # Remove repeated underscores
    text = re.sub(
        r"_+",
        "_",
        text
    )

    return text.strip("_")


# ============================================================
# FIND REAL HEADER ROW
# ============================================================

def find_header_row(raw_df):

    print("\nSearching for real header row...")

    # Words expected in analysis.xlsx
    header_keywords = [
        "company",
        "company_id",
        "sales",
        "profit",
        "growth",
        "roe",
        "stock",
        "price"
    ]

    best_row = None
    best_score = -1

    # Inspect first 15 rows
    max_rows = min(
        len(raw_df),
        15
    )

    for row_index in range(max_rows):

        row_values = raw_df.iloc[row_index].tolist()

        row_text = " ".join(
            str(value).lower()
            for value in row_values
            if pd.notna(value)
        )

        score = 0

        for keyword in header_keywords:

            if keyword in row_text:
                score += 1

        if score > best_score:

            best_score = score
            best_row = row_index

    # If no useful header was detected,
    # assume row 1 is header
    if best_row is None or best_score <= 0:

        best_row = 0

    print(
        f"Detected header row: Excel row {best_row + 1}"
    )

    return best_row


# ============================================================
# FIND COMPANY COLUMN
# ============================================================

def find_company_column(df):

    preferred = [
        "company_id",
        "company",
        "company_name",
        "symbol",
        "ticker",
        "stock",
        "name"
    ]

    normalized = {
        normalize_column(col): col
        for col in df.columns
    }

    # --------------------------------------------------------
    # Exact matches
    # --------------------------------------------------------

    for name in preferred:

        if name in normalized:

            return normalized[name]

    # --------------------------------------------------------
    # Partial matches
    # --------------------------------------------------------

    for normalized_name, original_name in normalized.items():

        if (
            "company" in normalized_name
            or "ticker" in normalized_name
            or "symbol" in normalized_name
        ):

            return original_name

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return df.columns[0]


# ============================================================
# IDENTIFY METRIC
# ============================================================

def identify_metric(column):

    normalized = normalize_column(column)

    # --------------------------------------------------------
    # COMPOUNDED SALES GROWTH
    # --------------------------------------------------------

    if (
        "sales" in normalized
        and "growth" in normalized
    ):

        return "compounded_sales_growth"

    # --------------------------------------------------------
    # COMPOUNDED PROFIT GROWTH
    # --------------------------------------------------------

    if (
        "profit" in normalized
        and "growth" in normalized
    ):

        return "compounded_profit_growth"

    # --------------------------------------------------------
    # STOCK PRICE CAGR
    # --------------------------------------------------------

    if (
        (
            "stock" in normalized
            and "price" in normalized
        )
        or "stock_price_cagr" in normalized
        or "price_cagr" in normalized
    ):

        return "stock_price_cagr"

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    if (
        normalized == "roe"
        or normalized.startswith("roe_")
        or "_roe" in normalized
    ):

        return "roe"

    return None


# ============================================================
# PARSE PERIOD
# ============================================================

def parse_period(text):

    if text is None:
        return None

    text = str(text)

    # Examples:
    # 10 Years
    # 5 Years
    # 3 Years
    # 1 Year
    # Last Year
    # TTM

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*Years?",
        text,
        re.IGNORECASE
    )

    if match:

        return float(
            match.group(1)
        )

    # --------------------------------------------------------
    # Last Year
    # --------------------------------------------------------

    if re.search(
        r"last\s*year",
        text,
        re.IGNORECASE
    ):

        return 1.0

    # --------------------------------------------------------
    # TTM
    # --------------------------------------------------------

    if re.search(
        r"\bttm\b",
        text,
        re.IGNORECASE
    ):

        return 0.0

    return None


# ============================================================
# PARSE SINGLE VALUE
# ============================================================

def parse_single_value(text):

    if text is None:
        return None

    if pd.isna(text):
        return None

    text = str(text).strip()

    if not text:
        return None

    # --------------------------------------------------------
    # Convert unusual dash characters
    # --------------------------------------------------------

    text = text.replace(
        "–",
        "-"
    )

    text = text.replace(
        "—",
        "-"
    )

    # --------------------------------------------------------
    # Remove commas from numbers
    # --------------------------------------------------------

    clean_text = text.replace(
        ",",
        ""
    )

    # --------------------------------------------------------
    # Find percentage
    # --------------------------------------------------------

    percentage_match = re.search(
        r"(-?\d+(?:\.\d+)?)\s*%",
        clean_text
    )

    if percentage_match:

        value_pct = float(
            percentage_match.group(1)
        )

    else:

        # ----------------------------------------------------
        # Try normal numeric value
        # ----------------------------------------------------

        number_match = re.search(
            r"(-?\d+(?:\.\d+)?)",
            clean_text
        )

        if not number_match:

            return None

        value_pct = float(
            number_match.group(1)
        )

    # --------------------------------------------------------
    # Period
    # --------------------------------------------------------

    period_years = parse_period(
        text
    )

    return {
        "period_years": period_years,
        "value_pct": value_pct,
        "raw_text": text
    }


# ============================================================
# PARSE VALUE
# ============================================================

def parse_value(raw_value):

    if raw_value is None:
        return None

    if pd.isna(raw_value):
        return None

    text = str(raw_value).strip()

    if not text:
        return None

    # --------------------------------------------------------
    # Some cells can contain multiple values.
    #
    # Example:
    #
    # 10 Years: 21%, 5 Years: 24%, 3 Years: 17%
    #
    # We return the first value here.
    # The main parser below also handles all occurrences.
    # --------------------------------------------------------

    return parse_single_value(
        text
    )


# ============================================================
# PARSE ALL VALUES FROM CELL
# ============================================================

def parse_all_values(raw_value):

    if raw_value is None:
        return []

    if pd.isna(raw_value):
        return []

    text = str(raw_value).strip()

    if not text:
        return []

    results = []

    # --------------------------------------------------------
    # Pattern:
    #
    # 10 Years: 21%
    # 5 Years: 24%
    # 3 Years: 17%
    # TTM: 43%
    # Last Year: 12%
    #
    # --------------------------------------------------------

    pattern = re.compile(
        r"""
        (?:
            (\d+(?:\.\d+)?)\s*Years?
            |
            (Last\s*Year)
            |
            (TTM)
        )
        \s*
        :
        \s*
        (-?\d+(?:\.\d+)?)
        \s*%
        """,
        re.IGNORECASE | re.VERBOSE
    )

    matches = pattern.findall(
        text
    )

    # --------------------------------------------------------
    # If structured pattern found
    # --------------------------------------------------------

    if matches:

        for match in matches:

            years_number = match[0]
            last_year = match[1]
            ttm = match[2]
            percentage = match[3]

            if years_number:

                period_years = float(
                    years_number
                )

            elif last_year:

                period_years = 1.0

            elif ttm:

                period_years = 0.0

            else:

                period_years = None

            results.append({

                "period_years":
                    period_years,

                "value_pct":
                    float(percentage),

                "raw_text":
                    text
            })

        return results

    # --------------------------------------------------------
    # Alternate pattern:
    #
    # 21%, 10 Years: 22%
    #
    # --------------------------------------------------------

    percent_matches = re.findall(
        r"(-?\d+(?:\.\d+)?)\s*%",
        text
    )

    if percent_matches:

        for percentage in percent_matches:

            # Find nearby period
            period_years = parse_period(
                text
            )

            results.append({

                "period_years":
                    period_years,

                "value_pct":
                    float(percentage),

                "raw_text":
                    text
            })

        return results

    # --------------------------------------------------------
    # Single numeric value
    # --------------------------------------------------------

    single = parse_single_value(
        text
    )

    if single:

        return [
            single
        ]

    return []


# ============================================================
# CLEAN COMPANY ID
# ============================================================

def clean_company_id(value):

    if value is None:
        return ""

    if pd.isna(value):
        return ""

    text = str(value).strip()

    # Remove accidental .0 from numeric IDs
    if text.endswith(".0"):

        text = text[:-2]

    return text


# ============================================================
# LOAD EXCEL WITH HEADER DETECTION
# ============================================================

def load_analysis_excel(input_file):

    print("\nReading Excel file...")

    # Read without assuming header
    raw_df = pd.read_excel(
        input_file,
        header=None
    )

    print(
        f"\nRaw rows: {len(raw_df)}"
    )

    print(
        f"Raw columns: {len(raw_df.columns)}"
    )

    # --------------------------------------------------------
    # Find real header
    # --------------------------------------------------------

    header_row = find_header_row(
        raw_df
    )

    # --------------------------------------------------------
    # Create dataframe from detected header
    # --------------------------------------------------------

    df = pd.read_excel(
        input_file,
        header=header_row
    )

    # --------------------------------------------------------
    # Remove completely empty columns
    # --------------------------------------------------------

    df = df.dropna(
        axis=1,
        how="all"
    )

    # --------------------------------------------------------
    # Remove completely empty rows
    # --------------------------------------------------------

    df = df.dropna(
        axis=0,
        how="all"
    )

    # --------------------------------------------------------
    # Clean column names
    # --------------------------------------------------------

    cleaned_columns = []

    for index, column in enumerate(df.columns):

        if pd.isna(column):

            cleaned_columns.append(
                f"Unnamed_{index}"
            )

        else:

            cleaned_columns.append(
                str(column).strip()
            )

    df.columns = cleaned_columns

    return df


# ============================================================
# MAIN PARSER
# ============================================================

def main():

    print("=" * 60)
    print("N100 FINANCIAL INTELLIGENCE")
    print("DAY 29 - NLP ANALYSIS PARSER")
    print("=" * 60)

    # --------------------------------------------------------
    # FIND INPUT FILE
    # --------------------------------------------------------

    input_file = find_input_file()

    print("\nInput file:")
    print(input_file)

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = load_analysis_excel(
        input_file
    )

    print(
        f"\nRows: {len(df)}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # AVAILABLE COLUMNS
    # --------------------------------------------------------

    print("\nAvailable columns:")

    for column in df.columns:

        metric = identify_metric(
            column
        )

        if metric:

            print(
                f"  - {column}  -->  {metric}"
            )

        else:

            print(
                f"  - {column}  -->  NOT A METRIC"
            )

    # --------------------------------------------------------
    # FIND COMPANY COLUMN
    # --------------------------------------------------------

    company_column = find_company_column(
        df
    )

    print(
        f"\nCompany column: {company_column}"
    )

    # --------------------------------------------------------
    # FIND METRIC COLUMNS
    # --------------------------------------------------------

    metric_columns = []

    for column in df.columns:

        metric = identify_metric(
            column
        )

        if metric is not None:

            metric_columns.append(
                (
                    column,
                    metric
                )
            )

    print("\nDetected metric columns:")

    if metric_columns:

        for column, metric in metric_columns:

            print(
                f"  - {column} --> {metric}"
            )

    else:

        print("NONE")

    # --------------------------------------------------------
    # STOP IF NO METRICS
    # --------------------------------------------------------

    if not metric_columns:

        print(
            "\nERROR: No metric columns were detected."
        )

        print(
            "\nPlease check the Excel header structure."
        )

        return

    # --------------------------------------------------------
    # PREPARE OUTPUT
    # --------------------------------------------------------

    parsed_rows = []

    failures = []

    # --------------------------------------------------------
    # PROCESS EACH ROW
    # --------------------------------------------------------

    print(
        "\nProcessing rows..."
    )

    for row_number, row in df.iterrows():

        company_id = clean_company_id(
            row[company_column]
        )

        # Skip blank company IDs
        if not company_id:

            continue

        # ----------------------------------------------------
        # PROCESS EACH METRIC COLUMN
        # ----------------------------------------------------

        for column, metric in metric_columns:

            raw_value = row[column]

            # ------------------------------------------------
            # Parse all values
            # ------------------------------------------------

            parsed_values = parse_all_values(
                raw_value
            )

            # ------------------------------------------------
            # No values found
            # ------------------------------------------------

            if not parsed_values:

                # Only register failure if cell has content
                if (
                    raw_value is not None
                    and not pd.isna(raw_value)
                    and str(raw_value).strip()
                ):

                    failures.append({

                        "company_id":
                            company_id,

                        "metric_type":
                            metric,

                        "source_column":
                            column,

                        "raw_text":
                            raw_value,

                        "reason":
                            "Unable to parse value"
                    })

                continue

            # ------------------------------------------------
            # Add parsed values
            # ------------------------------------------------

            for parsed in parsed_values:

                parsed_rows.append({

                    "company_id":
                        company_id,

                    "metric_type":
                        metric,

                    "period_years":
                        parsed["period_years"],

                    "value_pct":
                        parsed["value_pct"],

                    "raw_text":
                        parsed["raw_text"]
                })

    # ========================================================
    # CREATE DATAFRAMES
    # ========================================================

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

    # ========================================================
    # REMOVE DUPLICATES
    # ========================================================

    if not parsed_df.empty:

        parsed_df = parsed_df.drop_duplicates()

    if not failure_df.empty:

        failure_df = failure_df.drop_duplicates()

    # ========================================================
    # SAVE OUTPUT
    # ========================================================

    parsed_df.to_csv(
        PARSED_FILE,
        index=False,
        encoding="utf-8"
    )

    failure_df.to_csv(
        FAILURE_FILE,
        index=False,
        encoding="utf-8"
    )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("PARSER COMPLETED")
    print("=" * 60)

    print(
        f"\nParsed records : {len(parsed_df)}"
    )

    print(
        f"Failures       : {len(failure_df)}"
    )

    print("\nCreated:")

    print(
        f"  {PARSED_FILE}"
    )

    print(
        f"  {FAILURE_FILE}"
    )

    # ========================================================
    # SHOW SAMPLE
    # ========================================================

    if not parsed_df.empty:

        print(
            "\nFirst 15 parsed records:"
        )

        print(
            parsed_df.head(15).to_string(
                index=False
            )
        )

        print(
            "\nRecords by metric:"
        )

        metric_summary = (
            parsed_df
            .groupby("metric_type")
            .size()
            .sort_values(
                ascending=False
            )
        )

        print(
            metric_summary.to_string()
        )

        print(
            "\nCompanies parsed:"
        )

        print(
            parsed_df["company_id"]
            .nunique()
        )

    else:

        print(
            "\nWARNING: No records were parsed."
        )

        print(
            "\nCheck the detected metric columns above."
        )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()