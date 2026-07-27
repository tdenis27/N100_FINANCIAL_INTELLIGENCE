from pathlib import Path

import numpy as np
import pandas as pd
import sqlite3


ROOT = Path(__file__).resolve().parents[2]

METRICS = [
    "roe",
    "roce",
    "net_profit_margin",
    "debt_equity",
    "fcf",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "eps_cagr_5yr",
    "interest_coverage",
    "asset_turnover",
]


def percent_rank(series):
    numeric = pd.to_numeric(series, errors="coerce")

    return numeric.rank(
        method="min",
        pct=True
    )


def calculate_peer_percentiles(df):
    required = {
        "company_id",
        "peer_group_name"
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    output = []

    valid = df[
        df["peer_group_name"].notna()
    ].copy()

    for peer_name, group in valid.groupby("peer_group_name"):

        group = group.copy()

        for metric in METRICS:

            if metric not in group.columns:
                continue

            ranks = percent_rank(group[metric])

            if metric == "debt_equity":
                ranks = 1 - ranks

            for index in group.index:

                output.append({
                    "company_id":
                        group.loc[index, "company_id"],

                    "peer_group_name":
                        peer_name,

                    "metric":
                        metric,

                    "value":
                        group.loc[index, metric],

                    "percentile_rank":
                        ranks.loc[index],

                    "year":
                        group.loc[index, "year"]
                        if "year" in group.columns
                        else None,
                })

    return pd.DataFrame(output)


def get_company_peer_group(df, company_id):

    company = df[
        df["company_id"] == company_id
    ]

    if company.empty:
        return "No peer group assigned"

    peer = company.iloc[0].get(
        "peer_group_name"
    )

    if pd.isna(peer) or str(peer).strip() == "":
        return "No peer group assigned"

    return peer


def save_to_sqlite(percentiles, database_path):

    connection = sqlite3.connect(database_path)

    try:
        percentiles.to_sql(
            "peer_percentiles",
            connection,
            if_exists="replace",
            index=False
        )

        connection.commit()

    finally:
        connection.close()

    print(
        f"Saved {len(percentiles)} percentile rows "
        "to peer_percentiles."
    )


if __name__ == "__main__":
    print("Peer percentile engine ready.")