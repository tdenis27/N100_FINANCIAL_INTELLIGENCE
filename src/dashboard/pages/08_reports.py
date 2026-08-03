import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from src.dashboard.utils.db import get_documents, search_companies  # noqa: E402

st.set_page_config(page_title="Annual Reports | Nifty 100 Analytics", layout="wide")
st.title("📄 Annual Reports")

query = st.text_input("Search company name or ticker")

if query:
    matches = search_companies(query)
    if matches.empty:
        st.warning("Ticker not found — please try another")
    else:
        options = [f"{row.company_name} ({row.company_id})" for row in matches.itertuples()]
        choice = st.selectbox("Company", options)
        row = matches.iloc[options.index(choice)]

        st.subheader(f"{row['company_name']} — Available Annual Reports")

        docs = get_documents(row["company_id"])
        if docs.empty:
            st.info("No annual report links on file for this company.")
        else:
            for _, d in docs.iterrows():
                if isinstance(d["annual_report"], str) and d["annual_report"].startswith("http"):
                    st.markdown(f"[FY {d['year']} Annual Report]({d['annual_report']})")
                else:
                    col1, col2 = st.columns([3, 1])
                    col1.markdown(f"FY {d['year']}")
                    col2.markdown(":red-badge[Report unavailable]")
else:
    st.caption("Search for a company above to see its annual report links (sourced from documents.xlsx / BSE India).")
