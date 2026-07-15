import os
import pandas as pd

RAW_DATA_PATH = "data/raw"

def load_excel(file_name):
    """
    Load a single Excel file.
    """
    file_path = os.path.join(RAW_DATA_PATH, file_name)

    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    # Skip the title row and use the second row as column names
    df = pd.read_excel(file_path, header=1)

    return df


def load_all_excel_files():
    """
    Load all Excel files from raw folder and subfolders.
    """
    dataframes = {}

    for root, dirs, files in os.walk(RAW_DATA_PATH):
        for file in files:
            if file.endswith(".xlsx"):

                file_path = os.path.join(root, file)

                # Skip first title row
                df = pd.read_excel(file_path, header=1)

                dataframes[file] = df

                print(f"{file:<25} {len(df)} rows")

    return dataframes


if __name__ == "__main__":

    all_data = load_all_excel_files()

    print("\n--------------------------------------------")
    print(f"Total Excel Files Loaded : {len(all_data)}")

    print("\nChecking companies.xlsx\n")

    companies = all_data["companies.xlsx"]

    print(companies.head())

    print("\nColumns\n")

    print(companies.columns)