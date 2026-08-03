import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_latest_snapshot, get_sectors_summary  # noqa: E402

st.set_page_config(page_title="Sector Analysis | Nifty 100 Analytics", layout="wide")
st.title("🏭 Sector Analysis")

df = get_latest_snapshot()
sector_summary = get_sectors_summary()

sector_choice = st.selectbox("Sector", ["All"] + sector_summary["broad_sector"].tolist())
plot_df = df if sector_choice == "All" else df[df["broad_sector"] == sector_choice]

st.subheader("Free Cash Flow vs ROE (bubble = Market Cap)")
fig = px.scatter(
    plot_df, x="free_cash_flow_cr", y="return_on_equity_pct", size="market_cap_crore",
    color="sub_sector", hover_name="company_name", size_max=45,
)
fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig, width="stretch")

st.divider()
st.subheader("Sector Median KPIs (11 broad sectors)")
metric_choice = st.radio("Metric", ["avg_roe", "avg_de", "avg_pe"], horizontal=True,
                          format_func=lambda x: {"avg_roe": "Avg ROE %", "avg_de": "Avg D/E", "avg_pe": "Avg P/E"}[x])
fig2 = px.bar(sector_summary.sort_values(metric_choice, ascending=False), x="broad_sector", y=metric_choice)
fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig2, width="stretch")

st.divider()
st.dataframe(sector_summary.rename(columns={
    "broad_sector": "Sector", "company_count": "# Companies", "avg_roe": "Avg ROE %",
    "avg_de": "Avg D/E", "avg_pe": "Avg P/E", "total_market_cap": "Total Mkt Cap (₹Cr)",
}), width="stretch", hide_index=True)
