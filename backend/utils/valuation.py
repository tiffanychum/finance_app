"""
Utility functions for calculating valuation metrics
"""

def calculate_residual_earnings(earnings, book_value, cost_of_equity):
    """
    Calculate Residual Earnings (RE)
    RE = Comprehensive Earnings - (CoE - 1) * Beginning Book Value
    """
    return earnings - (cost_of_equity - 1) * book_value

def calculate_roce(net_income, common_equity):
    """
    Calculate Return on Common Equity (ROCE)
    ROCE = Net Income / Common Shareholders' Equity
    """
    if common_equity == 0:
        return 0
    return net_income / common_equity

def decompose_roce(operating_income, net_operating_assets, net_financial_expense, 
                  net_financial_obligations, common_equity):
    """
    Decompose ROCE into RNOA + FLEV * SPREAD
    
    RNOA = Operating Income / Net Operating Assets
    FLEV = Net Financial Obligations / Common Equity
    SPREAD = RNOA - NBC
    NBC = Net Financial Expense / Net Financial Obligations
    """
    if net_operating_assets == 0 or common_equity == 0 or net_financial_obligations == 0:
        return {
            "roce": 0,
            "rnoa": 0,
            "flev": 0,
            "spread": 0,
            "nbc": 0
        }
    
    rnoa = operating_income / net_operating_assets
    flev = net_financial_obligations / common_equity
    nbc = net_financial_expense / net_financial_obligations
    spread = rnoa - nbc
    roce = rnoa + (flev * spread)
    
    return {
        "roce": roce,
        "rnoa": rnoa,
        "flev": flev,
        "spread": spread,
        "nbc": nbc
    }

def decompose_rnoa(operating_income, sales, net_operating_assets):
    """
    Decompose RNOA into PM * ATO
    
    PM (Profit Margin) = Operating Income / Sales
    ATO (Asset Turnover) = Sales / Net Operating Assets
    """
    if sales == 0 or net_operating_assets == 0:
        return {
            "rnoa": 0,
            "pm": 0,
            "ato": 0
        }
    
    pm = operating_income / sales
    ato = sales / net_operating_assets
    rnoa = pm * ato
    
    return {
        "rnoa": rnoa,
        "pm": pm,
        "ato": ato
    }

def calculate_discounted_re_valuation(current_book_value, forecast_re, continuing_value, cost_of_equity):
    """
    Calculate firm value using the Residual Earnings model
    V0 = Current Book Value + PV of forecast RE + PV of continuing value
    """
    pv_forecast_re = 0
    for t, re in enumerate(forecast_re, 1):
        pv_forecast_re += re / ((1 + cost_of_equity) ** t)
    
    pv_continuing_value = continuing_value / ((1 + cost_of_equity) ** len(forecast_re))
    
    return current_book_value + pv_forecast_re + pv_continuing_value

def calculate_aeg_valuation(forward_earnings, forecast_aeg, cost_of_equity):
    """
    Calculate firm value using the Abnormal Earnings Growth model
    V0 = Forward Earnings / (CoE - 1) + PV of forecast AEG
    """
    capitalized_forward_earnings = forward_earnings / (cost_of_equity - 1)
    
    pv_forecast_aeg = 0
    for t, aeg in enumerate(forecast_aeg, 1):
        pv_forecast_aeg += aeg / ((1 + cost_of_equity) ** t)
    
    return capitalized_forward_earnings + pv_forecast_aeg 