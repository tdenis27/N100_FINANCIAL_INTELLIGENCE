"""
Generates a SQLite database of mock financial data for 92 NIFTY-100-style
companies across 11 sectors, 10 years of history (2015-2024).

Replace this with your real data ingestion pipeline (BSE/NSE feeds,
market_cap.xlsx, etc.) — the dashboard only depends on the schema below,
not on how the data got there.

Run:
    python scripts/generate_mock_data.py
"""
import sqlite3
import random
from pathlib import Path

random.seed(42)

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "nifty100.db"

SECTORS = {
    "IT": ["TCS", "Infosys", "Wipro", "HCL Tech", "Tech Mahindra", "LTIMindtree", "Mphasis", "Persistent", "Coforge"],
    "Financials": ["HDFC Bank", "ICICI Bank", "SBI", "Kotak Bank", "Axis Bank", "Bajaj Finance", "IndusInd Bank", "Bandhan Bank", "Chola Finance", "Shriram Finance", "PNB", "Bank of Baroda", "SBI Life", "HDFC Life", "ICICI Lombard"],
    "FMCG": ["HUL", "ITC", "Nestle India", "Britannia", "Dabur", "Godrej Consumer", "Marico", "Colgate", "Tata Consumer"],
    "Energy": ["Reliance", "ONGC", "IOC", "BPCL", "Coal India", "NTPC", "Power Grid", "Adani Green", "Tata Power"],
    "Healthcare": ["Sun Pharma", "Dr Reddy's", "Cipla", "Divi's Labs", "Apollo Hospitals", "Lupin", "Aurobindo Pharma", "Biocon", "Max Healthcare"],
    "Auto": ["Maruti Suzuki", "Tata Motors", "M&M", "Bajaj Auto", "Eicher Motors", "Hero MotoCorp", "TVS Motor", "Ashok Leyland"],
    "Metals": ["Tata Steel", "JSW Steel", "Hindalco", "Vedanta", "SAIL", "Jindal Steel", "NMDC", "APL Apollo"],
    "Cement": ["UltraTech", "Shree Cement", "Ambuja Cement", "ACC", "Dalmia Bharat", "JK Cement"],
    "Telecom": ["Bharti Airtel", "Vodafone Idea", "Indus Towers", "Tata Communications"],
    "Infra": ["Larsen & Toubro", "Adani Ports", "GMR Infra", "IRB Infra", "Adani Enterprises", "NBCC", "Rail Vikas Nigam"],
    "Consumer Durables": ["Titan", "Havells", "Voltas", "Asian Paints", "Berger Paints", "Bata India", "Crompton Greaves", "Whirlpool India"],
}

YEARS = list(range(2015, 2025))


def make_ticker(name: str) -> str:
    letters = "".join(ch for ch in name.upper() if ch.isalpha())
    return letters[:8]


def build():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE companies (
            company_id INTEGER PRIMARY KEY,
            company_name TEXT NOT NULL,
            ticker TEXT UNIQUE NOT NULL,
            sector TEXT NOT NULL,
            sub_sector TEXT NOT NULL,
            about TEXT NOT NULL
        );

        CREATE TABLE financials (
            company_id INTEGER,
            year INTEGER,
            revenue REAL,
            net_profit REAL,
            roe REAL,
            roce REAL,
            debt_to_equity REAL,
            pe REAL,
            pb REAL,
            fcf REAL,
            market_cap REAL,
            PRIMARY KEY (company_id, year),
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE capital_allocation (
            company_id INTEGER PRIMARY KEY,
            pattern TEXT NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );
        """
    )

    patterns = [
        "Reinvest & Expand", "Debt Paydown", "Dividend Payer", "Buyback Heavy",
        "M&A Roll-up", "Capex Heavy", "Cash Hoarder", "Turnaround",
    ]

    company_id = 1
    companies_rows = []
    financials_rows = []
    capital_rows = []

    for sector, names in SECTORS.items():
        for name in names:
            ticker = make_ticker(name)
            sub_sector = f"{sector} - {'Large Cap' if random.random() > 0.4 else 'Mid Cap'}"
            about = f"{name} is a leading player in the {sector} sector, listed on NSE as {ticker}."
            companies_rows.append((company_id, name, ticker, sector, sub_sector, about))

            base_revenue = random.uniform(5000, 150000)  # in crore
            base_margin = random.uniform(0.05, 0.25)
            growth = random.uniform(0.03, 0.18)
            base_mcap = base_revenue * random.uniform(1.5, 6)

            # ~10% of companies get sparse (partial) history to exercise edge cases
            sparse = random.random() < 0.1
            years_for_company = random.sample(YEARS, k=random.randint(4, 6)) if sparse else YEARS

            revenue = base_revenue
            for year in YEARS:
                if year not in years_for_company:
                    continue
                revenue *= (1 + growth + random.uniform(-0.03, 0.03))
                net_profit = revenue * (base_margin + random.uniform(-0.02, 0.02))
                roe = max(1, min(45, random.gauss(18, 7)))
                roce = max(1, min(40, roe * random.uniform(0.8, 1.1)))
                de = max(0, random.gauss(0.6, 0.5))
                pe = max(3, random.gauss(24, 10))
                pb = max(0.5, random.gauss(3.5, 1.8))
                mcap = base_mcap * (1 + growth) ** (year - YEARS[0]) * random.uniform(0.85, 1.15)
                fcf = net_profit * random.uniform(0.5, 1.1)

                financials_rows.append(
                    (company_id, year, round(revenue, 1), round(net_profit, 1), round(roe, 1),
                     round(roce, 1), round(de, 2), round(pe, 1), round(pb, 2), round(fcf, 1), round(mcap, 1))
                )

            capital_rows.append((company_id, random.choice(patterns)))
            company_id += 1

    cur.executemany(
        "INSERT INTO companies VALUES (?, ?, ?, ?, ?, ?)", companies_rows
    )
    cur.executemany(
        "INSERT INTO financials VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", financials_rows
    )
    cur.executemany(
        "INSERT INTO capital_allocation VALUES (?, ?)", capital_rows
    )

    conn.commit()
    conn.close()
    print(f"Built {DB_PATH} with {len(companies_rows)} companies, {len(financials_rows)} financial rows.")


if __name__ == "__main__":
    build()
