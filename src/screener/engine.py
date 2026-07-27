"""
NIFTY 100 FINANCIAL INTELLIGENCE
Stock Screener Engine

Supports:
- Day 7 stock screener verification
- Sprint 3 filtering
- Composite quality scoring
"""

import numpy as np
import pandas as pd


# ============================================================
# DEFAULT DAY 7 CRITERIA
# ============================================================

DEFAULT_CRITERIA = {
    "min_roe_percentage": 15,
    "min_roce_percentage": 15,
    "max_debt_to_asset_ratio": 0.5,
    "min_revenue_cagr_percentage": 10,
    "min_pat_cagr_percentage": 10,
    "min_net_profit_margin_percentage": 5,
    "min_financial_health_score": 50,
    "allowed_ratings": None,
}


def _get_criteria(criteria):
    """
    Merge supplied criteria with defaults.
    """

    result = DEFAULT_CRITERIA.copy()

    if criteria is not None:
        result.update(criteria)

    return result


def _numeric(series):
    """
    Convert values safely to numeric.
    """

    return pd.to_numeric(
        series,
        errors="coerce"
    )


# ============================================================
# DAY 7 CHECK FUNCTIONS
# ============================================================

def check_roe(df, criteria=None):
    """
    Return Boolean mask for ROE threshold.
    """

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_roe_percentage"
    ]

    if "roe_percentage" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["roe_percentage"]
    )

    return (
        values >= threshold
    ).fillna(False)


def check_roce(df, criteria=None):
    """
    Return Boolean mask for ROCE threshold.
    """

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_roce_percentage"
    ]

    if "roce_percentage" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["roce_percentage"]
    )

    return (
        values >= threshold
    ).fillna(False)


def check_debt_to_asset(df, criteria=None):
    """
    Return Boolean mask for debt-to-asset threshold.
    """

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "max_debt_to_asset_ratio"
    ]

    if "debt_to_asset_ratio" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["debt_to_asset_ratio"]
    )

    return (
        values <= threshold
    ).fillna(False)


def check_rating(df, criteria=None):
    """
    Check whether company rating is in allowed_ratings.

    If allowed_ratings is None, every company passes.
    """

    criteria = _get_criteria(criteria)

    allowed = criteria.get(
        "allowed_ratings"
    )

    # Rating filter disabled
    if allowed is None:
        return pd.Series(
            True,
            index=df.index
        )

    if "financial_rating" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    allowed = [
        str(value).strip().upper()
        for value in allowed
    ]

    ratings = (
        df["financial_rating"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return ratings.isin(allowed)


# ============================================================
# OTHER DAY 7 CHECKS
# ============================================================

def check_revenue_cagr(df, criteria=None):

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_revenue_cagr_percentage"
    ]

    if "revenue_cagr_percentage" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["revenue_cagr_percentage"]
    )

    return (
        values >= threshold
    ).fillna(False)


def check_pat_cagr(df, criteria=None):

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_pat_cagr_percentage"
    ]

    if "pat_cagr_percentage" not in df.columns:
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["pat_cagr_percentage"]
    )

    return (
        values >= threshold
    ).fillna(False)


def check_net_profit_margin(
    df,
    criteria=None
):

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_net_profit_margin_percentage"
    ]

    if (
        "net_profit_margin_percentage"
        not in df.columns
    ):
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["net_profit_margin_percentage"]
    )

    return (
        values >= threshold
    ).fillna(False)


def check_financial_health(
    df,
    criteria=None
):

    criteria = _get_criteria(criteria)

    threshold = criteria[
        "min_financial_health_score"
    ]

    if (
        "financial_health_score"
        not in df.columns
    ):
        return pd.Series(
            False,
            index=df.index
        )

    values = _numeric(
        df["financial_health_score"]
    )

    return (
        values >= threshold
    ).fillna(False)


# ============================================================
# DAY 7 APPLY CRITERIA
# ============================================================

