from loader import load_all_excel_files
from normalizer import normalize_column_names, normalize_text
from validator import validate_all


def prepare_data(data):
    normalized_data = {}

    for file_name, dataframe in data.items():
        print(f"Normalizing: {file_name}")

        dataframe = normalize_column_names(dataframe)
        dataframe = normalize_text(dataframe)

        normalized_data[file_name] = dataframe

    return normalized_data


def main():
    print("=" * 70)
    print("N100 FINANCIAL INTELLIGENCE")
    print("DAY 3 - DATA QUALITY VALIDATION")
    print("=" * 70)

    print("\nSTEP 1: LOADING EXCEL FILES\n")

    data = load_all_excel_files()

    print(f"\nExcel Files Loaded: {len(data)}")

    print("\n" + "=" * 70)
    print("STEP 2: NORMALIZING DATA")
    print("=" * 70)

    normalized_data = prepare_data(data)

    print("\nNormalization Completed")

    print("\n" + "=" * 70)
    print("STEP 3: RUNNING DATA QUALITY CHECKS")
    print("=" * 70)

    validation_results = validate_all(normalized_data)

    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    if validation_results.empty:
        print("No validation results returned.")
        return

    print(validation_results.to_string(index=False))

    total_checks = len(validation_results)

    if "failures" in validation_results.columns:
        failed_checks = (
            validation_results["failures"] > 0
        ).sum()

        passed_checks = total_checks - failed_checks

        total_failures = validation_results["failures"].sum()

        print("\n" + "-" * 70)
        print(f"Total Checks   : {total_checks}")
        print(f"Passed Checks  : {passed_checks}")
        print(f"Failed Checks  : {failed_checks}")
        print(f"Total Failures : {total_failures}")
        print("-" * 70)

        if failed_checks == 0:
            print("\nDATA QUALITY STATUS: PASSED")
        else:
            print("\nDATA QUALITY STATUS: REVIEW REQUIRED")

    else:
        print("\nERROR: 'failures' column not found.")

    print("\n" + "=" * 70)
    print("DAY 3 VALIDATION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()