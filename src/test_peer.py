from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_FILE = (
    BASE_DIR
    / "output"
    / "peer_comparison.xlsx"
)


def test_peer_file_exists():
    assert OUTPUT_FILE.exists(), (
        f"Missing file: {OUTPUT_FILE}"
    )


def test_peer_file_not_empty():
    df = pd.read_excel(OUTPUT_FILE)

    assert len(df) > 0
    assert len(df.columns) > 0


def test_company_name_column():
    df = pd.read_excel(OUTPUT_FILE)

    assert "company_name" in df.columns


def test_financial_score_column():
    df = pd.read_excel(OUTPUT_FILE)

    assert "financial_health_score" in df.columns


def test_rank_columns_exist():
    df = pd.read_excel(OUTPUT_FILE)

    rank_columns = [
        column
        for column in df.columns
        if column.endswith("_rank")
    ]

    assert len(rank_columns) > 0


if __name__ == "__main__":
    test_peer_file_exists()
    test_peer_file_not_empty()
    test_company_name_column()
    test_financial_score_column()
    test_rank_columns_exist()

    print("=" * 60)
    print("ALL PEER TESTS PASSED")
    print("=" * 60)