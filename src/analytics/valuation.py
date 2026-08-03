"""
Valuation module (Module 6) — computes, for every company:
  - FCF yield (%)          = free_cash_flow_cr / market_cap_crore * 100
  - sector median P/E       = median P/E of all companies in the same broad_sector, latest year
  - PE vs sector median (%) = (company P/E - sector median) / sector median * 100
  - flag:
        "Caution"  if P/E > sector_median * 1.5
        "Discount" if P/E < sector_median * 0.7
        "Fair"     otherwise

Outputs:
  output/valuation_summary.xlsx  — all 92 companies, all valuation columns
  output/valuation_flags.csv     — only companies flagged Caution or Discount

Run directly:
    python -m src.analytics.valuation
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.dashboard.utils.db import get_latest_snapshot  # noqa: E402

OUTPUT_DIR = ROOT / "output"


def compute_valuation(snapshot: pd.DataFrame = None) -> pd.DataFrame:
    if snapshot is None:
        snapshot = get_latest_snapshot()

    df = snapshot.copy()

    df["fcf_yield_pct"] = (df["free_cash_flow_cr"] / df["market_cap_crore"] * 100).round(2)

    sector_median_pe = df.groupby("broad_sector")["pe_ratio"].median().rename("sector_median_pe")
    df = df.merge(sector_median_pe, on="broad_sector", how="left")

    df["pe_vs_sector_median_pct"] = ((df["pe_ratio"] - df["sector_median_pe"]) / df["sector_median_pe"] * 100).round(1)

    def flag_row(row):
        if pd.isna(row["pe_ratio"]) or pd.isna(row["sector_median_pe"]) or row["sector_median_pe"] == 0:
            return "N/A"
        if row["pe_ratio"] > row["sector_median_pe"] * 1.5:
            return "Caution"
        if row["pe_ratio"] < row["sector_median_pe"] * 0.7:
            return "Discount"
        return "Fair"

    df["flag"] = df.apply(flag_row, axis=1)

    out = df.rename(columns={
        "pe_ratio": "PE", "pb_ratio": "PB", "broad_sector": "sector",
    })[[
        "company_id", "company_name", "sector", "PE", "PB",
        "fcf_yield_pct", "sector_median_pe", "pe_vs_sector_median_pct", "flag",
    ]].rename(columns={
        "fcf_yield_pct": "FCF_yield_pct",
        "sector_median_pe": "sector_median_PE",
        "pe_vs_sector_median_pct": "PE_vs_sector_median_pct",
    })

    return out


def write_outputs(df: pd.DataFrame = None):
    if df is None:
        df = compute_valuation()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    summary_path = OUTPUT_DIR / "valuation_summary.xlsx"
    df.to_excel(summary_path, index=False, sheet_name="valuation_summary")

    flags_path = OUTPUT_DIR / "valuation_flags.csv"
    df[df["flag"].isin(["Caution", "Discount"])].to_csv(flags_path, index=False)

    return summary_path, flags_path


if __name__ == "__main__":
    result = compute_valuation()
    summary_path, flags_path = write_outputs(result)
    print(f"Wrote {len(result)} companies to {summary_path}")
    print(f"Wrote {result['flag'].isin(['Caution', 'Discount']).sum()} flagged companies to {flags_path}")
