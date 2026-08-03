import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_latest_snapshot  # noqa: E402

st.set_page_config(page_title="Home | Nifty 100 Analytics", layout="wide")
st.title("🏠 Home — Nifty 100 Overview")

df = get_latest_snapshot()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Companies", f"{len(df)}")
col2.metric("Average ROE", f"{df['return_on_equity_pct'].mean():.1f}%")
col3.metric("Median P/E", f"{df['pe_ratio'].median():.1f}x")
col4.metric("Median D/E", f"{df['debt_to_equity'].median():.2f}")
col5.metric("Median Revenue CAGR (5yr)", f"{df['revenue_cagr_5yr'].median():.1f}%")
col6.metric("Debt-Free Companies", f"{(df['debt_to_equity'] <= 0.01).sum()}")

st.divider()

left, right = st.columns([1, 1])

with left:
    st.subheader("Market Cap by Sector")
    sector_mcap = df.groupby("broad_sector")["market_cap_crore"].sum().reset_index()
    fig = px.pie(sector_mcap, names="broad_sector", values="market_cap_crore", hole=0.5)
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
    st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Top 10 Companies by Composite Quality Score")
    top10 = df.sort_values("composite_score", ascending=False).head(10)[
        ["company_name", "broad_sector", "composite_score", "return_on_equity_pct", "debt_to_equity", "free_cash_flow_cr"]
    ].rename(columns={
        "company_name": "Company", "broad_sector": "Sector", "composite_score": "Score",
        "return_on_equity_pct": "ROE %", "debt_to_equity": "D/E", "free_cash_flow_cr": "FCF (₹Cr)",
    })
    st.dataframe(top10, width="stretch", hide_index=True)

st.divider()
st.subheader("Capital Allocation Pattern — Nifty 100")
pattern_counts = df["pattern_label"].fillna("Unclassified").value_counts().reset_index()
pattern_counts.columns = ["pattern", "companies"]
fig2 = px.bar(pattern_counts.sort_values("companies", ascending=True), x="companies", y="pattern", orientation="h")
fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig2, width="stretch")

st.caption("All figures from real Screener.in-sourced Nifty 100 statement data — most recent reported fiscal year per company. Simulated fields (stock_prices, market_cap multiples) are clearly labelled in the source workbooks.")
