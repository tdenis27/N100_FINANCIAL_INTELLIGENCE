"""
Shared, cached data-access layer for the Nifty 100 Analytics dashboard.

Talks to the real data/nifty100.db built by src/etl/loader.py (real Nifty
100 financial statements — not mock data). Every function is wrapped in
@st.cache_data(ttl=600) so repeated navigation between screens doesn't
re-query. Pages in pages/ only call functions in this file.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "nifty100.db"


def _connect():
    return sqlite3.connect(DB_PATH)


@st.cache_data(ttl=600)
def get_companies() -> pd.DataFrame:
    with _connect() as conn:
        q = """
            SELECT c.id AS company_id, c.company_name, c.about_company, c.website,
                   c.face_value, c.book_value, c.roce_percentage, c.roe_percentage,
                   s.broad_sector, s.sub_sector, s.market_cap_category
            FROM companies c
            LEFT JOIN sectors s ON s.company_id = c.id
            ORDER BY c.company_name
        """
        return pd.read_sql_query(q, conn)


@st.cache_data(ttl=600)
def get_latest_snapshot() -> pd.DataFrame:
    """One row per company: latest-year KPIs, sector, valuation, CAGR, capital pattern."""
    with _connect() as conn:
        return pd.read_sql_query("SELECT * FROM latest_snapshot", conn)


@st.cache_data(ttl=600)
def get_history(ticker: str) -> pd.DataFrame:
    """Full annual P&L + BS + CF + ratios history for one company, joined by year."""
    with _connect() as conn:
        q = """
            SELECT p.company_id, p.year, p.sales, p.expenses, p.operating_profit,
                   p.opm_percentage, p.other_income, p.interest, p.depreciation,
                   p.net_profit, p.eps, p.dividend_payout,
                   b.equity_capital, b.reserves, b.borrowings, b.total_assets,
                   f.net_profit_margin_pct, f.operating_profit_margin_pct,
                   f.return_on_equity_pct, f.debt_to_equity, f.interest_coverage,
                   f.asset_turnover, f.free_cash_flow_cr, f.book_value_per_share
            FROM profitandloss p
            LEFT JOIN balancesheet b ON b.company_id = p.company_id AND b.year = p.year
            LEFT JOIN financial_ratios f ON f.company_id = p.company_id AND f.year = p.year
            WHERE p.company_id = ?
            ORDER BY p.year
        """
        return pd.read_sql_query(q, conn, params=[ticker])


@st.cache_data(ttl=600)
def get_cashflow_history(ticker: str) -> pd.DataFrame:
    with _connect() as conn:
        q = """
            SELECT cf.*, ci.fcf, ci.cfo_pat_ratio, ci.capex_intensity_pct,
                   ci.fcf_conversion_pct, ci.distress_flag, ca.pattern_label
            FROM cashflow cf
            LEFT JOIN cashflow_intelligence ci ON ci.company_id = cf.company_id AND ci.year = cf.year
            LEFT JOIN capital_allocation ca ON ca.company_id = cf.company_id AND ca.year = cf.year
            WHERE cf.company_id = ?
            ORDER BY cf.year
        """
        return pd.read_sql_query(q, conn, params=[ticker])


@st.cache_data(ttl=600)
def get_market_cap_history(ticker: str) -> pd.DataFrame:
    with _connect() as conn:
        q = "SELECT * FROM market_cap WHERE company_id = ? ORDER BY year"
        return pd.read_sql_query(q, conn, params=[ticker])


@st.cache_data(ttl=600)
def get_pros_cons(ticker: str) -> pd.DataFrame:
    with _connect() as conn:
        q = "SELECT pros, cons FROM prosandcons WHERE company_id = ?"
        return pd.read_sql_query(q, conn, params=[ticker])


@st.cache_data(ttl=600)
def get_documents(ticker: str) -> pd.DataFrame:
    with _connect() as conn:
        q = 'SELECT "Year" AS year, "Annual_Report" AS annual_report FROM documents WHERE company_id = ? ORDER BY "Year" DESC'
        return pd.read_sql_query(q, conn, params=[ticker])


@st.cache_data(ttl=600)
def get_sectors_summary() -> pd.DataFrame:
    with _connect() as conn:
        q = """
            SELECT broad_sector,
                   COUNT(*) AS company_count,
                   ROUND(AVG(return_on_equity_pct), 1) AS avg_roe,
                   ROUND(AVG(debt_to_equity), 2) AS avg_de,
                   ROUND(AVG(pe_ratio), 1) AS avg_pe,
                   ROUND(SUM(market_cap_crore), 0) AS total_market_cap
            FROM latest_snapshot
            GROUP BY broad_sector
            ORDER BY total_market_cap DESC
        """
        return pd.read_sql_query(q, conn)


@st.cache_data(ttl=600)
def get_peer_group_names() -> list:
    with _connect() as conn:
        df = pd.read_sql_query("SELECT DISTINCT peer_group_name FROM peer_groups ORDER BY peer_group_name", conn)
        return df["peer_group_name"].tolist()


@st.cache_data(ttl=600)
def get_peer_group(group_name: str) -> pd.DataFrame:
    with _connect() as conn:
        q = """
            SELECT pg.company_id, pg.is_benchmark, s.company_name, s.broad_sector,
                   s.return_on_equity_pct, s.debt_to_equity, s.net_profit_margin_pct,
                   s.free_cash_flow_cr, s.pe_ratio, s.pb_ratio, s.revenue_cagr_5yr,
                   s.pat_cagr_5yr
            FROM peer_groups pg
            JOIN latest_snapshot s ON s.company_id = pg.company_id
            WHERE pg.peer_group_name = ?
        """
        df = pd.read_sql_query(q, conn, params=[group_name])
        for col in ["return_on_equity_pct", "debt_to_equity", "net_profit_margin_pct", "free_cash_flow_cr", "pe_ratio", "pb_ratio", "revenue_cagr_5yr", "pat_cagr_5yr"]:
            asc = col == "debt_to_equity"
            df[f"{col}_pctile"] = df[col].rank(pct=True, ascending=not asc).round(2)
        return df


@st.cache_data(ttl=600)
def search_companies(term: str) -> pd.DataFrame:
    term = f"%{term.lower()}%"
    with _connect() as conn:
        q = """
            SELECT id AS company_id, company_name
            FROM companies
            WHERE lower(company_name) LIKE ? OR lower(id) LIKE ?
            ORDER BY company_name
        """
        return pd.read_sql_query(q, conn, params=[term, term])
