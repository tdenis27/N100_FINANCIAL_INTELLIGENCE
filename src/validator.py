import os
import pandas as pd


OUTPUT_DIR = "output"
VALIDATION_FILE = os.path.join(
    OUTPUT_DIR,
    "validation_failures.csv"
)


def create_result(rule, table, severity, failures, message):
    return {
        "rule": rule,
        "table": table,
        "severity": severity,
        "failures": failures,
        "message": message
    }


def dq_01_pk_uniqueness(df, table):
    """
    DQ-01: Primary key must be unique.
    """

    if "id" not in df.columns:
        return create_result(
            "DQ-01",
            table,
            "CRITICAL",
            1,
            "id column not found"
        )

    failures = int(df["id"].duplicated().sum())

    return create_result(
        "DQ-01",
        table,
        "CRITICAL",
        failures,
        "Primary key uniqueness check"
    )


def dq_02_company_year_unique(df, table):
    """
    DQ-02: company_id + year must be unique.
    """

    required = ["company_id", "year"]

    if not all(col in df.columns for col in required):
        return create_result(
            "DQ-02",
            table,
            "CRITICAL",
            0,
            "Rule not applicable"
        )

    failures = int(
        df.duplicated(
            subset=["company_id", "year"]
        ).sum()
    )

    return create_result(
        "DQ-02",
        table,
        "CRITICAL",
        failures,
        "company_id and year uniqueness"
    )


def dq_03_fk_integrity(df, table, company_ids):
    """
    DQ-03: company_id must exist in companies.
    """

    if "company_id" not in df.columns:
        return create_result(
            "DQ-03",
            table,
            "CRITICAL",
            0,
            "Rule not applicable"
        )

    failures = int(
        (~df["company_id"].isin(company_ids)).sum()
    )

    return create_result(
        "DQ-03",
        table,
        "CRITICAL",
        failures,
        "Foreign key integrity check"
    )


