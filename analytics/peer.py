from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "output"
    / "company_financial_metrics.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "peer_comparison.xlsx"
)


def calculate_peer_rankings():

    df = pd.read_csv(INPUT_FILE)

    metrics = [
        "financial_health_score",
        "roe_percentage",
        "roce_percentage",
        "net_profit_margin_percentage",
        "revenue_cagr_percentage",
        "pat_cagr_percentage",
        "eps_cagr_percentage"
    ]

    for metric in metrics:
        if metric in df.columns:
            df[f"{metric}_rank"] = (
                df[metric]
                .rank(
                    ascending=False,
                    method="dense"
                )
            )

    if "financial_health_score" in df.columns:
        df = df.sort_values(
            "financial_health_score",
            ascending=False
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_excel(
        OUTPUT_FILE,
        index=False
    )

    print("=" * 60)
    print("PEER COMPARISON COMPLETED")
    print("=" * 60)
    print(df.head(20))


if __name__ == "__main__":
    calculate_peer_rankings()