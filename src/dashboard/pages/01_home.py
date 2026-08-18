import sys
from pathlib import Path

import requests
import plotly.express as px
import streamlit as st

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.dashboard.utils.db import get_latest_snapshot  # noqa: E402


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="Home | Nifty 100 Analytics",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Home — Nifty 100 Financial Intelligence")


# ---------------------------------------------------------
# FASTAPI CONFIG
# ---------------------------------------------------------

API_BASE_URL = "http://127.0.0.1:8000"


@st.cache_data(ttl=60)
def get_api_data(endpoint):
    """Fetch data from FastAPI backend."""
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            timeout=5,
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException:
        return None


# ---------------------------------------------------------
# API STATUS
# ---------------------------------------------------------

health_data = get_api_data("/health")
info_data = get_api_data("/api/info")
metrics_data = get_api_data("/api/metrics")
rankings_data = get_api_data("/api/rankings")


# ---------------------------------------------------------
# API STATUS DISPLAY
# ---------------------------------------------------------

if health_data and health_data.get("status") == "healthy":
    st.success("🟢 FastAPI Backend: Connected")
else:
    st.warning(
        "🟡 FastAPI Backend: Not available. "
        "Start Uvicorn using the API terminal."
    )


# ---------------------------------------------------------
# PROJECT INFORMATION
# ---------------------------------------------------------

if info_data:
    info_col1, info_col2, info_col3 = st.columns(3)

    info_col1.metric(
        "API Project",
        info_data.get("project", "NIFTY 100"),
    )

    info_col2.metric(
        "API Version",
        info_data.get("version", "1.0.0"),
    )

    info_col3.metric(
        "API Status",
        info_data.get("status", "unknown").upper(),
    )


st.divider()


# ---------------------------------------------------------
# DATABASE SNAPSHOT
# ---------------------------------------------------------

df = get_latest_snapshot()


# ---------------------------------------------------------
# API METRICS
# ---------------------------------------------------------

api_metrics = []

if metrics_data:
    api_metrics = metrics_data.get("data", [])

# Convert API metrics to a dictionary for easy lookup
metrics_by_company = {}

for company in api_metrics:
    company_id = company.get("company_id")

    if company_id:
        metrics_by_company[company_id] = company


# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

company_count = len(df)

average_roe = None
median_pe = None
median_de = None
median_revenue_cagr = None
debt_free_count = None

if "return_on_equity_pct" in df.columns:
    average_roe = df["return_on_equity_pct"].mean()

if "pe_ratio" in df.columns:
    median_pe = df["pe_ratio"].median()

if "debt_to_equity" in df.columns:
    median_de = df["debt_to_equity"].median()

if "revenue_cagr_5yr" in df.columns:
    median_revenue_cagr = df["revenue_cagr_5yr"].median()

if "debt_to_equity" in df.columns:
    debt_free_count = (
        df["debt_to_equity"] <= 0.01
    ).sum()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric(
    "Companies",
    f"{company_count}",
)

if average_roe is not None:
    col2.metric(
        "Average ROE",
        f"{average_roe:.1f}%",
    )
else:
    col2.metric("Average ROE", "N/A")


if median_pe is not None:
    col3.metric(
        "Median P/E",
        f"{median_pe:.1f}x",
    )
else:
    col3.metric("Median P/E", "N/A")


if median_de is not None:
    col4.metric(
        "Median D/E",
        f"{median_de:.2f}",
    )
else:
    col4.metric("Median D/E", "N/A")


if median_revenue_cagr is not None:
    col5.metric(
        "Median Revenue CAGR",
        f"{median_revenue_cagr:.1f}%",
    )
else:
    col5.metric("Median Revenue CAGR", "N/A")


if debt_free_count is not None:
    col6.metric(
        "Debt-Free Companies",
        f"{debt_free_count}",
    )
else:
    col6.metric("Debt-Free Companies", "N/A")


st.divider()


# ---------------------------------------------------------
# API DATA SUMMARY
# ---------------------------------------------------------

st.subheader("🔌 FastAPI Data Summary")

api_col1, api_col2, api_col3 = st.columns(3)

api_col1.metric(
    "Metrics Records",
    len(api_metrics),
)

if rankings_data:
    ranking_data = rankings_data.get("data", [])
    api_col2.metric(
        "Ranking Records",
        len(ranking_data),
    )
else:
    ranking_data = []
    api_col2.metric(
        "Ranking Records",
        "N/A",
    )


