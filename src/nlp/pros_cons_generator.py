from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = PROJECT_ROOT / "output" / "analysis_parsed.csv"
OUTPUT_FILE = PROJECT_ROOT / "output" / "pros_cons_generated.csv"


def add_rule(rows, company_id, rule_id, rule_type, text, confidence):
    if confidence > 60:
        rows.append({
            "company_id": company_id,
            "type": rule_type,
            "rule_id": rule_id,
            "text": text,
            "confidence_pct": confidence
        })


def main():

    print("=" * 60)
    print("DAY 30 - PROS & CONS GENERATOR")
    print("=" * 60)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Missing input: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        raise ValueError(
            "analysis_parsed.csv is empty. "
            "Complete Day 29 successfully first."
        )

    rows = []

    # Convert long format into company-level metrics
    pivot = df.pivot_table(
        index="company_id",
        columns="metric_type",
        values="value_pct",
        aggfunc="first"
    ).reset_index()

    # --------------------------------------------------------
    # 12 PRO RULES
    # --------------------------------------------------------

    for _, row in pivot.iterrows():

        company = row["company_id"]

        sales = row.get(
            "compounded_sales_growth"
        )

        profit = row.get(
            "compounded_profit_growth"
        )

        stock = row.get(
            "stock_price_cagr"
        )

        roe = row.get("roe")

        # PRO 01
        if pd.notna(sales) and sales > 15:
            add_rule(
                rows,
                company,
                "PRO_01",
                "Pro",
                "Strong compounded sales growth above 15%.",
                90
            )

        # PRO 02
        if pd.notna(sales) and sales > 10:
            add_rule(
                rows,
                company,
                "PRO_02",
                "Pro",
                "Healthy long-term sales growth.",
                80
            )

        # PRO 03
        if pd.notna(profit) and profit > 15:
            add_rule(
                rows,
                company,
                "PRO_03",
                "Pro",
                "Strong compounded profit growth above 15%.",
                90
            )

        # PRO 04
        if pd.notna(profit) and profit > 10:
            add_rule(
                rows,
                company,
                "PRO_04",
                "Pro",
                "Healthy long-term profit growth.",
                80
            )

        # PRO 05
        if pd.notna(roe) and roe > 20:
            add_rule(
                rows,
                company,
                "PRO_05",
                "Pro",
                "High return on equity above 20%.",
                90
            )

        # PRO 06
        if pd.notna(roe) and roe > 15:
            add_rule(
                rows,
                company,
                "PRO_06",
                "Pro",
                "Good return on equity.",
                80
            )

        # PRO 07
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and sales > 10
            and profit > 10
        ):
            add_rule(
                rows,
                company,
                "PRO_07",
                "Pro",
                "Sales and profit are both growing strongly.",
                95
            )

        # PRO 08
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and profit > sales
        ):
            add_rule(
                rows,
                company,
                "PRO_08",
                "Pro",
                "Profit growth is exceeding sales growth.",
                85
            )

        # PRO 09
        if pd.notna(stock) and stock > 15:
            add_rule(
                rows,
                company,
                "PRO_09",
                "Pro",
                "Strong long-term stock price CAGR.",
                85
            )

        # PRO 10
        if (
            pd.notna(stock)
            and pd.notna(sales)
            and stock > 0
            and sales > 0
        ):
            add_rule(
                rows,
                company,
                "PRO_10",
                "Pro",
                "Positive stock performance alongside business growth.",
                75
            )

        # PRO 11
        if (
            pd.notna(roe)
            and pd.notna(profit)
            and roe > 15
            and profit > 10
        ):
            add_rule(
                rows,
                company,
                "PRO_11",
                "Pro",
                "Strong profitability supported by healthy ROE.",
                90
            )

        # PRO 12
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and sales > 10
            and profit > 10
        ):
            add_rule(
                rows,
                company,
                "PRO_12",
                "Pro",
                "Consistent business growth profile.",
                80
            )

        # ----------------------------------------------------
        # 12 CON RULES
        # ----------------------------------------------------

        # CON 01
        if pd.notna(sales) and sales < 0:
            add_rule(
                rows,
                company,
                "CON_01",
                "Con",
                "Negative compounded sales growth.",
                95
            )

        # CON 02
        if pd.notna(sales) and sales < 5:
            add_rule(
                rows,
                company,
                "CON_02",
                "Con",
                "Weak sales growth below 5%.",
                75
            )

        # CON 03
        if pd.notna(profit) and profit < 0:
            add_rule(
                rows,
                company,
                "CON_03",
                "Con",
                "Negative compounded profit growth.",
                95
            )

        # CON 04
        if pd.notna(profit) and profit < 5:
            add_rule(
                rows,
                company,
                "CON_04",
                "Con",
                "Weak profit growth below 5%.",
                75
            )

        # CON 05
        if pd.notna(roe) and roe < 10:
            add_rule(
                rows,
                company,
                "CON_05",
                "Con",
                "Low return on equity.",
                80
            )

        # CON 06
        if pd.notna(roe) and roe < 0:
            add_rule(
                rows,
                company,
                "CON_06",
                "Con",
                "Negative return on equity.",
                95
            )

        # CON 07
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and sales > 0
            and profit < 0
        ):
            add_rule(
                rows,
                company,
                "CON_07",
                "Con",
                "Sales growth is positive but profit growth is negative.",
                90
            )

        # CON 08
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and sales > profit
            and sales > 5
        ):
            add_rule(
                rows,
                company,
                "CON_08",
                "Con",
                "Profit growth is trailing sales growth.",
                70
            )

        # CON 09
        if pd.notna(stock) and stock < 0:
            add_rule(
                rows,
                company,
                "CON_09",
                "Con",
                "Negative long-term stock price CAGR.",
                95
            )

        # CON 10
        if (
            pd.notna(stock)
            and pd.notna(sales)
            and stock < 0
            and sales > 0
        ):
            add_rule(
                rows,
                company,
                "CON_10",
                "Con",
                "Stock performance is negative despite business growth.",
                85
            )

        # CON 11
        if (
            pd.notna(profit)
            and pd.notna(roe)
            and profit < 5
            and roe < 10
        ):
            add_rule(
                rows,
                company,
                "CON_11",
                "Con",
                "Weak profit growth and low ROE.",
                85
            )

        # CON 12
        if (
            pd.notna(sales)
            and pd.notna(profit)
            and sales < 5
            and profit < 5
        ):
            add_rule(
                rows,
                company,
                "CON_12",
                "Con",
                "Both sales and profit growth are weak.",
                85
            )

    # --------------------------------------------------------
    # SAVE
    # --------------------------------------------------------

    result = pd.DataFrame(
        rows,
        columns=[
            "company_id",
            "type",
            "rule_id",
            "text",
            "confidence_pct"
        ]
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nGenerated rows:", len(result))
    print("Output:", OUTPUT_FILE)

    if not result.empty:
        print("\nPros:")
        print(
            (result["type"] == "Pro").sum()
        )

        print("Cons:")
        print(
            (result["type"] == "Con").sum()
        )

        coverage = result.groupby(
            ["company_id", "type"]
        ).size().unstack(fill_value=0)

        print("\nCompany coverage:")
        print(coverage.head(10))


if __name__ == "__main__":
    main()