from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


# ============================================================
# NIFTY 100 FINANCIAL INTELLIGENCE
# DAY 6 - FINANCIAL METRICS ENGINE
# ============================================================


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_FILE = (
    BASE_DIR
    / "db"
    / "n100_financial_intelligence.db"
)

OUTPUT_DIR = BASE_DIR / "output"

METRICS_FILE = (
    OUTPUT_DIR
    / "company_financial_metrics.csv"
)

RANKING_FILE = (
    OUTPUT_DIR
    / "company_rankings.csv"
)


def safe_numeric(series):
    """
    Convert a pandas Series to numeric values.
    Invalid values are converted to NaN.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


def load_financial_data(connection):
    """
    Load the source financial tables from SQLite.
    """

    print("Loading financial data...")

    companies = pd.read_sql_query(
        """
        SELECT
            id AS company_id,
            company_name,
            roce_percentage,
            roe_percentage
        FROM companies
        """,
        connection
    )

    profit_loss = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            sales,
            operating_profit,
            net_profit,
            eps
        FROM profitandloss
        """,
        connection
    )

    balance_sheet = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            reserves,
            borrowings,
            total_liabilities,
            total_assets
        FROM balancesheet
        """,
        connection
    )

    cash_flow = pd.read_sql_query(
        """
        SELECT
            company_id,
            year,
            operating_activity,
            net_cash_flow
        FROM cashflow
        """,
        connection
    )

    analysis = pd.read_sql_query(
        """
        SELECT
            company_id,
            compounded_sales_growth,
            compounded_profit_growth,
            stock_price_cagr,
            roe
        FROM analysis
        """,
        connection
    )

    print(
        f"Companies Loaded       : {len(companies)}"
    )

    print(
        f"Profit/Loss Rows       : {len(profit_loss)}"
    )

    print(
        f"Balance Sheet Rows     : {len(balance_sheet)}"
    )

    print(
        f"Cash Flow Rows         : {len(cash_flow)}"
    )

    print(
        f"Analysis Rows          : {len(analysis)}"
    )

    return (
        companies,
        profit_loss,
        balance_sheet,
        cash_flow,
        analysis
    )


def prepare_profit_loss(profit_loss):
    """
    Prepare latest profit and loss metrics.
    """

    data = profit_loss.copy()

    numeric_columns = [
        "year",
        "sales",
        "operating_profit",
        "net_profit",
        "eps"
    ]

    for column in numeric_columns:
        data[column] = safe_numeric(
            data[column]
        )

    data = data.sort_values(
        [
            "company_id",
            "year"
        ]
    )

    latest = (
        data
        .dropna(
            subset=["company_id"]
        )
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .copy()
    )

    latest["operating_margin_percentage"] = (
        np.where(
            latest["sales"].ne(0),
            (
                latest["operating_profit"]
                / latest["sales"]
            )
            * 100,
            np.nan
        )
    )

    latest["net_profit_margin_percentage"] = (
        np.where(
            latest["sales"].ne(0),
            (
                latest["net_profit"]
                / latest["sales"]
            )
            * 100,
            np.nan
        )
    )

    latest = latest.rename(
        columns={
            "year": "latest_financial_year",
            "sales": "latest_sales",
            "operating_profit": (
                "latest_operating_profit"
            ),
            "net_profit": "latest_net_profit",
            "eps": "latest_eps"
        }
    )

    return latest[
        [
            "company_id",
            "latest_financial_year",
            "latest_sales",
            "latest_operating_profit",
            "latest_net_profit",
            "latest_eps",
            "operating_margin_percentage",
            "net_profit_margin_percentage"
        ]
    ]


def prepare_balance_sheet(balance_sheet):
    """
    Prepare latest balance sheet metrics.
    """

    data = balance_sheet.copy()

    numeric_columns = [
        "year",
        "reserves",
        "borrowings",
        "total_liabilities",
        "total_assets"
    ]

    for column in numeric_columns:
        data[column] = safe_numeric(
            data[column]
        )

    data = data.sort_values(
        [
            "company_id",
            "year"
        ]
    )

    latest = (
        data
        .dropna(
            subset=["company_id"]
        )
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .copy()
    )

    latest["debt_to_asset_ratio"] = (
        np.where(
            latest["total_assets"].ne(0),
            (
                latest["borrowings"]
                / latest["total_assets"]
            ),
            np.nan
        )
    )

    latest = latest.rename(
        columns={
            "reserves": "latest_reserves",
            "borrowings": "latest_borrowings",
            "total_liabilities": (
                "latest_total_liabilities"
            ),
            "total_assets": (
                "latest_total_assets"
            )
        }
    )

    return latest[
        [
            "company_id",
            "latest_reserves",
            "latest_borrowings",
            "latest_total_liabilities",
            "latest_total_assets",
            "debt_to_asset_ratio"
        ]
    ]


def prepare_cash_flow(cash_flow):
    """
    Prepare latest cash flow metrics.
    """

    data = cash_flow.copy()

    numeric_columns = [
        "year",
        "operating_activity",
        "net_cash_flow"
    ]

    for column in numeric_columns:
        data[column] = safe_numeric(
            data[column]
        )

    data = data.sort_values(
        [
            "company_id",
            "year"
        ]
    )

    latest = (
        data
        .dropna(
            subset=["company_id"]
        )
        .groupby(
            "company_id",
            as_index=False
        )
        .tail(1)
        .copy()
    )

    latest = latest.rename(
        columns={
            "operating_activity": (
                "latest_operating_cash_flow"
            ),
            "net_cash_flow": (
                "latest_net_cash_flow"
            )
        }
    )

    return latest[
        [
            "company_id",
            "latest_operating_cash_flow",
            "latest_net_cash_flow"
        ]
    ]


def prepare_analysis(analysis):
    """
    Prepare growth and CAGR metrics.
    """

    data = analysis.copy()

    numeric_columns = [
        "compounded_sales_growth",
        "compounded_profit_growth",
        "stock_price_cagr",
        "roe"
    ]

    for column in numeric_columns:
        data[column] = safe_numeric(
            data[column]
        )

    data = (
        data
        .dropna(
            subset=["company_id"]
        )
        .drop_duplicates(
            subset=["company_id"],
            keep="last"
        )
    )

    return data


def percentile_score(series):
    """
    Convert a metric to a 0-100 percentile score.
    """

    numeric = safe_numeric(series)

    return (
        numeric
        .rank(
            pct=True,
            method="average"
        )
        .mul(100)
    )


def calculate_financial_score(metrics):
    """
    Calculate the financial intelligence score.
    """

    data = metrics.copy()

    positive_metrics = {
        "sales_growth_score": (
            "compounded_sales_growth"
        ),
        "profit_growth_score": (
            "compounded_profit_growth"
        ),
        "stock_cagr_score": (
            "stock_price_cagr"
        ),
        "roe_score": "roe_percentage",
        "roce_score": "roce_percentage",
        "profit_margin_score": (
            "net_profit_margin_percentage"
        ),
        "cash_flow_score": (
            "latest_operating_cash_flow"
        )
    }

    for score_column, metric_column in (
        positive_metrics.items()
    ):
        data[score_column] = percentile_score(
            data[metric_column]
        )

    debt_score = percentile_score(
        data["debt_to_asset_ratio"]
    )

    data["debt_score"] = 100 - debt_score

    score_columns = [
        "sales_growth_score",
        "profit_growth_score",
        "stock_cagr_score",
        "roe_score",
        "roce_score",
        "profit_margin_score",
        "cash_flow_score",
        "debt_score"
    ]

    data["financial_health_score"] = (
        data[score_columns]
        .mean(
            axis=1,
            skipna=True
        )
        .round(2)
    )

    return data


def assign_rating(score):
    """
    Assign financial health rating.
    """

    if pd.isna(score):
        return "NO DATA"

    if score >= 80:
        return "EXCELLENT"

    if score >= 65:
        return "STRONG"

    if score >= 50:
        return "GOOD"

    if score >= 35:
        return "AVERAGE"

    return "WEAK"


def compute_metrics():
    """
    Execute the Day 6 financial metrics pipeline.
    """

    print("=" * 70)

    print(
        "NIFTY 100 FINANCIAL INTELLIGENCE"
    )

    print(
        "DAY 6 - FINANCIAL METRICS ENGINE"
    )

    print("=" * 70)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    try:
        (
            companies,
            profit_loss,
            balance_sheet,
            cash_flow,
            analysis
        ) = load_financial_data(connection)

        profit_metrics = prepare_profit_loss(
            profit_loss
        )

        balance_metrics = prepare_balance_sheet(
            balance_sheet
        )

        cash_metrics = prepare_cash_flow(
            cash_flow
        )

        analysis_metrics = prepare_analysis(
            analysis
        )

        metrics = companies.copy()

        datasets = [
            profit_metrics,
            balance_metrics,
            cash_metrics,
            analysis_metrics
        ]

        for dataset in datasets:
            metrics = metrics.merge(
                dataset,
                on="company_id",
                how="left"
            )

        numeric_columns = [
            "roce_percentage",
            "roe_percentage",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe"
        ]

        for column in numeric_columns:
            metrics[column] = safe_numeric(
                metrics[column]
            )

        metrics = calculate_financial_score(
            metrics
        )

        metrics["financial_rating"] = (
            metrics[
                "financial_health_score"
            ]
            .apply(assign_rating)
        )

        metrics = metrics.sort_values(
            "financial_health_score",
            ascending=False
        )

        metrics["company_rank"] = range(
            1,
            len(metrics) + 1
        )

        metrics.to_csv(
            METRICS_FILE,
            index=False,
            encoding="utf-8"
        )

        ranking_columns = [
            "company_rank",
            "company_id",
            "company_name",
            "financial_health_score",
            "financial_rating",
            "compounded_sales_growth",
            "compounded_profit_growth",
            "stock_price_cagr",
            "roe_percentage",
            "roce_percentage",
            "net_profit_margin_percentage",
            "debt_to_asset_ratio"
        ]

        rankings = metrics[
            ranking_columns
        ].copy()

        rankings.to_csv(
            RANKING_FILE,
            index=False,
            encoding="utf-8"
        )

        print()
        print("-" * 70)

        print(
            "FINANCIAL METRICS SUMMARY"
        )

        print("-" * 70)

        print(
            f"Companies Analysed : {len(metrics)}"
        )

        print(
            "Metrics File       : "
            f"{METRICS_FILE}"
        )

        print(
            "Ranking File       : "
            f"{RANKING_FILE}"
        )

        print()

        print(
            "TOP 10 FINANCIAL COMPANIES"
        )

        print("-" * 70)

        print(
            rankings[
                [
                    "company_rank",
                    "company_name",
                    "financial_health_score",
                    "financial_rating"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

        print()
        print("-" * 70)

        print(
            "FINANCIAL METRICS STATUS: PASSED"
        )

        print()
        print("=" * 70)

        print(
            "DAY 6 FINANCIAL METRICS COMPLETED"
        )

        print("=" * 70)

        return metrics

    finally:
        connection.close()


if __name__ == "__main__":
    compute_metrics()