if health_data:
    api_col3.metric(
        "Backend",
        "ONLINE",
    )
else:
    api_col3.metric(
        "Backend",
        "OFFLINE",
    )


st.divider()


# ---------------------------------------------------------
# MAIN DASHBOARD
# ---------------------------------------------------------

left, right = st.columns([1, 1])


# ---------------------------------------------------------
# MARKET CAP BY SECTOR
# ---------------------------------------------------------

with left:

    st.subheader("📊 Market Cap by Sector")

    if (
        "broad_sector" in df.columns
        and "market_cap_crore" in df.columns
    ):

        sector_mcap = (
            df.groupby("broad_sector")["market_cap_crore"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            sector_mcap,
            names="broad_sector",
            values="market_cap_crore",
            hole=0.5,
        )

        fig.update_layout(
            margin=dict(
                t=10,
                b=10,
                l=10,
                r=10,
            )
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    else:
        st.info("Sector market-cap data unavailable.")


# ---------------------------------------------------------
# TOP 10 COMPANIES
# ---------------------------------------------------------

with right:

    st.subheader(
        "🏆 Top 10 Companies by Composite Quality Score"
    )

    if ranking_data:

        ranking_rows = []

        for company in ranking_data[:10]:

            ranking_rows.append(
                {
                    "Company": company.get(
                        "company_name",
                        "Unknown",
                    ),
                    "Rank": company.get(
                        "company_rank",
                        "",
                    ),
                    "Health Score": company.get(
                        "financial_health_score",
                        "",
                    ),
                    "Rating": company.get(
                        "financial_rating",
                        "",
                    ),
                    "ROE %": company.get(
                        "roe_percentage",
                        "",
                    ),
                    "ROCE %": company.get(
                        "roce_percentage",
                        "",
                    ),
                    "D/A": company.get(
                        "debt_to_asset_ratio",
                        "",
                    ),
                }
            )

        st.dataframe(
            ranking_rows,
            width="stretch",
            hide_index=True,
        )

    elif "composite_score" in df.columns:

        top10 = (
            df.sort_values(
                "composite_score",
                ascending=False,
            )
            .head(10)
            [
                [
                    "company_name",
                    "broad_sector",
                    "composite_score",
                    "return_on_equity_pct",
                    "debt_to_equity",
                    "free_cash_flow_cr",
                ]
            ]
            .rename(
                columns={
                    "company_name": "Company",
                    "broad_sector": "Sector",
                    "composite_score": "Score",
                    "return_on_equity_pct": "ROE %",
                    "debt_to_equity": "D/E",
                    "free_cash_flow_cr": "FCF (₹Cr)",
                }
            )
        )

        st.dataframe(
            top10,
            width="stretch",
            hide_index=True,
        )

    else:
        st.info("Ranking data unavailable.")


st.divider()


# ---------------------------------------------------------
# CAPITAL ALLOCATION PATTERN
# ---------------------------------------------------------

st.subheader(
    "💰 Capital Allocation Pattern — Nifty 100"
)

if "pattern_label" in df.columns:

    pattern_counts = (
        df["pattern_label"]
        .fillna("Unclassified")
        .value_counts()
        .reset_index()
    )

    pattern_counts.columns = [
        "pattern",
        "companies",
    ]

    fig2 = px.bar(
        pattern_counts.sort_values(
            "companies",
            ascending=True,
        ),
        x="companies",
        y="pattern",
        orientation="h",
    )

    fig2.update_layout(
        margin=dict(
            t=10,
            b=10,
            l=10,
            r=10,
        )
    )

    st.plotly_chart(
        fig2,
        width="stretch",
    )

else:
    st.info("Capital allocation data unavailable.")


# ---------------------------------------------------------
# API ENDPOINT STATUS
# ---------------------------------------------------------

st.divider()

st.subheader("🔗 API Endpoint Status")

endpoints = {
    "/health": health_data,
    "/api/info": info_data,
    "/api/metrics": metrics_data,
    "/api/rankings": rankings_data,
}

endpoint_rows = []

for endpoint, data in endpoints.items():

    endpoint_rows.append(
        {
            "Endpoint": endpoint,
            "Status": (
                "✅ Working"
                if data is not None
                else "❌ Unavailable"
            ),
        }
    )

st.dataframe(
    endpoint_rows,
    width="stretch",
    hide_index=True,
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.caption(
    "NIFTY 100 Financial Intelligence — "
    "FastAPI + Streamlit dashboard. "
    "Financial metrics are sourced from the project's "
    "validated data pipeline."
)