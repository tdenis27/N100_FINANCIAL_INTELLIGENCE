"""
Financial Ratio Calculations
"""

def net_profit_margin(net_profit, sales):
    """
    Calculate Net Profit Margin (%)

    Formula:
        Net Profit Margin = (Net Profit / Sales) * 100

    Returns:
        float: Net Profit Margin
        None: if sales is 0 or None
    """

    if sales is None or sales == 0:
        return None

    return round((net_profit / sales) * 100, 2)

def operating_profit_margin(operating_profit, sales):
    """
    Calculate Operating Profit Margin (%)
    """

    if sales is None or sales == 0:
        return None

    return round((operating_profit / sales) * 100, 2)

def return_on_equity(net_profit, equity):
    """
    Calculate Return on Equity (ROE)

    Formula:
        ROE = (Net Profit / Equity) * 100
    """

    if equity is None or equity <= 0:
        return None

    return round((net_profit / equity) * 100, 2)

def return_on_capital_employed(ebit, equity, borrowings):
    """
    Calculate Return on Capital Employed (ROCE)

    Formula:
        ROCE = (EBIT / (Equity + Borrowings)) * 100
    """

    capital_employed = equity + borrowings

    if capital_employed <= 0:
        return None

    return round((ebit / capital_employed) * 100, 2)

def return_on_assets(net_profit, total_assets):
    """
    Calculate Return on Assets (ROA)

    Formula:
        ROA = (Net Profit / Total Assets) * 100
    """

    if total_assets is None or total_assets <= 0:
        return None

    return round((net_profit / total_assets) * 100, 2)

def asset_turnover_ratio(sales, total_assets):
    """
    Calculate Asset Turnover Ratio

    Formula:
        Asset Turnover = Sales / Total Assets
    """

    if total_assets is None or total_assets <= 0:
        return None

    return round(sales / total_assets, 2)

def debt_to_equity(borrowings, equity):
    """
    Calculate Debt-to-Equity Ratio

    Formula:
        Debt to Equity = Borrowings / Equity
    """

    if equity is None or equity <= 0:
        return None

    return round(borrowings / equity, 2)

def interest_coverage(operating_profit, interest):
    """
    Calculate Interest Coverage Ratio

    Formula:
        Interest Coverage = Operating Profit / Interest
    """

    if interest is None or interest <= 0:
        return None

    return round(operating_profit / interest, 2)
def net_debt(borrowings, investments):
    """
    Calculate Net Debt

    Formula:
        Net Debt = Borrowings - Investments
    """

    if borrowings is None:
        return None

    if investments is None:
        investments = 0

    return round(borrowings - investments, 2)

def operating_cash_flow_ratio(operating_cash_flow, current_liabilities):
    """
    Calculate Operating Cash Flow Ratio

    Formula:
        Operating Cash Flow Ratio = Operating Cash Flow / Current Liabilities
    """

    if current_liabilities is None or current_liabilities <= 0:
        return None

    return round(operating_cash_flow / current_liabilities, 2)

def free_cash_flow_ratio(free_cash_flow, operating_cash_flow):
    """
    Calculate Free Cash Flow Ratio

    Formula:
        Free Cash Flow Ratio = Free Cash Flow / Operating Cash Flow
    """

    if operating_cash_flow is None or operating_cash_flow == 0:
        return None

    return round(free_cash_flow / operating_cash_flow, 2)

def earnings_per_share(net_profit, shares_outstanding):
    """
    Calculate Earnings Per Share (EPS)

    Formula:
        EPS = Net Profit / Shares Outstanding
    """

    if shares_outstanding is None or shares_outstanding <= 0:
        return None

    return round(net_profit / shares_outstanding, 2)

def dividend_payout_ratio(dividend_per_share, earnings_per_share):
    """
    Calculate Dividend Payout Ratio

    Formula:
        Dividend Payout Ratio = (Dividend Per Share / Earnings Per Share) * 100
    """

    if earnings_per_share is None or earnings_per_share <= 0:
        return None

    return round((dividend_per_share / earnings_per_share) * 100, 2)

def book_value_per_share(equity, shares_outstanding):
    """
    Calculate Book Value Per Share (BVPS)

    Formula:
        BVPS = Equity / Shares Outstanding
    """

    if shares_outstanding is None or shares_outstanding <= 0:
        return None

    return round(equity / shares_outstanding, 2)