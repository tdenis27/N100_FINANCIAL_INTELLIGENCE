# Nifty 100 Analytics Dashboard

An 8-screen Streamlit dashboard covering company profiles, screening, peer
comparison, trends, sector analysis, capital allocation, and annual reports —
built on **real** Nifty 100 financial statement data (92 companies, 7 core +
5 supplementary datasets), per the Nifty 100 Financial Intelligence Platform
project specification.

## Setup

```bash
pip install -r requirements.txt
```

## 1. Build the database (ETL)

Source workbooks live in `data/raw/` (7 core files: companies, P&L, balance
sheet, cash flow, analysis, documents, pros & cons) and `data/supporting/`
(5 supplementary files: sectors, stock_prices, market_cap, financial_ratios,
peer_groups).

```bash
python src/etl/loader.py
```

This:
- normalises tickers (`strip().upper()`) and year labels (`Mar-23`, `Dec 2012`,
  `FY23`, `2023` → `YYYY-MM`)
- drops duplicate `(company_id, year)` rows and orphan rows with no matching
  company
- flags data-quality issues (OPM cross-check, balance sheet imbalance,
  CFO+CFI+CFF mismatch) to `output/validation_failures.csv`
- writes a per-table load audit to `output/load_audit.csv`
- computes 3/5/10-year Revenue, PAT and EPS CAGR per company (with the
  turnaround/negative-base edge case → `None`, per spec)
- classifies each company's latest-year capital allocation pattern from the
  sign of CFO / CFI / CFF
- computes cash-flow quality metrics (CFO/PAT ratio, CapEx intensity, FCF
  conversion, distress flag)
- computes a simplified 0–100 composite quality score (35% ROE, 30% FCF,
  20% D/E, 15% NPM, winsorised P10–P90)
- loads everything into a single SQLite file: `data/nifty100.db`

## 2. Run the dashboard

```bash
streamlit run src/dashboard/app.py
```

Opens at `http://localhost:8501`.

## 3. Run the valuation module

```bash
python -m src.analytics.valuation
```

Produces:
- `output/valuation_summary.xlsx` — all 92 companies with P/E, P/B, FCF
  yield, sector-median P/E, and Caution/Discount/Fair flags
- `output/valuation_flags.csv` — only companies flagged Caution or Discount

## Screens

| # | Screen | File | What it shows |
|---|--------|------|----------------|
| 1 | Home | `pages/01_home.py` | 6 KPI tiles, market cap by sector, top-10 companies by composite score, capital allocation pattern breakdown |
| 2 | Company Profile | `pages/02_profile.py` | Search-driven company card, KPI tiles, sales/profit bar chart, ROE vs D/E chart, real pros & cons |
| 3 | Screener | `pages/03_screener.py` | Sector filter + 9 metric sliders, 6 preset screens (Quality Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue Chip, Turnaround Watch), live results, CSV export |
| 4 | Peer Comparison | `pages/04_peers.py` | 11 real peer groups (from `peer_groups.xlsx`), radar chart vs group average, percentile-ranked comparison table |
| 5 | Trend Analysis | `pages/05_trends.py` | Company search, up to 3 overlaid metrics across full reported history |
| 6 | Sector Analysis | `pages/06_sectors.py` | FCF vs ROE bubble chart (bubble = market cap), sector median KPI bar chart across all 11 broad sectors |
| 7 | Capital Allocation Map | `pages/07_capital.py` | Treemap of all 92 companies by capital allocation pattern, click-through company list |
| 8 | Annual Reports | `pages/08_reports.py` | Real BSE annual report links per company (from `documents.xlsx`) |

## Architecture

```
data/raw/                      7 core Excel files (companies, P&L, BS, CF, analysis, documents, pros&cons)
data/supporting/                5 supplementary Excel files (sectors, stock_prices, market_cap, financial_ratios, peer_groups)
data/nifty100.db                Built by the ETL loader — 16 tables (12 source + 4 derived)
src/etl/loader.py               Module 1 — ETL: normalise, validate, derive, persist
src/dashboard/app.py            Main entry point, sidebar nav
src/dashboard/pages/            8 screen files (01_home.py ... 08_reports.py)
src/dashboard/utils/db.py       Cached (@st.cache_data ttl=600) data-access layer
src/analytics/valuation.py      Module 6 — FCF yield + overvaluation/discount flags
output/                         load_audit.csv, validation_failures.csv, valuation_summary.xlsx, valuation_flags.csv
```

## Data notes

- `stock_prices.xlsx` and `market_cap.xlsx` are **simulated** datasets
  (created to augment the real P&L/BS/CF data, per the project spec) — treat
  P/E, P/B, EV/EBITDA, dividend yield, and monthly OHLCV as illustrative, not
  live market data.
- `analysis.xlsx` and `prosandcons.xlsx` have partial coverage (~8 of 92
  companies) in the source data — the dashboard shows what's available and
  degrades gracefully where it's missing.
- `peer_groups.xlsx` covers 46 of 92 companies across 11 defined peer groups;
  companies not in any group won't appear in the Peer Comparison screen.

## Known limitations / possible next steps

- Composite quality score is a simplified version of the spec's full
  50/30/20 profitability/cash-quality/growth-leverage weighting — extend
  `compute_composite_score()` in `src/etl/loader.py` for the full formula.
- No PDF tearsheet generator, FastAPI layer, KMeans clustering, or NLP
  pros/cons auto-generator yet (Modules 8–10 in the full spec) — the ETL +
  ratio engine + dashboard + valuation module (Modules 1, 2, 5, 6) are
  implemented and running on real data.
- Annual report URLs are not HEAD-checked for 404s (DQ-13 in the spec);
  broken links will just fail to open.
