"""
database.py
Data-access layer for the Nifty 100 Financial Intelligence dashboard.
Every Streamlit page should import from here rather than touching sqlite3 directly.
"""

from pathlib import Path
import re
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "n100_financial_intelligence.db"

# Tables whose column headers were loaded incorrectly (a data row was used as the
# header instead of the real header row). We cannot safely infer what each
# "Unnamed: N" column represents without the original source CSVs, so anything
# built on top of these returns raw/best-effort data with a loud warning.
# TODO: re-load market_cap.csv, stock_prices.csv, financial_ratios.csv with the
# correct header row, then delete the workaround functions below.
#
# Confirmed side-effect of the same bug: sectors and peer_groups are each
# missing exactly one row (the row that got consumed as the header) — e.g.
# ABB is absent from `sectors` entirely, and HDFCBANK (the presumed peer-group
# leader) is absent from `peer_groups`. The lookups below degrade gracefully
# (empty result) for those rows, but re-loading all five tables from the
# original CSVs with the correct header row is the real fix.
BROKEN_TABLES = ["market_cap", "stock_prices", "financial_ratios"]


def get_connection():
    return sqlite3.connect(DB_PATH)


def _read(query, params=None):
    with get_connection() as conn:
        return pd.read_sql(query, conn, params=params)


# ------------------------------------------------------------------
# Companies
# ------------------------------------------------------------------

def get_companies():
    """All companies with their static profile + latest ROE/ROCE."""
    return _read("SELECT * FROM companies ORDER BY company_name")


def get_company(company_id):
    df = _read("SELECT * FROM companies WHERE id = ?", (company_id,))
    return df.iloc[0] if not df.empty else None


def get_company_ids():
    return _read("SELECT id, company_name FROM companies ORDER BY company_name")


# ------------------------------------------------------------------
# Financial statements
# ------------------------------------------------------------------

def get_profit_loss(company_id=None):
    q = "SELECT * FROM profitandloss"
    if company_id:
        return _read(q + " WHERE company_id = ? ORDER BY year", (company_id,))
    return _read(q + " ORDER BY company_id, year")


def get_balance_sheet(company_id=None):
    q = "SELECT * FROM balancesheet"
    if company_id:
        return _read(q + " WHERE company_id = ? ORDER BY year", (company_id,))
    return _read(q + " ORDER BY company_id, year")


def get_cash_flow(company_id=None):
    q = "SELECT * FROM cashflow"
    if company_id:
        return _read(q + " WHERE company_id = ? ORDER BY year", (company_id,))
    return _read(q + " ORDER BY company_id, year")


def get_analysis(company_id=None):
    """Growth/CAGR text table. Values are messy free text like '10 Years: 21%'."""
    q = "SELECT * FROM analysis"
    if company_id:
        return _read(q + " WHERE company_id = ?", (company_id,))
    return _read(q)


def get_pros_cons(company_id):
    return _read("SELECT * FROM prosandcons WHERE company_id = ?", (company_id,))


def get_documents(company_id):
    return _read(
        "SELECT * FROM documents WHERE company_id = ? ORDER BY year DESC",
        (company_id,),
    )


# ------------------------------------------------------------------
# Sectors / peer groups — headers fixed below (safe to trust)
# ------------------------------------------------------------------

_SECTOR_COLUMNS = {
    "Unnamed: 0": "id",
    "abb": "ticker",
    "industrials": "sector",
    "capital_goods": "industry",
    "Unnamed: 4": "index_weight_pct",
    "large_cap": "market_cap_category",
}


def get_sectors():
    """Sector/industry classification per ticker. Column names in the raw table
    were mislabeled at load time (e.g. the 'industrials' column actually holds
    each row's sector, not a constant) — renamed here to their real meaning."""
    df = _read("SELECT * FROM sectors")
    df = df.rename(columns=_SECTOR_COLUMNS)
    return df[["id", "ticker", "sector", "industry", "index_weight_pct", "market_cap_category"]]


_PEER_GROUP_COLUMNS = {
    "Unnamed: 0": "id",
    "private_banks": "peer_group",
    "hdfcbank": "ticker",
    "true.1": "is_group_leader",
}


def get_peer_groups():
    df = _read("SELECT * FROM peer_groups")
    df = df.rename(columns=_PEER_GROUP_COLUMNS)
    return df[["id", "peer_group", "ticker", "is_group_leader"]]


def get_peers_for(ticker):
    """Other tickers in the same peer group as `ticker`."""
    groups = get_peer_groups()
    row = groups[groups["ticker"] == ticker]
    if row.empty:
        return pd.DataFrame(columns=groups.columns)
    peer_group = row.iloc[0]["peer_group"]
    return groups[(groups["peer_group"] == peer_group) & (groups["ticker"] != ticker)]


