"""
Compound Annual Growth Rate (CAGR) Calculations
"""


def calculate_cagr(start_value, end_value, years):
    """
    Calculate Compound Annual Growth Rate (CAGR)

    Formula:
        CAGR = ((Ending Value / Beginning Value) ** (1 / Years) - 1) * 100

    Returns:
        float : CAGR percentage
        None  : Invalid input
    """

    if start_value is None or end_value is None:
        return None

    if years is None or years <= 0:
        return None

    if start_value <= 0:
        return None

    return round((((end_value / start_value) ** (1 / years)) - 1) * 100, 2)


def revenue_cagr(start_revenue, end_revenue, years):
    """Revenue CAGR"""
    return calculate_cagr(start_revenue, end_revenue, years)


def pat_cagr(start_pat, end_pat, years):
    """PAT CAGR"""
    return calculate_cagr(start_pat, end_pat, years)


def eps_cagr(start_eps, end_eps, years):
    """EPS CAGR"""
    return calculate_cagr(start_eps, end_eps, years)