from pathlib import Path
from ratios import *
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

METRICS_FILE = OUTPUT_DIR / "company_financial_metrics.csv"
RANKINGS_FILE = OUTPUT_DIR / "company_rankings.csv"


def verify_financial_metrics():
    print("=" * 70)
    print("NIFTY 100 FINANCIAL INTELLIGENCE")
    print("DAY 6 - FINANCIAL METRICS VERIFICATION")
    print("=" * 70)

    failed_checks = 0

    # ------------------------------------------------------------
    # CHECK 1: OUTPUT FILES
    # ------------------------------------------------------------
    print("\n[CHECK 1] OUTPUT FILE VERIFICATION")
    print("-" * 70)

    required_files = [
        METRICS_FILE,
        RANKINGS_FILE,
    ]

    for file_path in required_files:
        if file_path.exists():
            print(f"PASS : {file_path.name} found")
        else:
            print(f"FAIL : {file_path.name} not found")
            failed_checks += 1

    if failed_checks > 0:
        print("\nFINANCIAL METRICS VERIFICATION STATUS: FAILED")
        return

    # ------------------------------------------------------------
    # LOAD OUTPUT FILES
    # ------------------------------------------------------------
    metrics_df = pd.read_csv(METRICS_FILE)
    rankings_df = pd.read_csv(RANKINGS_FILE)

    # ------------------------------------------------------------
    # CHECK 2: DATASET SIZE
    # ------------------------------------------------------------
    print("\n[CHECK 2] DATASET SIZE")
    print("-" * 70)

    print(f"Metrics Rows    : {len(metrics_df)}")
    print(f"Metrics Columns : {len(metrics_df.columns)}")
    print(f"Ranking Rows    : {len(rankings_df)}")
    print(f"Ranking Columns : {len(rankings_df.columns)}")

    if len(metrics_df) > 0:
        print("PASS : Metrics dataset contains records")
    else:
        print("FAIL : Metrics dataset is empty")
        failed_checks += 1

    if len(rankings_df) > 0:
        print("PASS : Rankings dataset contains records")
    else:
        print("FAIL : Rankings dataset is empty")
        failed_checks += 1

    # ------------------------------------------------------------
    # CHECK 3: COMPANY ID UNIQUENESS
    # ------------------------------------------------------------
    print("\n[CHECK 3] COMPANY ID UNIQUENESS")
    print("-" * 70)

    if "company_id" in metrics_df.columns:
        duplicate_ids = metrics_df["company_id"].duplicated().sum()

        print(f"Duplicate Company IDs : {duplicate_ids}")

        if duplicate_ids == 0:
            print("PASS : Company IDs are unique")
        else:
            print("FAIL : Duplicate company IDs found")
            failed_checks += 1
    else:
        print("FAIL : company_id column not found")
        failed_checks += 1

    # ------------------------------------------------------------
    # CHECK 4: METRIC COLUMN VALIDATION
    # ------------------------------------------------------------
    print("\n[CHECK 4] METRIC COLUMN VALIDATION")
    print("-" * 70)

    score_columns = [
        column
        for column in metrics_df.columns
        if column.endswith("_score")
    ]

    print(f"Score Columns Found : {len(score_columns)}")

    for column in score_columns:
        print(f"PASS : {column}")

    if len(score_columns) > 0:
        print("PASS : Financial metric score columns found")
    else:
        print("FAIL : No financial score columns found")
        failed_checks += 1

    # ------------------------------------------------------------
    # CHECK 5: SCORE RANGE VALIDATION
    # ------------------------------------------------------------
    print("\n[CHECK 5] SCORE RANGE VALIDATION")
    print("-" * 70)

    invalid_score_columns = []

    for column in score_columns:
        numeric_values = pd.to_numeric(
            metrics_df[column],
            errors="coerce",
        )

        valid_values = numeric_values.dropna()

        if valid_values.empty:
            print(f"INFO : {column} has no numeric values")
            continue

        minimum_score = valid_values.min()
        maximum_score = valid_values.max()

        print(
            f"{column:<25} "
            f"MIN={minimum_score} "
            f"MAX={maximum_score}"
        )

        if valid_values.between(0, 100).all():
            print(f"PASS : {column} score range valid")
        else:
            print(f"FAIL : {column} score range invalid")
            invalid_score_columns.append(column)

    if invalid_score_columns:
        failed_checks += len(invalid_score_columns)

    # ------------------------------------------------------------
    # CHECK 6: RANKING ORDER
    # ------------------------------------------------------------
    print("\n[CHECK 6] COMPANY RANKING ORDER")
    print("-" * 70)

    ranking_score_column = None

    preferred_score_columns = [
        "overall_score",
        "composite_score",
        "total_score",
        "score",
    ]

    for column in preferred_score_columns:
        if column in rankings_df.columns:
            ranking_score_column = column
            break

    if ranking_score_column is None:
        ranking_score_candidates = [
            column
            for column in rankings_df.columns
            if "score" in column.lower()
        ]

        if ranking_score_candidates:
            ranking_score_column = ranking_score_candidates[0]

    if ranking_score_column is not None:
        print(
            f"Ranking Score Column : "
            f"{ranking_score_column}"
        )

        ranking_scores = pd.to_numeric(
            rankings_df[ranking_score_column],
            errors="coerce",
        )

        if ranking_scores.is_monotonic_decreasing:
            print("PASS : Companies are sorted by score")
        else:
            print("FAIL : Company ranking order is incorrect")
            failed_checks += 1
    else:
        print("FAIL : Ranking score column not found")
        failed_checks += 1

    # ------------------------------------------------------------
    # CHECK 7: TOP 10 COMPANY RANKINGS
    # ------------------------------------------------------------
    print("\n[CHECK 7] TOP 10 COMPANY RANKINGS")
    print("-" * 70)

    top_10 = rankings_df.head(10)

    display_columns = []

    for column in [
        "company_id",
        "company_name",
        ranking_score_column,
        "investment_rating",
        "rating",
    ]:
        if (
            column is not None
            and column in top_10.columns
            and column not in display_columns
        ):
            display_columns.append(column)

    print(
        top_10[display_columns].to_string(
            index=False
        )
    )

    # ------------------------------------------------------------
    # FINAL STATUS
    # ------------------------------------------------------------
    print("\n" + "=" * 70)

    if failed_checks == 0:
        print(
            "FINANCIAL METRICS VERIFICATION STATUS: PASSED"
        )
    else:
        print(
            "FINANCIAL METRICS VERIFICATION STATUS: "
            "REVIEW REQUIRED"
        )

    print("\n" + "=" * 70)
    print(
        "DAY 6 FINANCIAL METRICS "
        "VERIFICATION COMPLETED"
    )
    print("=" * 70)


if __name__ == "__main__":
    verify_financial_metrics()
    
    

def test_net_profit_margin():
    assert net_profit_margin(100, 1000) == 10.0

def test_operating_profit_margin():
    assert operating_profit_margin(200, 1000) == 20.0

def test_return_on_equity():
    assert return_on_equity(100, 500) == 20.0

def test_return_on_assets():
    assert return_on_assets(100, 1000) == 10.0