def apply_criteria(df, criteria=None):
    """
    Apply all Day 7 screening checks.

    Returns
    -------
    screened : DataFrame
        Companies passing every criterion.

    pass_counts : dict
        Number of companies passing each individual check.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "df must be a pandas DataFrame"
        )

    criteria = _get_criteria(criteria)

    masks = {
        "roe":
            check_roe(df, criteria),

        "roce":
            check_roce(df, criteria),

        "debt_to_asset":
            check_debt_to_asset(
                df,
                criteria
            ),

        "revenue_cagr":
            check_revenue_cagr(
                df,
                criteria
            ),

        "pat_cagr":
            check_pat_cagr(
                df,
                criteria
            ),

        "net_profit_margin":
            check_net_profit_margin(
                df,
                criteria
            ),

        "financial_health":
            check_financial_health(
                df,
                criteria
            ),

        "rating":
            check_rating(
                df,
                criteria
            ),
    }

    pass_counts = {
        name: int(mask.sum())
        for name, mask in masks.items()
    }

    combined = pd.Series(
        True,
        index=df.index
    )

    for mask in masks.values():
        combined &= mask.fillna(False)

    screened = (
        df.loc[combined]
        .copy()
        .reset_index(drop=True)
    )

    return screened, pass_counts


# ============================================================
# DAY 7 RANKING
# ============================================================

def rank_screened_companies(df):
    """
    Rank companies by financial_health_score descending.

    Highest score gets screen_rank = 1.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "df must be a pandas DataFrame"
        )

    result = df.copy()

    # Empty input must still have screen_rank.
    if result.empty:

        result["screen_rank"] = pd.Series(
            dtype="int64"
        )

        return result

    if (
        "financial_health_score"
        not in result.columns
    ):

        result[
            "financial_health_score"
        ] = 0

    result[
        "financial_health_score"
    ] = _numeric(
        result[
            "financial_health_score"
        ]
    ).fillna(0)

    result = (
        result
        .sort_values(
            by="financial_health_score",
            ascending=False,
            kind="stable"
        )
        .reset_index(drop=True)
    )

    result["screen_rank"] = (
        np.arange(
            1,
            len(result) + 1
        )
    )

    return result


# ============================================================
# SPRINT 3 FILTER MAP
# ============================================================

FILTER_MAP = {
    "roe_min":
        ("roe", "min"),

    "roce_min":
        ("roce", "min"),

    "de_max":
        ("debt_equity", "max"),

    "debt_equity_max":
        ("debt_equity", "max"),

    "fcf_min":
        ("fcf", "min"),

    "revenue_cagr_5yr_min":
        ("revenue_cagr_5yr", "min"),

    "pat_cagr_5yr_min":
        ("pat_cagr_5yr", "min"),

    "opm_min":
        ("opm", "min"),

    "pe_max":
        ("pe", "max"),

    "pb_max":
        ("pb", "max"),

    "dividend_yield_min":
        ("dividend_yield", "min"),

    "icr_min":
        ("interest_coverage", "min"),

    "market_cap_min":
        ("market_cap", "min"),

    "net_profit_min":
        ("net_profit", "min"),

    "eps_cagr_min":
        ("eps_cagr_5yr", "min"),

    "asset_turnover_min":
        ("asset_turnover", "min"),

    "sales_min":
        ("sales", "min"),
}


# ============================================================
# SPRINT 3 FILTER ENGINE
# ============================================================

