from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


from ratios import (
    net_profit_margin,
    operating_profit_margin,
    return_on_equity,
    return_on_capital_employed,
    return_on_assets,
    asset_turnover_ratio,
    debt_to_equity,
    interest_coverage,
    net_debt,
    operating_cash_flow_ratio,
    free_cash_flow_ratio,
    earnings_per_share,
    dividend_payout_ratio,
    book_value_per_share,
)


from cagr import (
    revenue_cagr,
    pat_cagr,
    eps_cagr,
)

from cashflow_kpis import (
    free_cash_flow,
    operating_cash_flow_ratio as cashflow_kpi_ocf_ratio,
    cfo_quality_score,
    capex_intensity,
    fcf_conversion_ratio,
    capital_allocation_pattern,
)


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
            investing_activity,
            financing_activity,
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
        "investing_activity",
        "financing_activity",
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
            "investing_activity": (
                "latest_investing_cash_flow"
            ),
            "financing_activity": (
                "latest_financing_cash_flow"
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
            "latest_investing_cash_flow",
            "latest_financing_cash_flow",
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


def prepare_cagr_metrics(profit_loss):
    """
    Calculate Revenue, PAT (net profit) and EPS CAGR per company
    using the earliest and latest reported years available in
    the profit and loss data.
    """

    data = profit_loss.copy()

    numeric_columns = [
        "year",
        "sales",
        "net_profit",
        "eps"
    ]

    for column in numeric_columns:
        data[column] = safe_numeric(
            data[column]
        )

    data = data.dropna(
        subset=[
            "company_id",
            "year"
        ]
    )

    data = data.sort_values(
        [
            "company_id",
            "year"
        ]
    )

    first_year = (
        data
        .groupby(
            "company_id",
            as_index=False
        )
        .first()
    )

    last_year = (
        data
        .groupby(
            "company_id",
            as_index=False
        )
        .last()
    )

    spans = first_year.merge(
        last_year,
        on="company_id",
        suffixes=("_start", "_end")
    )

    spans["num_years"] = (
        spans["year_end"]
        - spans["year_start"]
    )

    def _safe_cagr(function, start_value, end_value, num_years):
        if (
            pd.isna(start_value)
            or pd.isna(end_value)
            or pd.isna(num_years)
            or num_years <= 0
            or start_value <= 0
        ):
            return np.nan

        return function(
            start_value,
            end_value,
            num_years
        )

    spans["revenue_cagr_percentage"] = spans.apply(
        lambda row: _safe_cagr(
            revenue_cagr,
            row["sales_start"],
            row["sales_end"],
            row["num_years"]
        ),
        axis=1
    )

    spans["pat_cagr_percentage"] = spans.apply(
        lambda row: _safe_cagr(
            pat_cagr,
            row["net_profit_start"],
            row["net_profit_end"],
            row["num_years"]
        ),
        axis=1
    )

    spans["eps_cagr_percentage"] = spans.apply(
        lambda row: _safe_cagr(
            eps_cagr,
            row["eps_start"],
            row["eps_end"],
            row["num_years"]
        ),
        axis=1
    )

    return spans[
        [
            "company_id",
            "num_years",
            "revenue_cagr_percentage",
            "pat_cagr_percentage",
            "eps_cagr_percentage"
        ]
    ]


def prepare_cashflow_kpis(cash_flow, profit_loss, balance_sheet):
    """
    Calculate cash-flow quality KPIs per company using the latest
    reported year of cash flow, profit and loss, and balance sheet
    data.

    ASSUMPTION: operating_cash_flow_ratio() expects
    current_liabilities, but the balancesheet table only exposes
    total_liabilities in this pipeline. total_liabilities is used
    as a proxy below -- swap in a real current_liabilities column
    if one exists in your schema.
    """

    cash_data = cash_flow.copy()

    cash_numeric_columns = [
        "year",
        "operating_activity",
        "investing_activity",
        "financing_activity"
    ]

    for column in cash_numeric_columns:
        cash_data[column] = safe_numeric(
            cash_data[column]
        )

    cash_data = cash_data.dropna(
        subset=["company_id", "year"]
    )

    cash_data = cash_data.sort_values(
        ["company_id", "year"]
    )

    latest_cash = (
        cash_data
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )

    profit_data = profit_loss.copy()

    profit_numeric_columns = [
        "year",
        "sales",
        "operating_profit",
        "net_profit"
    ]

    for column in profit_numeric_columns:
        profit_data[column] = safe_numeric(
            profit_data[column]
        )

    profit_data = profit_data.dropna(
        subset=["company_id", "year"]
    )

    profit_data = profit_data.sort_values(
        ["company_id", "year"]
    )

    latest_profit = (
        profit_data
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )

    balance_data = balance_sheet.copy()

    balance_data["year"] = safe_numeric(
        balance_data["year"]
    )

    balance_data["total_liabilities"] = safe_numeric(
        balance_data["total_liabilities"]
    )

    balance_data = balance_data.dropna(
        subset=["company_id", "year"]
    )

    balance_data = balance_data.sort_values(
        ["company_id", "year"]
    )

    latest_balance = (
        balance_data
        .groupby("company_id", as_index=False)
        .tail(1)
        .copy()
    )

    merged = latest_cash.merge(
        latest_profit[
            ["company_id", "sales", "operating_profit", "net_profit"]
        ],
        on="company_id",
        how="left"
    )

    merged = merged.merge(
        latest_balance[
            ["company_id", "total_liabilities"]
        ],
        on="company_id",
        how="left"
    )

    def _safe_call(function, *args):
        for value in args:
            if pd.isna(value):
                return np.nan

        try:
            result = function(*args)
        except (ZeroDivisionError, ValueError, TypeError):
            return np.nan

        return np.nan if result is None else result

    merged["free_cash_flow_value"] = merged.apply(
        lambda row: _safe_call(
            free_cash_flow,
            row["operating_activity"],
            row["investing_activity"]
        ),
        axis=1
    )

    merged["operating_cash_flow_ratio_value"] = merged.apply(
        lambda row: _safe_call(
            cashflow_kpi_ocf_ratio,
            row["operating_activity"],
            row["total_liabilities"]
        ),
        axis=1
    )

    merged["cfo_quality_score_value"] = merged.apply(
        lambda row: _safe_call(
            cfo_quality_score,
            row["operating_activity"],
            row["net_profit"]
        ),
        axis=1
    )

    merged["capex_intensity_value"] = merged.apply(
        lambda row: _safe_call(
            capex_intensity,
            row["investing_activity"],
            row["sales"]
        ),
        axis=1
    )

    merged["fcf_conversion_ratio_value"] = merged.apply(
        lambda row: _safe_call(
            fcf_conversion_ratio,
            row["free_cash_flow_value"],
            row["operating_profit"]
        ),
        axis=1
    )

    merged["capital_allocation_pattern_value"] = merged.apply(
        lambda row: _safe_call(
            capital_allocation_pattern,
            row["operating_activity"],
            row["investing_activity"],
            row["financing_activity"]
        ),
        axis=1
    )

    return merged[
        [
            "company_id",
            "free_cash_flow_value",
            "operating_cash_flow_ratio_value",
            "cfo_quality_score_value",
            "capex_intensity_value",
            "fcf_conversion_ratio_value",
            "capital_allocation_pattern_value"
        ]
    ]


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
        ),
        "revenue_cagr_score": (
            "revenue_cagr_percentage"
        ),
        "pat_cagr_score": (
            "pat_cagr_percentage"
        ),
        "eps_cagr_score": (
            "eps_cagr_percentage"
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
        "debt_score",
        "revenue_cagr_score",
        "pat_cagr_score",
        "eps_cagr_score"
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

        cagr_metrics = prepare_cagr_metrics(
            profit_loss
        )

        cashflow_kpi_metrics = prepare_cashflow_kpis(
            cash_flow,
            profit_loss,
            balance_sheet
        )

        metrics = companies.copy()

        datasets = [
            profit_metrics,
            balance_metrics,
            cash_metrics,
            analysis_metrics,
            cagr_metrics,
            cashflow_kpi_metrics
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
            "revenue_cagr_percentage",
            "pat_cagr_percentage",
            "eps_cagr_percentage",
            "stock_price_cagr",
            "roe_percentage",
            "roce_percentage",
            "net_profit_margin_percentage",
            "debt_to_asset_ratio",
            "free_cash_flow_value",
            "operating_cash_flow_ratio_value",
            "cfo_quality_score_value",
            "capex_intensity_value",
            "fcf_conversion_ratio_value",
            "capital_allocation_pattern_value"
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