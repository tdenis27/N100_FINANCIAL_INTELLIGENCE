"""
Nifty 100 Financial Intelligence Platform — ETL Loader (Module 1)

Reads the 7 core + 5 supplementary Excel files from data/raw and
data/supporting, normalises tickers and year labels, validates a subset of
the spec's data-quality rules, computes the financial ratio / CAGR /
capital-allocation fields the dashboard needs, and writes everything into a
single SQLite file: data/nifty100.db.

Run:
    python src/etl/loader.py   (or: make load)
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
SUPPORT = ROOT / "data" / "supporting"
DB_PATH = ROOT / "data" / "nifty100.db"
AUDIT_PATH = ROOT / "output" / "load_audit.csv"
DQ_PATH = ROOT / "output" / "validation_failures.csv"

MONTHS = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
    "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


# --------------------------------------------------------------------------- #
# Normalisers
# --------------------------------------------------------------------------- #
def normalize_ticker(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.upper()


def normalize_year(value) -> str | None:
    """Handle 'Mar-23', 'Mar 2014', 'Dec 2012', '2023', 'FY23', '2023-03', etc."""
    if pd.isna(value):
        return None
    s = str(value).strip()
    s = re.sub(r"^FY", "", s, flags=re.IGNORECASE)

    m = re.match(r"^(\d{4})-(\d{2})$", s)
    if m:
        return s

    m = re.match(r"^([A-Za-z]{3,})[\s\-]?(\d{2,4})$", s)
    if m:
        mon_raw, yr_raw = m.group(1)[:3].lower(), m.group(2)
        if mon_raw in MONTHS:
            year = int(yr_raw) if len(yr_raw) == 4 else 2000 + int(yr_raw)
            return f"{year}-{MONTHS[mon_raw]}"

    m = re.match(r"^\d{4}$", s)
    if m:
        return f"{s}-03"  # integer-year -> assume March FY close

    return None  # PARSE_ERROR


def fy_year_int(norm_year: str) -> int | None:
    """The reporting FY as a plain int, e.g. '2023-03' -> 2023."""
    if not norm_year:
        return None
    return int(norm_year.split("-")[0])


# --------------------------------------------------------------------------- #
# Loaders for the 7 core files (header row 1 per spec)
# --------------------------------------------------------------------------- #
def load_core(name: str) -> pd.DataFrame:
    return pd.read_excel(RAW / f"{name}.xlsx", header=1)


def load_supporting(name: str) -> pd.DataFrame:
    return pd.read_excel(SUPPORT / f"{name}.xlsx", header=0)


def build_all() -> dict[str, pd.DataFrame]:
    audit_rows = []
    dq_rows = []

    def audit(table, rows_in, rows_out, rejected):
        audit_rows.append(dict(table=table, rows_in=rows_in, rows_out=rows_out, rejected=rejected))

    def flag(company_id, year, field, issue, severity):
        dq_rows.append(dict(company_id=company_id, year=year, field=field, issue=issue, severity=severity))

    # ---- companies -------------------------------------------------------
    companies = load_core("companies")
    companies["id"] = normalize_ticker(companies["id"])
    companies["company_name"] = companies["company_name"].astype(str).str.replace("\n", " ").str.strip()
    before = len(companies)
    companies = companies.drop_duplicates(subset="id")
    audit("companies", before, len(companies), before - len(companies))
    valid_ids = set(companies["id"])

    # ---- profitandloss -----------------------------------------------------
    pl = load_core("profitandloss")
    pl["company_id"] = normalize_ticker(pl["company_id"])
    before = len(pl)
    pl["year"] = pl["year"].apply(normalize_year)
    pl = pl[pl["company_id"].isin(valid_ids) & pl["year"].notna()]
    pl = pl.drop_duplicates(subset=["company_id", "year"], keep="last")
    audit("profitandloss", before, len(pl), before - len(pl))
    for _, r in pl.iterrows():
        if r["sales"] and r["sales"] != 0:
            computed_opm = r["operating_profit"] / r["sales"] * 100
            if abs(computed_opm - r["opm_percentage"]) > 1.0:
                flag(r["company_id"], r["year"], "opm_percentage", "OPM cross-check mismatch >1%", "WARNING")
        else:
            flag(r["company_id"], r["year"], "sales", "sales<=0", "WARNING")

    # ---- balancesheet -------------------------------------------------------
    bs = load_core("balancesheet")
    bs["company_id"] = normalize_ticker(bs["company_id"])
    before = len(bs)
    bs["year"] = bs["year"].apply(normalize_year)
    bs = bs[bs["company_id"].isin(valid_ids) & bs["year"].notna()]
    bs = bs.drop_duplicates(subset=["company_id", "year"], keep="last")
    audit("balancesheet", before, len(bs), before - len(bs))
    for _, r in bs.iterrows():
        if r["total_assets"]:
            diff = abs(r["total_assets"] - r["total_liabilities"]) / max(abs(r["total_assets"]), 1)
            if diff > 0.01:
                flag(r["company_id"], r["year"], "total_assets", "BS does not balance >1%", "WARNING")

    # ---- cashflow -------------------------------------------------------
    cf = load_core("cashflow")
    cf["company_id"] = normalize_ticker(cf["company_id"])
    before = len(cf)
    cf["year"] = cf["year"].apply(normalize_year)
    cf = cf[cf["company_id"].isin(valid_ids) & cf["year"].notna()]
    cf = cf.drop_duplicates(subset=["company_id", "year"], keep="last")
    audit("cashflow", before, len(cf), before - len(cf))
    for _, r in cf.iterrows():
        parts = [r.get("operating_activity", 0) or 0, r.get("investing_activity", 0) or 0, r.get("financing_activity", 0) or 0]
        if r.get("net_cash_flow") is not None and abs(sum(parts) - r["net_cash_flow"]) > 10:
            flag(r["company_id"], r["year"], "net_cash_flow", "CFO+CFI+CFF mismatch >10cr", "WARNING")

    # ---- analysis / documents / prosandcons -------------------------------
    analysis = load_core("analysis")
    analysis["company_id"] = normalize_ticker(analysis["company_id"])
    audit("analysis", len(analysis), len(analysis), 0)

    documents = load_core("documents")
    documents["company_id"] = normalize_ticker(documents["company_id"])
    audit("documents", len(documents), len(documents), 0)

    prosandcons = load_core("prosandcons")
    prosandcons["company_id"] = normalize_ticker(prosandcons["company_id"])
    audit("prosandcons", len(prosandcons), len(prosandcons), 0)

    # ---- supplementary ------------------------------------------------------
    sectors = load_supporting("sectors")
    sectors["company_id"] = normalize_ticker(sectors["company_id"])
    audit("sectors", len(sectors), len(sectors), 0)

    stock_prices = load_supporting("stock_prices")
    stock_prices["company_id"] = normalize_ticker(stock_prices["company_id"])
    audit("stock_prices", len(stock_prices), len(stock_prices), 0)

    market_cap = load_supporting("market_cap")
    market_cap["company_id"] = normalize_ticker(market_cap["company_id"])
    audit("market_cap", len(market_cap), len(market_cap), 0)

    financial_ratios = load_supporting("financial_ratios")
    financial_ratios["company_id"] = normalize_ticker(financial_ratios["company_id"])
    financial_ratios["year"] = financial_ratios["year"].apply(normalize_year)
    audit("financial_ratios", len(financial_ratios), len(financial_ratios), 0)

    peer_groups = load_supporting("peer_groups")
    peer_groups["company_id"] = normalize_ticker(peer_groups["company_id"])
    audit("peer_groups", len(peer_groups), len(peer_groups), 0)

    pd.DataFrame(audit_rows).to_csv(AUDIT_PATH, index=False)
    pd.DataFrame(dq_rows).to_csv(DQ_PATH, index=False)

    return dict(
        companies=companies, profitandloss=pl, balancesheet=bs, cashflow=cf,
        analysis=analysis, documents=documents, prosandcons=prosandcons,
        sectors=sectors, stock_prices=stock_prices, market_cap=market_cap,
        financial_ratios=financial_ratios, peer_groups=peer_groups,
    )


# --------------------------------------------------------------------------- #
# Derived analytics: CAGR, capital allocation pattern, composite score
# --------------------------------------------------------------------------- #
def cagr(start, end, years):
    if start is None or end is None or years <= 0:
        return None
    if start <= 0:  # turnaround / both-negative / zero-base -> None per spec
        return None
    if end <= 0:
        return None
    return ((end / start) ** (1 / years) - 1) * 100


def compute_growth(pl: pd.DataFrame) -> pd.DataFrame:
    """Revenue / PAT / EPS CAGR (3/5/10yr) per company, evaluated as of latest year."""
    rows = []
    for cid, g in pl.groupby("company_id"):
        g = g.dropna(subset=["year"]).sort_values("year")
        g["fy"] = g["year"].apply(fy_year_int)
        g = g.drop_duplicates(subset="fy").set_index("fy")
        if g.empty:
            continue
        latest_fy = g.index.max()
        rec = dict(company_id=cid, latest_year=g.loc[latest_fy, "year"])
        for horizon in (3, 5, 10):
            base_fy = latest_fy - horizon
            if base_fy in g.index:
                rec[f"revenue_cagr_{horizon}yr"] = cagr(g.loc[base_fy, "sales"], g.loc[latest_fy, "sales"], horizon)
                rec[f"pat_cagr_{horizon}yr"] = cagr(g.loc[base_fy, "net_profit"], g.loc[latest_fy, "net_profit"], horizon)
                rec[f"eps_cagr_{horizon}yr"] = cagr(g.loc[base_fy, "eps"], g.loc[latest_fy, "eps"], horizon)
            else:
                rec[f"revenue_cagr_{horizon}yr"] = None
                rec[f"pat_cagr_{horizon}yr"] = None
                rec[f"eps_cagr_{horizon}yr"] = None
        rec["years_of_history"] = len(g)
        rows.append(rec)
    return pd.DataFrame(rows)


CAP_PATTERNS = {
    (1, -1, -1): "Reinvestor / Shareholder Returns",
    (1, -1, 1): "Growth via External Capital",
    (1, 1, -1): "Divesting & Returning Capital",
    (1, 1, 1): "Divesting & Building Cash",
    (-1, -1, 1): "Distress — Funding Ops via Debt/Equity",
    (-1, -1, -1): "Severe Distress — Depleting Reserves",
    (-1, 1, -1): "Asset Sale to Fund Operations",
    (-1, 1, 1): "Asset Sale + External Capital",
}


def sign(x):
    if x is None or pd.isna(x):
        return 0
    return 1 if x > 0 else (-1 if x < 0 else 0)


def compute_capital_allocation(cf: pd.DataFrame) -> pd.DataFrame:
    df = cf.copy()
    df["cfo_sign"] = df["operating_activity"].apply(sign)
    df["cfi_sign"] = df["investing_activity"].apply(sign)
    df["cff_sign"] = df["financing_activity"].apply(sign)
    df["pattern_label"] = df.apply(
        lambda r: CAP_PATTERNS.get((r["cfo_sign"], r["cfi_sign"], r["cff_sign"]), "Mixed / Undefined"), axis=1
    )
    return df[["company_id", "year", "cfo_sign", "cfi_sign", "cff_sign", "pattern_label"]]


def compute_cashflow_intelligence(cf: pd.DataFrame, pl: pd.DataFrame) -> pd.DataFrame:
    merged = cf.merge(pl[["company_id", "year", "net_profit", "sales", "operating_profit"]], on=["company_id", "year"], how="left")
    merged["fcf"] = merged["operating_activity"] + merged["investing_activity"]
    merged["cfo_pat_ratio"] = merged.apply(
        lambda r: r["operating_activity"] / r["net_profit"] if r["net_profit"] not in (0, None) and not pd.isna(r["net_profit"]) else None, axis=1
    )
    merged["capex_intensity_pct"] = merged.apply(
        lambda r: abs(r["investing_activity"]) / r["sales"] * 100 if r["sales"] not in (0, None) and not pd.isna(r["sales"]) else None, axis=1
    )
    merged["fcf_conversion_pct"] = merged.apply(
        lambda r: r["fcf"] / r["operating_profit"] * 100 if r["operating_profit"] not in (0, None) and not pd.isna(r["operating_profit"]) else None, axis=1
    )
    merged["distress_flag"] = (merged["operating_activity"] < 0) & (merged["financing_activity"] > 0)
    return merged[["company_id", "year", "fcf", "cfo_pat_ratio", "capex_intensity_pct", "fcf_conversion_pct", "distress_flag"]]


def compute_composite_score(latest: pd.DataFrame) -> pd.Series:
    """Simplified version of the spec's weighted composite quality score (0-100),
    using winsorised (P10-P90) min-max scaling on the metrics we have."""
    def scale(s, higher_is_better=True):
        lo, hi = s.quantile(0.10), s.quantile(0.90)
        if hi == lo:
            return pd.Series(50.0, index=s.index)
        clipped = s.clip(lo, hi)
        scaled = (clipped - lo) / (hi - lo) * 100
        return scaled if higher_is_better else (100 - scaled)

    roe_s = scale(latest["return_on_equity_pct"].fillna(latest["return_on_equity_pct"].median()))
    npm_s = scale(latest["net_profit_margin_pct"].fillna(latest["net_profit_margin_pct"].median()))
    fcf_s = scale(latest["free_cash_flow_cr"].fillna(0), higher_is_better=True)
    de_s = scale(latest["debt_to_equity"].fillna(latest["debt_to_equity"].median()), higher_is_better=False)
    return (0.35 * roe_s + 0.15 * npm_s + 0.30 * fcf_s + 0.20 * de_s).round(1)


# --------------------------------------------------------------------------- #
# Persist to SQLite
# --------------------------------------------------------------------------- #
def write_sqlite(tables: dict[str, pd.DataFrame]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    with sqlite3.connect(DB_PATH) as conn:
        for name, df in tables.items():
            df.to_sql(name, conn, index=False)
        conn.execute("CREATE INDEX idx_pl_company ON profitandloss(company_id)")
        conn.execute("CREATE INDEX idx_bs_company ON balancesheet(company_id)")
        conn.execute("CREATE INDEX idx_cf_company ON cashflow(company_id)")
        conn.execute("CREATE INDEX idx_fr_company ON financial_ratios(company_id)")
        conn.execute("CREATE INDEX idx_mc_company ON market_cap(company_id)")
        conn.commit()


def main():
    tables = build_all()

    growth = compute_growth(tables["profitandloss"])
    capital = compute_capital_allocation(tables["cashflow"])
    cf_intel = compute_cashflow_intelligence(tables["cashflow"], tables["profitandloss"])

    # latest-year financial_ratios snapshot per company, joined with growth + sector + market cap
    fr = tables["financial_ratios"].copy()
    fr["fy"] = fr["year"].apply(fy_year_int)
    latest_fr = fr.sort_values("fy").groupby("company_id").tail(1).reset_index(drop=True)

    mc = tables["market_cap"].copy()
    latest_mc = mc.sort_values("year").groupby("company_id").tail(1).reset_index(drop=True)

    snapshot = (
        latest_fr.merge(tables["companies"][["id", "company_name", "about_company", "face_value"]], left_on="company_id", right_on="id", how="left")
        .merge(tables["sectors"][["company_id", "broad_sector", "sub_sector", "market_cap_category"]], on="company_id", how="left")
        .merge(latest_mc.drop(columns=["id", "year"], errors="ignore"), on="company_id", how="left")
        .merge(growth, on="company_id", how="left")
        .merge(capital.sort_values("year").groupby("company_id").tail(1)[["company_id", "pattern_label"]], on="company_id", how="left")
    )
    snapshot["composite_score"] = compute_composite_score(snapshot)
    snapshot = snapshot.drop(columns=["id"], errors="ignore")

    tables["latest_snapshot"] = snapshot
    tables["growth_metrics"] = growth
    tables["capital_allocation"] = capital
    tables["cashflow_intelligence"] = cf_intel

    write_sqlite(tables)
    print(f"Loaded {len(tables)} tables into {DB_PATH}")
    for name, df in tables.items():
        print(f"  {name:22s} {len(df):>6} rows")


if __name__ == "__main__":
    main()
