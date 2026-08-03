import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_latest_snapshot  # noqa: E402

st.set_page_config(page_title="Screener | Nifty 100 Analytics", layout="wide")
st.title("🔎 Investment Screener")

df = get_latest_snapshot().copy()
for col in ["revenue_cagr_5yr", "pat_cagr_5yr", "dividend_yield_pct", "interest_coverage", "net_profit_margin_pct"]:
    if col not in df:
        df[col] = 0
df = df.fillna({
    "revenue_cagr_5yr": 0, "pat_cagr_5yr": 0, "dividend_yield_pct": 0,
    "interest_coverage": 999, "debt_to_equity": 0, "pe_ratio": 999, "pb_ratio": 999,
})

PRESETS = {
    "Quality Compounder": dict(roe_min=15.0, de_max=1.0, fcf_min=0.0, revenue_cagr_min=10.0),
    "Value Pick": dict(pe_max=20.0, pb_max=3.0, de_max=2.0, div_yield_min=1.0),
    "Growth Accelerator": dict(pat_cagr_min=20.0, revenue_cagr_min=15.0, de_max=2.0),
    "Dividend Champion": dict(div_yield_min=2.0, fcf_min=0.0),
    "Debt-Free Blue Chip": dict(de_max=0.0, roe_min=12.0),
    "Turnaround Watch": dict(revenue_cagr_min=10.0),
}

st.sidebar.subheader("Presets")
preset_choice = st.sidebar.radio("Apply a preset", ["None"] + list(PRESETS.keys()))
preset = PRESETS.get(preset_choice, {})

st.sidebar.subheader("Filters")
sector_choice = st.sidebar.multiselect("Sector", sorted(df["broad_sector"].dropna().unique().tolist()))
roe_min = st.sidebar.slider("ROE min (%)", 0.0, 60.0, preset.get("roe_min", 0.0))
de_max = st.sidebar.slider("D/E max", 0.0, 5.0, preset.get("de_max", 5.0))
fcf_min = st.sidebar.slider("FCF min (₹ Cr)", float(df["free_cash_flow_cr"].min()), float(df["free_cash_flow_cr"].max()), float(preset.get("fcf_min", df["free_cash_flow_cr"].min())))
revenue_cagr_min = st.sidebar.slider("Revenue CAGR (5yr) min (%)", -20.0, 40.0, preset.get("revenue_cagr_min", -20.0))
pat_cagr_min = st.sidebar.slider("PAT CAGR (5yr) min (%)", -20.0, 60.0, preset.get("pat_cagr_min", -20.0))
pe_max = st.sidebar.slider("P/E max", 0.0, 100.0, preset.get("pe_max", 100.0))
pb_max = st.sidebar.slider("P/B max", 0.0, 20.0, preset.get("pb_max", 20.0))
div_yield_min = st.sidebar.slider("Dividend Yield min (%)", 0.0, 6.0, preset.get("div_yield_min", 0.0))
icr_min = st.sidebar.slider("Interest Coverage min", 0.0, 50.0, 0.0)

filtered = df[
    (df["return_on_equity_pct"].fillna(-999) >= roe_min)
    & (df["debt_to_equity"] <= de_max)
    & (df["free_cash_flow_cr"].fillna(-1e9) >= fcf_min)
    & (df["revenue_cagr_5yr"] >= revenue_cagr_min)
    & (df["pat_cagr_5yr"] >= pat_cagr_min)
    & (df["pe_ratio"] <= pe_max)
    & (df["pb_ratio"] <= pb_max)
    & (df["dividend_yield_pct"] >= div_yield_min)
    & (df["interest_coverage"].fillna(999) >= icr_min)
].copy()
if sector_choice:
    filtered = filtered[filtered["broad_sector"].isin(sector_choice)]

st.markdown(f"**{len(filtered)} companies match your filters**")

display_cols = {
    "company_id": "Ticker", "company_name": "Company", "broad_sector": "Sector",
    "composite_score": "Score", "return_on_equity_pct": "ROE %", "debt_to_equity": "D/E",
    "pe_ratio": "P/E", "pb_ratio": "P/B", "free_cash_flow_cr": "FCF (₹Cr)",
    "revenue_cagr_5yr": "Rev CAGR 5yr %", "pat_cagr_5yr": "PAT CAGR 5yr %",
    "dividend_yield_pct": "Div Yield %", "interest_coverage": "ICR",
}
result_table = filtered[list(display_cols)].rename(columns=display_cols).sort_values("Score", ascending=False)
st.dataframe(result_table, width="stretch", hide_index=True)

csv = result_table.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download CSV", csv, file_name="screener_results.csv", mime="text/csv")
