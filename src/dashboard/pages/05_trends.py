import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_history, search_companies  # noqa: E402

st.set_page_config(page_title="Trend Analysis | Nifty 100 Analytics", layout="wide")
st.title("📈 Trend Analysis")

query = st.text_input("Search company name or ticker")

METRIC_OPTIONS = {
    "Sales": "sales",
    "Net Profit": "net_profit",
    "ROE %": "return_on_equity_pct",
    "Operating Margin %": "operating_profit_margin_pct",
    "D/E": "debt_to_equity",
    "EPS": "eps",
    "Free Cash Flow": "free_cash_flow_cr",
    "Interest Coverage": "interest_coverage",
}

if query:
    matches = search_companies(query)
    if matches.empty:
        st.warning("Ticker not found — please try another")
    else:
        options = [f"{row.company_name} ({row.company_id})" for row in matches.itertuples()]
        choice = st.selectbox("Company", options)
        ticker = matches.iloc[options.index(choice)]["company_id"]

        selected_metrics = st.multiselect(
            "Metrics to overlay (up to 3)", list(METRIC_OPTIONS.keys()), default=["Sales"], max_selections=3,
        )

        history = get_history(ticker)
        if history.empty:
            st.warning("No data available for this ticker.")
        else:
            fig = go.Figure()
            for label in selected_metrics:
                col = METRIC_OPTIONS[label]
                fig.add_trace(go.Scatter(x=history["year"], y=history[col], name=label, mode="lines+markers"))
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, width="stretch")

            if len(history) < 10:
                st.info(f"Data available for {len(history)} years for this company.")

            st.divider()
            st.subheader("Underlying data")
            st.dataframe(history[["year"] + [METRIC_OPTIONS[m] for m in selected_metrics]], width="stretch", hide_index=True)
else:
    st.caption("Search for a company above to see its trends.")
