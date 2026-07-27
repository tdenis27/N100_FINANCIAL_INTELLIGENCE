from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "reports" / "radar_charts"


RADAR_METRICS = [
    "roe",
    "roce",
    "net_profit_margin",
    "debt_equity",
    "fcf",
    "pat_cagr_5yr",
    "revenue_cagr_5yr",
    "composite_quality_score",
]


def normalise(series):
    series = pd.to_numeric(
        series,
        errors="coerce"
    )

    minimum = series.min()
    maximum = series.max()

    if pd.isna(minimum) or pd.isna(maximum):
        return series.fillna(0)

    if maximum == minimum:
        return pd.Series(
            50,
            index=series.index
        )

    return (
        (series - minimum)
        / (maximum - minimum)
        * 100
    ).fillna(0)


def generate_radar_charts(df):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    data = df.copy()

    available = [
        metric
        for metric in RADAR_METRICS
        if metric in data.columns
    ]

    for metric in available:
        data[f"{metric}_radar"] = normalise(
            data[metric]
        )

    radar_columns = [
        f"{metric}_radar"
        for metric in available
    ]

    angles = np.linspace(
        0,
        2 * np.pi,
        len(available),
        endpoint=False
    ).tolist()

    angles += angles[:1]

    for _, company in data.iterrows():

        values = [
            company[column]
            for column in radar_columns
        ]

        values += values[:1]

        peer_name = company.get(
            "peer_group_name"
        )

        if pd.notna(peer_name):

            peers = data[
                data["peer_group_name"]
                == peer_name
            ]

        else:
            peers = data

        averages = [
            peers[column].mean()
            for column in radar_columns
        ]

        averages += averages[:1]

        fig = plt.figure(figsize=(8, 8))

        ax = fig.add_subplot(
            111,
            polar=True
        )

        ax.plot(
            angles,
            values,
            linewidth=2,
            label="Company"
        )

        ax.fill(
            angles,
            values,
            alpha=0.25
        )

        ax.plot(
            angles,
            averages,
            linewidth=2,
            linestyle="--",
            label="Peer Average"
        )

        ax.set_xticks(angles[:-1])

        ax.set_xticklabels(
            available,
            fontsize=9
        )

        company_name = str(
            company.get(
                "company_name",
                company.get(
                    "company_id",
                    "company"
                )
            )
        )

        ax.set_title(
            f"{company_name} - Peer Radar",
            pad=25
        )

        ax.legend(
            loc="upper right",
            bbox_to_anchor=(1.3, 1.1)
        )

        safe_name = "".join(
            character
            if character.isalnum()
            else "_"
            for character in company_name
        )

        filename = (
            OUTPUT_DIR
            / f"{safe_name}_radar.png"
        )

        plt.tight_layout()

        plt.savefig(
            filename,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close(fig)

    print(
        f"Radar charts created in: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    print("Radar chart module ready.")