def apply_filters(df, filters=None):
    """
    Apply Sprint 3 threshold filters.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "df must be a pandas DataFrame"
        )

    if filters is None:
        return df.copy()

    result = df.copy()

    for name, threshold in filters.items():

        if threshold is None:
            continue

        if name not in FILTER_MAP:
            continue

        column, direction = (
            FILTER_MAP[name]
        )

        if column not in result.columns:
            continue

        # ----------------------------------------
        # Interest Coverage
        # ----------------------------------------

        if column == "interest_coverage":

            raw = (
                result[column]
                .astype(str)
                .str.strip()
                .str.lower()
            )

            values = _numeric(
                result[column]
            )

            debt_free = raw.isin(
                [
                    "debt free",
                    "debt-free",
                    "debtfree",
                ]
            )

            values.loc[
                debt_free
            ] = np.inf

        else:

            values = _numeric(
                result[column]
            )

        threshold = float(
            threshold
        )

        # ----------------------------------------
        # Financial-sector D/E exception
        # ----------------------------------------

        if (
            column == "debt_equity"
            and direction == "max"
            and "broad_sector"
            in result.columns
        ):

            financial = (
                result[
                    "broad_sector"
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    "financial",
                    na=False
                )
            )

            mask = (
                financial
                |
                (values <= threshold)
            )

        elif direction == "min":

            mask = (
                values >= threshold
            )

        else:

            mask = (
                values <= threshold
            )

        result = (
            result.loc[
                mask.fillna(False)
            ]
            .copy()
        )

    return result


# ============================================================
# P10 / P90 NORMALISATION
# ============================================================

def _normalise(
    series,
    inverse=False
):
    """
    Winsorise at P10/P90 and scale to 0-100.
    """

    values = _numeric(
        series
    )

    values = values.replace(
        [np.inf, -np.inf],
        np.nan
    )

    valid = values.dropna()

    if valid.empty:

        return pd.Series(
            0.0,
            index=series.index
        )

    p10 = valid.quantile(
        0.10
    )

    p90 = valid.quantile(
        0.90
    )

    clipped = values.clip(
        lower=p10,
        upper=p90
    )

    minimum = clipped.min()
    maximum = clipped.max()

    if (
        pd.isna(minimum)
        or pd.isna(maximum)
    ):

        score = pd.Series(
            0.0,
            index=series.index
        )

    elif maximum == minimum:

        score = pd.Series(
            50.0,
            index=series.index
        )

    else:

        score = (
            (
                clipped
                - minimum
            )
            /
            (
                maximum
                - minimum
            )
            * 100
        )

    if inverse:
        score = 100 - score

    return score.fillna(0)


# ============================================================
# SPRINT 3 COMPOSITE SCORE
# ============================================================

def add_composite_quality_score(df):
    """
    Add composite_quality_score on a 0-100 scale.
    """

    result = df.copy()

    total = pd.Series(
        0.0,
        index=result.index
    )

    metrics = {
        "roe":
            (0.15, False),

        "roce":
            (0.10, False),

        "net_profit_margin":
            (0.10, False),

        "fcf_cagr_5yr":
            (0.15, False),

        "cfo_pat_ratio":
            (0.10, False),

        "revenue_cagr_5yr":
            (0.10, False),

        "pat_cagr_5yr":
            (0.10, False),

        "debt_equity":
            (0.10, True),

        "interest_coverage":
            (0.05, False),
    }

    for column, (
        weight,
        inverse
    ) in metrics.items():

        if column not in result.columns:
            continue

        values = result[column]

        if column == "interest_coverage":

            text = (
                values
                .astype(str)
                .str.strip()
                .str.lower()
            )

            numeric = _numeric(
                values
            )

            finite = (
                numeric
                .replace(
                    [
                        np.inf,
                        -np.inf
                    ],
                    np.nan
                )
                .dropna()
            )

            replacement = (
                finite.max()
                if not finite.empty
                else 100
            )

            numeric.loc[
                text.isin(
                    [
                        "debt free",
                        "debt-free",
                        "debtfree",
                    ]
                )
            ] = replacement

            values = numeric

        metric_score = _normalise(
            values,
            inverse=inverse
        )

        total += (
            metric_score
            * weight
        )

    # Positive FCF = 5%
    if "fcf" in result.columns:

        positive_fcf = (
            _numeric(
                result["fcf"]
            ) > 0
        ).astype(float)

        total += (
            positive_fcf
            * 100
            * 0.05
        )

    result[
        "composite_quality_score"
    ] = (
        total
        .clip(
            lower=0,
            upper=100
        )
        .round(2)
    )

    return result


# ============================================================
# SPRINT 3 MAIN SCREENER
# ============================================================

def screen_companies(
    df,
    filters=None
):
    """
    Score, filter and sort companies.
    """

    scored = (
        add_composite_quality_score(
            df
        )
    )

    filtered = apply_filters(
        scored,
        filters
    )

    if (
        "composite_quality_score"
        in filtered.columns
    ):

        filtered = (
            filtered
            .sort_values(
                "composite_quality_score",
                ascending=False
            )
            .reset_index(drop=True)
        )

    return filtered


# Compatibility alias
run_screener = screen_companies


if __name__ == "__main__":

    print(
        "NIFTY 100 Financial Intelligence"
    )

    print(
        "Stock Screener Engine loaded successfully."
    )