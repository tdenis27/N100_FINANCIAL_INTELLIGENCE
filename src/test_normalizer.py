from loader import load_all_excel_files
from normalizer import normalize_column_names, normalize_text

data = load_all_excel_files()

companies = data["companies.xlsx"]

companies = normalize_column_names(companies)
companies = normalize_text(companies)

print("\nFirst Five Rows\n")

print(companies.head())

print("\nColumn Names\n")

print(companies.columns)