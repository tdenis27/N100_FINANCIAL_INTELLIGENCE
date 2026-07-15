from pathlib import Path

import pandas as pd

from loader import load_all_excel_files
from normalizer import normalize_column_names, normalize_text


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def remove_empty_rows_and_columns(df):
    """Remove completely empty rows and columns."""
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")

    return df


def remove_unnamed_columns(df):
    """Remove Excel-generated unnamed columns."""
    columns_to_remove = [
        column
        for column in df.columns
        if str(column).lower().startswith("unnamed")
    ]

    return df.drop(columns=columns_to_remove, errors="ignore")


def remove_duplicate_rows(df):
    """Remove exact duplicate rows."""
    return df.drop_duplicates()


def clean_text_columns(df):
    """Normalize text values."""
    return normalize_text(df)


def clean_dataframe(df):
    """Run the standard cleaning pipeline."""
    df = df.copy()

    df = normalize_column_names(df)
    df = remove_empty_rows_and_columns(df)
    df = remove_unnamed_columns(df)
    df = clean_text_columns(df)
    df = remove_duplicate_rows(df)

    df = df.reset_index(drop=True)

    return df


def save_processed_file(df, file_name):
    """Save cleaned dataframe as CSV."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_name = Path(file_name).stem + ".csv"
    output_path = PROCESSED_DIR / output_name

    df.to_csv(
        output_path,
        index=False,
        encoding="utf-8"
    )

    return output_path


def clean_all_files():
    """Load, clean, and save all Excel datasets."""
    data = load_all_excel_files()

    results = []

    print("\n" + "=" * 70)
    print("DAY 4 DATA CLEANING")
    print("=" * 70)

    for file_name, df in data.items():
        original_rows = len(df)
        original_columns = len(df.columns)

        cleaned_df = clean_dataframe(df)

        cleaned_rows = len(cleaned_df)
        cleaned_columns = len(cleaned_df.columns)

        output_path = save_processed_file(
            cleaned_df,
            file_name
        )

        results.append(
            {
                "file": file_name,
                "original_rows": original_rows,
                "cleaned_rows": cleaned_rows,
                "original_columns": original_columns,
                "cleaned_columns": cleaned_columns,
                "removed_rows": original_rows - cleaned_rows,
                "output": str(output_path),
            }
        )

        print(f"\n{file_name}")
        print(f"Original Rows   : {original_rows}")
        print(f"Cleaned Rows    : {cleaned_rows}")
        print(f"Removed Rows    : {original_rows - cleaned_rows}")
        print(f"Original Columns: {original_columns}")
        print(f"Cleaned Columns : {cleaned_columns}")
        print(f"Saved           : {output_path.name}")

    result_df = pd.DataFrame(results)

    summary_path = PROCESSED_DIR / "cleaning_summary.csv"

    result_df.to_csv(
        summary_path,
        index=False,
        encoding="utf-8"
    )

    print("\n" + "=" * 70)
    print(f"TOTAL FILES CLEANED: {len(results)}")
    print(f"CLEANING SUMMARY   : {summary_path}")
    print("DAY 4 CLEANING COMPLETED")
    print("=" * 70)

    return result_df


if __name__ == "__main__":
    clean_all_files()