"""
Nifty 100 Analytics — main Streamlit entry point.

Run:
    streamlit run src/dashboard/app.py

Sidebar navigation to all 8 screens is handled automatically by Streamlit's
multi-page app support via the pages/ directory (01_home.py ... 08_reports.py).
"""
import streamlit as st

st.set_page_config(
    page_title="Nifty 100 Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Nifty 100 Analytics")
st.markdown(
    """
Welcome. Use the sidebar to navigate between screens:

1. **Home** — portfolio-wide KPIs, sector breakdown, top companies
2. **Company Profile** — search any company for a full financial snapshot
3. **Screener** — filter all 92 companies by 10 metrics, export to CSV
4. **Peer Comparison** — benchmark a company against its sector peers
5. **Trend Analysis** — multi-metric 10-year trend lines
6. **Sector Analysis** — sector bubble map and median KPIs
7. **Capital Allocation Map** — treemap of capital allocation patterns
8. **Annual Reports** — links to company annual reports

If this is your first run, build the database from the real Nifty 100
source workbooks in `data/raw/` and `data/supporting/`:

```
python src/etl/loader.py
```

This loads 92 Nifty 100 companies across 7 core + 5 supplementary datasets
(profit & loss, balance sheet, cash flow, sectors, market cap, financial
ratios, peer groups, etc.) into `data/nifty100.db`, and derives revenue/PAT/
EPS CAGR, capital allocation patterns, and a composite quality score for
each company.
"""
)

st.info("👈 Select a screen from the sidebar to get started.")
