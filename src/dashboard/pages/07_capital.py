import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_latest_snapshot  # noqa: E402

st.set_page_config(page_title="Capital Allocation Map | Nifty 100 Analytics", layout="wide")
st.title("🗺️ Capital Allocation Map")

df = get_latest_snapshot().copy()
df["pattern_label"] = df["pattern_label"].fillna("Unclassified")
df["market_cap_crore"] = df["market_cap_crore"].fillna(1)
df["company_name"] = df["company_name"].fillna(df["company_id"])
df = df[df["company_name"].astype(str).str.strip() != ""]
df = df.drop_duplicates(subset=["company_id"])

fig = px.treemap(df, path=["pattern_label", "company_name"], values="market_cap_crore", color="pattern_label")
fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
st.plotly_chart(fig, width="stretch")

st.caption(
    "Pattern derived from the sign of CFO / CFI / CFF in the most recent reported year "
    "(e.g. CFO+ / CFI− / CFF− = reinvesting operating cash while returning capital to shareholders)."
)

st.divider()
st.subheader("Companies by pattern")
pattern_choice = st.selectbox("Select a pattern to list companies", sorted(df["pattern_label"].unique()))
listing = df[df["pattern_label"] == pattern_choice][
    ["company_name", "broad_sector", "market_cap_crore", "return_on_equity_pct", "debt_to_equity"]
].rename(columns={
    "company_name": "Company", "broad_sector": "Sector", "market_cap_crore": "Mkt Cap ₹Cr",
    "return_on_equity_pct": "ROE %", "debt_to_equity": "D/E",
}).sort_values("Mkt Cap ₹Cr", ascending=False)
st.dataframe(listing, width="stretch", hide_index=True)
