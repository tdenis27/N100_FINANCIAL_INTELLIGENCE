import sys
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_peer_group, get_peer_group_names  # noqa: E402

st.set_page_config(page_title="Peer Comparison | Nifty 100 Analytics", layout="wide")
st.title("⚖️ Peer Comparison")

groups = get_peer_group_names()
group_name = st.selectbox("Peer group", groups)

peers = get_peer_group(group_name)

if peers.empty:
    st.warning("No peers found for this group.")
else:
    default_ticker = peers.loc[peers["is_benchmark"] == True, "company_id"]  # noqa: E712
    default_name = peers.loc[peers["company_id"] == default_ticker.iloc[0], "company_name"].iloc[0] if not default_ticker.empty else peers["company_name"].iloc[0]

    benchmark_name = st.selectbox("Focus company", peers["company_name"].tolist(), index=peers["company_name"].tolist().index(default_name))
    benchmark = peers[peers["company_name"] == benchmark_name].iloc[0]

    metrics = ["return_on_equity_pct", "net_profit_margin_pct", "free_cash_flow_cr", "revenue_cagr_5yr", "pat_cagr_5yr"]
    metric_labels = ["ROE %", "NPM %", "FCF ₹Cr", "Rev CAGR 5yr %", "PAT CAGR 5yr %"]

    group_avg = peers[metrics].mean()

    def normalize(row):
        return [(row[m] / peers[m].abs().max() * 100) if peers[m].abs().max() else 0 for m in metrics]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=normalize(benchmark), theta=metric_labels, fill="toself", name=benchmark["company_name"]))
    fig.add_trace(go.Scatterpolar(r=normalize(group_avg), theta=metric_labels, fill="toself", name=f"{group_name} average"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True)
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader(f"All companies in {group_name} — with percentile rank")
    display_cols = {
        "company_name": "Company", "return_on_equity_pct": "ROE %", "return_on_equity_pct_pctile": "ROE %ile",
        "debt_to_equity": "D/E", "debt_to_equity_pctile": "D/E %ile (lower=better)",
        "free_cash_flow_cr": "FCF ₹Cr", "pe_ratio": "P/E", "revenue_cagr_5yr": "Rev CAGR 5yr %",
    }
    table = peers[list(display_cols)].rename(columns=display_cols).sort_values("ROE %", ascending=False)
    st.dataframe(table, width="stretch", hide_index=True)