def dq_04_balance_check(df, table):
    """
    DQ-04: Balance sheet balance check.
    """

    required = [
        "total_assets",
        "total_liabilities"
    ]

    if not all(col in df.columns for col in required):
        return create_result(
            "DQ-04",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    assets = pd.to_numeric(
        df["total_assets"],
        errors="coerce"
    )

    liabilities = pd.to_numeric(
        df["total_liabilities"],
        errors="coerce"
    )

    difference = (
        assets - liabilities
    ).abs()

    denominator = assets.abs().replace(0, pd.NA)

    percentage = (
        difference / denominator
    ) * 100

    failures = int((percentage >= 1).sum())

    return create_result(
        "DQ-04",
        table,
        "WARNING",
        failures,
        "Balance difference must be below 1 percent"
    )


def dq_05_opm_cross_check(df, table):
    """
    DQ-05: Operating profit margin check.
    """

    required = [
        "operating_profit",
        "sales",
        "opm_percentage"
    ]

    if not all(col in df.columns for col in required):
        return create_result(
            "DQ-05",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    operating_profit = pd.to_numeric(
        df["operating_profit"],
        errors="coerce"
    )

    sales = pd.to_numeric(
        df["sales"],
        errors="coerce"
    )

    reported_opm = pd.to_numeric(
        df["opm_percentage"],
        errors="coerce"
    )

    calculated_opm = (
        operating_profit / sales.replace(0, pd.NA)
    ) * 100

    difference = (
        calculated_opm - reported_opm
    ).abs()

    failures = int((difference > 1).sum())

    return create_result(
        "DQ-05",
        table,
        "WARNING",
        failures,
        "OPM cross-check"
    )


def dq_06_positive_sales(df, table):
    """
    DQ-06: Sales must be positive.
    """

    if "sales" not in df.columns:
        return create_result(
            "DQ-06",
            table,
            "CRITICAL",
            0,
            "Rule not applicable"
        )

    sales = pd.to_numeric(
        df["sales"],
        errors="coerce"
    )

    failures = int((sales <= 0).sum())

    return create_result(
        "DQ-06",
        table,
        "CRITICAL",
        failures,
        "Sales must be positive"
    )


def dq_07_null_company_id(df, table):
    """
    DQ-07: company_id cannot be null.
    """

    if "company_id" not in df.columns:
        return create_result(
            "DQ-07",
            table,
            "CRITICAL",
            0,
            "Rule not applicable"
        )

    failures = int(
        df["company_id"].isna().sum()
    )

    return create_result(
        "DQ-07",
        table,
        "CRITICAL",
        failures,
        "company_id null check"
    )


def dq_08_null_year(df, table):
    """
    DQ-08: year cannot be null.
    """

    if "year" not in df.columns:
        return create_result(
            "DQ-08",
            table,
            "CRITICAL",
            0,
            "Rule not applicable"
        )

    failures = int(
        df["year"].isna().sum()
    )

    return create_result(
        "DQ-08",
        table,
        "CRITICAL",
        failures,
        "year null check"
    )


def dq_09_year_range(df, table):
    """
    DQ-09: Validate year range.
    """

    if "year" not in df.columns:
        return create_result(
            "DQ-09",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    years = pd.to_numeric(
        df["year"],
        errors="coerce"
    )

    failures = int(
        ((years < 1900) | (years > 2100)).sum()
    )

    return create_result(
        "DQ-09",
        table,
        "WARNING",
        failures,
        "Year must be between 1900 and 2100"
    )


def dq_10_duplicate_rows(df, table):
    """
    DQ-10: Full duplicate row check.
    """

    failures = int(
        df.duplicated().sum()
    )

    return create_result(
        "DQ-10",
        table,
        "WARNING",
        failures,
        "Duplicate row check"
    )


def dq_11_empty_table(df, table):
    """
    DQ-11: Table cannot be empty.
    """

    failures = 1 if df.empty else 0

    return create_result(
        "DQ-11",
        table,
        "CRITICAL",
        failures,
        "Empty table check"
    )


def dq_12_empty_company_name(df, table):
    """
    DQ-12: company_name cannot be empty.
    """

    if "company_name" not in df.columns:
        return create_result(
            "DQ-12",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    values = df["company_name"].fillna("").astype(str)

    failures = int(
        values.str.strip().eq("").sum()
    )

    return create_result(
        "DQ-12",
        table,
        "WARNING",
        failures,
        "Company name empty check"
    )


def dq_13_negative_face_value(df, table):
    """
    DQ-13: face_value cannot be negative.
    """

    if "face_value" not in df.columns:
        return create_result(
            "DQ-13",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    values = pd.to_numeric(
        df["face_value"],
        errors="coerce"
    )

    failures = int((values < 0).sum())

    return create_result(
        "DQ-13",
        table,
        "WARNING",
        failures,
        "Face value cannot be negative"
    )


def dq_14_url_validation(df, table):
    """
    DQ-14: website must be a valid URL.
    """

    if "website" not in df.columns:
        return create_result(
            "DQ-14",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    urls = df["website"].fillna("").astype(str)

    valid = (
        urls.str.startswith("http://")
        | urls.str.startswith("https://")
        | urls.eq("")
    )

    failures = int((~valid).sum())

    return create_result(
        "DQ-14",
        table,
        "WARNING",
        failures,
        "Website URL validation"
    )


def dq_15_eps_sign_check(df, table):
    """
    DQ-15: EPS sign validation.
    """

    required = [
        "eps",
        "net_profit"
    ]

    if not all(col in df.columns for col in required):
        return create_result(
            "DQ-15",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    eps = pd.to_numeric(
        df["eps"],
        errors="coerce"
    )

    profit = pd.to_numeric(
        df["net_profit"],
        errors="coerce"
    )

    failures = int(
        (
            ((profit > 0) & (eps < 0))
            | ((profit < 0) & (eps > 0))
        ).sum()
    )

    return create_result(
        "DQ-15",
        table,
        "WARNING",
        failures,
        "EPS sign cross-check"
    )


def dq_16_bse_balance_coverage(df, table):
    """
    DQ-16: BSE profile coverage check.
    """

    if "bse_profile" not in df.columns:
        return create_result(
            "DQ-16",
            table,
            "WARNING",
            0,
            "Rule not applicable"
        )

    values = df["bse_profile"].fillna("").astype(str)

    failures = int(
        values.str.strip().eq("").sum()
    )

    return create_result(
        "DQ-16",
        table,
        "WARNING",
        failures,
        "BSE profile coverage check"
    )


def validate_all(data):
    """
    Run all 16 DQ rules.
    """

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []

    companies = data.get("companies.xlsx")

    if companies is None:
        raise ValueError("companies.xlsx not found")

    company_ids = set(
        companies["id"].dropna().astype(str)
    )

    for table, df in data.items():

        results.append(
            dq_01_pk_uniqueness(df, table)
        )

        results.append(
            dq_02_company_year_unique(df, table)
        )

        results.append(
            dq_03_fk_integrity(
                df,
                table,
                company_ids
            )
        )

        results.append(
            dq_04_balance_check(df, table)
        )

        results.append(
            dq_05_opm_cross_check(df, table)
        )

        results.append(
            dq_06_positive_sales(df, table)
        )

        results.append(
            dq_07_null_company_id(df, table)
        )

        results.append(
            dq_08_null_year(df, table)
        )

        results.append(
            dq_09_year_range(df, table)
        )

        results.append(
            dq_10_duplicate_rows(df, table)
        )

        results.append(
            dq_11_empty_table(df, table)
        )

        results.append(
            dq_12_empty_company_name(df, table)
        )

        results.append(
            dq_13_negative_face_value(df, table)
        )

        results.append(
            dq_14_url_validation(df, table)
        )

        results.append(
            dq_15_eps_sign_check(df, table)
        )

        results.append(
            dq_16_bse_balance_coverage(df, table)
        )

    result_df = pd.DataFrame(results)

    failures_df = result_df[
        result_df["failures"] > 0
    ]

    failures_df.to_csv(
        VALIDATION_FILE,
        index=False
    )

    return result_df