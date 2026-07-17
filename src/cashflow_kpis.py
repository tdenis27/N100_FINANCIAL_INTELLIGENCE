"""
Cash Flow KPI Functions
"""


def free_cash_flow(operating_cash_flow, investing_cash_flow):
    """
    Free Cash Flow = Operating Cash Flow + Investing Cash Flow
    """
    if operating_cash_flow is None or investing_cash_flow is None:
        return None
    return round(operating_cash_flow + investing_cash_flow, 2)


def operating_cash_flow_ratio(operating_cash_flow, current_liabilities):
    """
    Operating Cash Flow Ratio
    """
    if current_liabilities is None or current_liabilities == 0:
        return None
    return round(operating_cash_flow / current_liabilities, 2)


def cfo_quality_score(operating_cash_flow, pat):
    """
    CFO Quality Score
    """
    if pat is None or pat == 0:
        return None
    return round(operating_cash_flow / pat, 2)


def capex_intensity(investing_cash_flow, sales):
    """
    CapEx Intensity (%)
    """
    if sales is None or sales == 0:
        return None
    return round((abs(investing_cash_flow) / sales) * 100, 2)


def fcf_conversion_ratio(free_cash_flow_value, operating_profit):
    """
    FCF Conversion Ratio
    """
    if operating_profit is None or operating_profit == 0:
        return None
    return round((free_cash_flow_value / operating_profit) * 100, 2)


def capital_allocation_pattern(cfo, cfi, cff):
    """
    Capital Allocation Pattern
    """

    if cfo > 0 and cfi < 0 and cff < 0:
        return "Reinvestor"

    elif cfo > 0 and cfi < 0 and cff > 0:
        return "Debt Funded Growth"

    elif cfo > 0 and cfi > 0 and cff < 0:
        return "Shareholder Returns"

    elif cfo > 0 and cfi > 0 and cff > 0:
        return "Cash Accumulator"

    else:
        return "Mixed"