def get_sector_for(ticker):
    sectors = get_sectors()
    row = sectors[sectors["ticker"] == ticker]
    return row.iloc[0] if not row.empty else None


def get_peers_by_sector(ticker):
    """Fallback peer set: other companies in the same sector, when no explicit
    peer group entry exists for this ticker."""
    sectors = get_sectors()
    row = sectors[sectors["ticker"] == ticker]
    if row.empty:
        return pd.DataFrame(columns=sectors.columns)
    sector = row.iloc[0]["sector"]
    return sectors[(sectors["sector"] == sector) & (sectors["ticker"] != ticker)]


# ------------------------------------------------------------------
# Broken tables — raw passthrough with a warning, DO NOT trust column meaning
# ------------------------------------------------------------------

def get_raw_broken_table(table_name):
    if table_name not in BROKEN_TABLES:
        raise ValueError(f"{table_name} is not in BROKEN_TABLES")
    return _read(f"SELECT * FROM {table_name}")


# ------------------------------------------------------------------
# Derived metrics (computed from the clean tables only)
# ------------------------------------------------------------------

def _cagr(first, last, years):
    if first is None or last is None or years <= 0:
        return None
    if pd.isna(first) or pd.isna(last) or first <= 0 or last <= 0:
        return None
    return (((last / first) ** (1 / years)) - 1) * 100


def compute_company_metrics():
    """One row per company with health-score inputs, all derived from the
    clean statement tables (profitandloss, balancesheet, cashflow, companies)."""
    companies = get_companies()
    pnl = get_profit_loss()
    bs = get_balance_sheet()
    cf = get_cash_flow()

    rows = []
    for _, co in companies.iterrows():
        cid = co["id"]
        co_pnl = pnl[pnl["company_id"] == cid].sort_values("year")
        co_bs = bs[bs["company_id"] == cid].sort_values("year")
        co_cf = cf[cf["company_id"] == cid].sort_values("year")

        n_years = co_pnl["year"].nunique()
        revenue_cagr = pat_cagr = eps_cagr = None
        net_profit_margin = None
        latest_fcf = None
        debt_equity = None

        if len(co_pnl) >= 2:
            first, last = co_pnl.iloc[0], co_pnl.iloc[-1]
            years_span = max(len(co_pnl["year"].unique()) - 1, 1)
            revenue_cagr = _cagr(first.get("sales"), last.get("sales"), years_span)
            pat_cagr = _cagr(first.get("net_profit"), last.get("net_profit"), years_span)
            eps_cagr = _cagr(first.get("eps"), last.get("eps"), years_span)
            if last.get("sales"):
                net_profit_margin = (last.get("net_profit") or 0) / last["sales"] * 100

        if not co_bs.empty:
            last_bs = co_bs.iloc[-1]
            equity = (last_bs.get("equity_capital") or 0) + (last_bs.get("reserves") or 0)
            if equity:
                debt_equity = (last_bs.get("borrowings") or 0) / equity

        if not co_cf.empty:
            latest_fcf = co_cf.iloc[-1].get("operating_activity")

        rows.append(
            {
                "id": cid,
                "company_name": co["company_name"],
                "roe_percentage": co.get("roe_percentage"),
                "roce_percentage": co.get("roce_percentage"),
                "net_profit_margin_percentage": net_profit_margin,
                "revenue_cagr_percentage": revenue_cagr,
                "pat_cagr_percentage": pat_cagr,
                "eps_cagr_percentage": eps_cagr,
                "debt_to_equity": debt_equity,
                "latest_operating_cash_flow": latest_fcf,
                "years_of_data": n_years,
            }
        )

    df = pd.DataFrame(rows)

    # Simple 0-100 composite health score: average of min-max normalized
    # ROE, ROCE, net margin, and revenue CAGR (higher debt/equity penalized).
    score_cols = ["roe_percentage", "roce_percentage", "net_profit_margin_percentage", "revenue_cagr_percentage"]
    norm = pd.DataFrame(index=df.index)
    for c in score_cols:
        col = df[c]
        rng = col.max() - col.min()
        norm[c] = 0 if rng == 0 or pd.isna(rng) else (col - col.min()) / rng * 100
    debt_penalty = df["debt_to_equity"].fillna(0).clip(lower=0)
    debt_penalty_norm = (debt_penalty / debt_penalty.max() * 20) if debt_penalty.max() else 0

    df["financial_health_score"] = norm.mean(axis=1, skipna=True) - debt_penalty_norm
    df["financial_health_score"] = df["financial_health_score"].clip(lower=0, upper=100).round(1)

    return df.sort_values("financial_health_score", ascending=False).reset_index(drop=True)