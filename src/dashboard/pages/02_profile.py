import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_companies, get_history, get_pros_cons, search_companies  # noqa: E402

st.set_page_config(page_title="Company Profile | Nifty 100 Analytics", layout="wide")
st.title("🏢 Company Profile")

companies = get_companies()
query = st.text_input("Search company name or ticker", placeholder="e.g. TCS, HDFC Bank")

ticker = None
if query:
    matches = search_companies(query)
    if matches.empty:
        st.warning("Ticker not found — please try another")
    else:
        options = [f"{row.company_name} ({row.company_id})" for row in matches.itertuples()]
        choice = st.selectbox("Matches", options)
        ticker = matches.iloc[options.index(choice)]["company_id"]

if ticker:
    company_row = companies[companies["company_id"] == ticker].iloc[0]
    history = get_history(ticker)

    if history.empty:
        st.warning("No financial history found for this ticker.")
    else:
        st.subheader(company_row["company_name"])
        st.caption(f"{company_row['broad_sector'] or '—'} · {company_row['sub_sector'] or '—'} · NSE: {ticker}")
        if isinstance(company_row["about_company"], str):
            st.write(company_row["about_company"])

        latest = history.iloc[-1]
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("ROE", f"{latest['return_on_equity_pct']:.1f}%" if latest['return_on_equity_pct'] == latest['return_on_equity_pct'] else "N/A")
        k2.metric("Net Profit Margin", f"{latest['net_profit_margin_pct']:.1f}%" if latest['net_profit_margin_pct'] == latest['net_profit_margin_pct'] else "N/A")
        k3.metric("D/E", f"{latest['debt_to_equity']:.2f}" if latest['debt_to_equity'] == latest['debt_to_equity'] else "N/A")
        k4.metric("Interest Coverage", f"{latest['interest_coverage']:.1f}x" if latest['interest_coverage'] == latest['interest_coverage'] else "Debt Free")
        k5.metric("EPS", f"₹{latest['eps']:.1f}" if latest['eps'] == latest['eps'] else "N/A")
        k6.metric("Free Cash Flow", f"₹{latest['free_cash_flow_cr']:.0f} Cr" if latest['free_cash_flow_cr'] == latest['free_cash_flow_cr'] else "N/A")

        if len(history) < 10:
            st.info(f"Data available for {len(history)} of the last ~15 years for this company.")

        st.divider()
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Sales & Net Profit (₹ Cr)")
            fig = go.Figure()
            fig.add_bar(x=history["year"], y=history["sales"], name="Sales")
            fig.add_bar(x=history["year"], y=history["net_profit"], name="Net Profit")
            fig.update_layout(barmode="group", margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, width="stretch")

        with c2:
            st.subheader("ROE vs D/E")
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=history["year"], y=history["return_on_equity_pct"], name="ROE %"))
            fig2.add_trace(go.Scatter(x=history["year"], y=history["debt_to_equity"], name="D/E", yaxis="y2"))
            fig2.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                yaxis2=dict(overlaying="y", side="right", title="D/E"),
            )
            st.plotly_chart(fig2, width="stretch")

        st.divider()
        st.subheader("Pros & Cons")
        pc = get_pros_cons(ticker)
        pros = [p for p in pc["pros"].dropna().tolist() if p]
        cons = [c for c in pc["cons"].dropna().tolist() if c]
        if not pros and not cons:
            st.caption("No curated pros/cons available for this company yet.")
        pc1, pc2 = st.columns(2)
        with pc1:
            for p in pros:
                st.success(f"✅ {p}")
        with pc2:
            for c in cons:
                st.error(f"❌ {c}")
else:
    st.caption("Search for a company above to see its full profile.")
