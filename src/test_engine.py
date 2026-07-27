"""
NIFTY 100 FINANCIAL INTELLIGENCE
DAY 7 - STOCK SCREENER ENGINE VERIFICATION
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(
    0, str(Path(__file__).resolve().parent / "screener")
)

from engine import (  # type: ignore[import-not-found]
    apply_criteria,
    check_debt_to_asset,
    check_rating,
    check_roce,
    check_roe,
    rank_screened_companies,
)


def _sample_data():
    return pd.DataFrame(
        {
            "company_id": [1, 2, 3, 4],
            "company_name": ["Alpha", "Beta", "Gamma", "Delta"],
            "roe_percentage": [20, 10, 18, None],
            "roce_percentage": [22, 12, 16, 25],
            "debt_to_asset_ratio": [0.2, 0.6, 0.4, 0.1],
            "revenue_cagr_percentage": [15, 8, 12, 20],
            "pat_cagr_percentage": [15, 5, 11, 18],
            "net_profit_margin_percentage": [10, 3, 8, 12],
            "financial_health_score": [80, 40, 60, 70],
            "financial_rating": [
                "EXCELLENT",
                "AVERAGE",
                "GOOD",
                "STRONG",
            ],
        }
    )


CRITERIA = {
    "min_roe_percentage": 15,
    "min_roce_percentage": 15,
    "max_debt_to_asset_ratio": 0.5,
    "min_revenue_cagr_percentage": 10,
    "min_pat_cagr_percentage": 10,
    "min_net_profit_margin_percentage": 5,
    "min_financial_health_score": 50,
    "allowed_ratings": None,
}


def test_check_roe_filters_below_threshold():
    data = _sample_data()

    mask = check_roe(data, CRITERIA)

    assert mask.tolist() == [True, False, True, False]


def test_check_roe_treats_missing_value_as_fail():
    data = _sample_data()

    mask = check_roe(data, CRITERIA).fillna(False)

    assert mask.iloc[3] == False  # noqa: E712 (Delta has ROE = None)


def test_check_roce_filters_below_threshold():
    data = _sample_data()

    mask = check_roce(data, CRITERIA)

    assert mask.tolist() == [True, False, True, True]


def test_check_debt_to_asset_filters_above_threshold():
    data = _sample_data()

    mask = check_debt_to_asset(data, CRITERIA)

    assert mask.tolist() == [True, False, True, True]


def test_check_rating_disabled_passes_everyone():
    data = _sample_data()

    mask = check_rating(data, CRITERIA)

    assert mask.all()


def test_check_rating_filters_to_allowed_list():
    data = _sample_data()

    criteria = dict(CRITERIA)
    criteria["allowed_ratings"] = ["EXCELLENT", "STRONG"]

    mask = check_rating(data, criteria)

    assert mask.tolist() == [True, False, False, True]


def test_apply_criteria_combines_all_checks():
    data = _sample_data()

    screened, pass_counts = apply_criteria(data, CRITERIA)

    # Alpha and Gamma clear every threshold; Beta fails on multiple
    # metrics and Delta fails on missing ROE.
    assert sorted(screened["company_name"].tolist()) == [
        "Alpha",
        "Gamma",
    ]
    assert pass_counts["roe"] == 2
    assert pass_counts["debt_to_asset"] == 3


def test_apply_criteria_with_none_criteria_uses_defaults():
    data = _sample_data()

    screened, pass_counts = apply_criteria(data, criteria=None)

    # Should not raise, and should return a dataframe + dict
    assert isinstance(screened, pd.DataFrame)
    assert isinstance(pass_counts, dict)


def test_rank_screened_companies_orders_by_score_desc():
    data = _sample_data()

    ranked = rank_screened_companies(data)

    assert ranked["company_name"].tolist() == [
        "Alpha",
        "Delta",
        "Gamma",
        "Beta",
    ]
    assert ranked["screen_rank"].tolist() == [1, 2, 3, 4]


def test_rank_screened_companies_handles_empty_input():
    data = _sample_data().iloc[0:0]

    ranked = rank_screened_companies(data)

    assert len(ranked) == 0
    assert "screen_rank" in ranked.columns


TESTS = [
    test_check_roe_filters_below_threshold,
    test_check_roe_treats_missing_value_as_fail,
    test_check_roce_filters_below_threshold,
    test_check_debt_to_asset_filters_above_threshold,
    test_check_rating_disabled_passes_everyone,
    test_check_rating_filters_to_allowed_list,
    test_apply_criteria_combines_all_checks,
    test_apply_criteria_with_none_criteria_uses_defaults,
    test_rank_screened_companies_orders_by_score_desc,
    test_rank_screened_companies_handles_empty_input,
]


def main():
    passed = 0
    failed = 0

    for test_function in TESTS:
        name = test_function.__name__

        try:
            test_function()
            print(f"[PASS] {name}")
            passed += 1
        except AssertionError as error:
            print(f"[FAIL] {name}: {error}")
            failed += 1
        except Exception as error:  # noqa: BLE001
            print(f"[ERROR] {name}: {error}")
            failed += 1

    print("=" * 70)

    if failed == 0:
        print("ALL ENGINE TESTS PASSED")
    else:
        print(f"ENGINE TESTS FAILED: {failed} of {len(TESTS)}")

    print("=" * 70)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)