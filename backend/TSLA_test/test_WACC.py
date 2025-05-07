import yfinance as yf
import numpy as np
import pandas as pd
import datetime
from curl_cffi import requests
import time
import json

# Configure requests with Chrome browser impersonation
def get_yf_ticker(symbol):
    session = requests.Session(
        impersonate="chrome110",
        headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://finance.yahoo.com/",
            "DNT": "1"
        }
    )
    return yf.Ticker(symbol, session=session)

def calculate_wacc(ticker_symbol, market_index="^GSPC"):
    """
    Calculate WACC for a given ticker using only yfinance with no default values
    
    Parameters:
    ticker_symbol (str): The stock ticker symbol
    market_index (str): The market index to use (default: ^GSPC for S&P 500)
    
    Returns:
    dict: WACC and all component calculations, or None if data isn't available
    """
    print(f"Calculating WACC for {ticker_symbol}")
    
    # Get ticker data
    ticker = get_yf_ticker(ticker_symbol)
    
    # Save the ticker.info data
    save_ticker_info(ticker.info, ticker_symbol)
    
    # 1. Calculate Cost of Equity
    
    # Get beta
    beta = ticker.info.get('beta')
    if beta is None:
        print("Beta not available")
        return None
    print(f"Beta: {beta}")
    
    # Get risk-free rate (10-year Treasury yield)
    treasury = get_yf_ticker("^TNX")
    risk_free_rate = treasury.info.get('regularMarketPrice')
    if risk_free_rate is None:
        print("Risk-free rate not available")
        return None
    risk_free_rate = risk_free_rate / 100  # Convert to decimal
    print(f"Risk-free rate: {risk_free_rate:.4f}")
    
    # Calculate market risk premium
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=5*365)  # 5 years of data
    
    market = get_yf_ticker(market_index)
    market_data = market.history(start=start_date, end=end_date)
    
    if market_data.empty:
        print("Market data not available")
        return None
    
    # Calculate monthly returns and annualize
    market_data['Monthly_Return'] = market_data['Close'].pct_change(21)
    market_data = market_data.dropna()
    
    if market_data.empty:
        print("Market return calculation failed")
        return None
    
    expected_market_return = ((1 + market_data['Monthly_Return'].mean()) ** 12) - 1
    market_risk_premium = expected_market_return - risk_free_rate
    print(f"Expected Market Return: {expected_market_return:.4f}")
    print(f"Market risk premium: {market_risk_premium:.4f}")
    
    # Calculate cost of equity using CAPM
    cost_of_equity = risk_free_rate + beta * market_risk_premium
    print(f"Cost of Equity: {cost_of_equity:.4f}")
    
    # 2. Calculate Cost of Debt
    
    # Get financial data - prioritize balance sheet for total debt
    bs = ticker.balance_sheet

    # Get total debt directly from balance sheet
    total_debt = None
    if bs is not None and not bs.empty:
        if 'Total Debt' in bs.index:
            total_debt = bs.loc['Total Debt'].iloc[0]
            print(f"Total Debt from balance sheet: ${total_debt:,.0f}")
        elif 'Long Term Debt' in bs.index and 'Short Term Debt' in bs.index:
            long_term_debt = bs.loc['Long Term Debt'].iloc[0]
            short_term_debt = bs.loc['Short Term Debt'].iloc[0]
            total_debt = long_term_debt + short_term_debt
            print(f"Total Debt (Long + Short) from balance sheet: ${total_debt:,.0f}")

    # If balance sheet doesn't have it, fall back to ticker.info
    if total_debt is None:
        total_debt = ticker.info.get('totalDebt')
        if total_debt is not None:
            print(f"Total Debt from ticker.info: ${total_debt:,.0f}")
        else:
            # Try long-term and short-term debt
            long_term_debt = ticker.info.get('longTermDebt')
            short_term_debt = ticker.info.get('shortTermDebt')
            
            if long_term_debt is not None and short_term_debt is not None:
                total_debt = long_term_debt + short_term_debt
                print(f"Total Debt (Long + Short) from ticker.info: ${total_debt:,.0f}")
        
    if total_debt is None or total_debt == 0:
        print("Total debt data not available")
        return None
    
    print(f"Total Debt: ${total_debt:,.0f}")
    
    # Get interest expense and tax rate
    income_stmt = ticker.financials
    
    # Save financials data to file instead of printing
    save_financial_data(income_stmt, ticker_symbol, "financials")
    
    # Get interest expense
    interest_expense = None
    for col in ['Interest Expense', 'Interest Expense, Net']:
        if col in income_stmt.index:
            interest_expense = abs(income_stmt.loc[col].iloc[0])
            break
            
    if interest_expense is None:
        print("Interest expense data not available")
        return None
        
    print(f"Interest Expense: ${interest_expense:,.0f}")
    
    # Get tax rate
    # First try to get the pre-calculated tax rate directly
    tax_rate_direct = None
    if 'Tax Rate For Calcs' in income_stmt.index:
        tax_rate_direct = income_stmt.loc['Tax Rate For Calcs'].iloc[0]
        print(f"Tax Rate from 'Tax Rate For Calcs': {tax_rate_direct:.4f}")

    # Also calculate tax rate from Tax Provision and Pretax Income for comparison
    tax_rate_calculated = None
    if 'Tax Provision' in income_stmt.index and 'Pretax Income' in income_stmt.index:
        tax_provision = income_stmt.loc['Tax Provision'].iloc[0]
        pretax_income = income_stmt.loc['Pretax Income'].iloc[0]
        
        if pretax_income != 0:
            tax_rate_calculated = tax_provision / pretax_income
            print(f"Calculated Tax Rate (Tax Provision/Pretax Income): {tax_rate_calculated:.4f}")
            
            # Handle negative tax rates (could happen for tax benefits)
            if tax_rate_calculated < 0:
                print(f"Note: Calculated tax rate is negative ({tax_rate_calculated:.4f}), which may indicate tax benefits or credits")

    # Try alternative calculation methods if the first one failed
    if tax_rate_calculated is None:
        tax_cols = ['Income Tax Expense', 'Tax Provision']
        income_cols = ['Income Before Tax', 'Pretax Income', 'EBT']
        
        for tax_col in tax_cols:
            if tax_col in income_stmt.index:
                tax_expense = income_stmt.loc[tax_col].iloc[0]
                
                for income_col in income_cols:
                    if income_col in income_stmt.index:
                        income_before_tax = income_stmt.loc[income_col].iloc[0]
                        
                        if income_before_tax != 0:
                            tax_rate_calculated = tax_expense / income_before_tax
                            print(f"Calculated Tax Rate ({tax_col}/{income_col}): {tax_rate_calculated:.4f}")
                            break
                
                if tax_rate_calculated is not None:
                    break

    # Use the direct rate if available, otherwise use calculated
    if tax_rate_direct is not None:
        tax_rate = tax_rate_direct
        print(f"Using direct tax rate from Yahoo Finance: {tax_rate:.4f}")
    elif tax_rate_calculated is not None:
        # If negative, use absolute value with a warning
        if tax_rate_calculated < 0:
            tax_rate = abs(tax_rate_calculated)
            print(f"Warning: Using absolute value of negative tax rate: {tax_rate:.4f}")
        else:
            tax_rate = tax_rate_calculated
        print(f"Using calculated tax rate: {tax_rate:.4f}")
    else:
        print("Tax rate data not available or invalid")
        return None

    print(f"Final Effective Tax Rate: {tax_rate:.4f}")
    
    # Calculate pre-tax cost of debt
    cost_of_debt_pretax = interest_expense / total_debt
    print(f"Pre-tax Cost of Debt: {cost_of_debt_pretax:.4f}")
    
    # Calculate after-tax cost of debt
    cost_of_debt = cost_of_debt_pretax * (1 - tax_rate)
    print(f"After-tax Cost of Debt: {cost_of_debt:.4f}")
    
    # 3. Calculate Weights
    
    # Get market cap
    market_cap = ticker.info.get('marketCap')
    
    if market_cap is None:
        shares_outstanding = ticker.info.get('sharesOutstanding')
        current_price = ticker.info.get('regularMarketPrice')
        
        if shares_outstanding is not None and current_price is not None:
            market_cap = shares_outstanding * current_price
    
    if market_cap is None or market_cap == 0:
        print("Market cap data not available")
        return None
            
    print(f"Market Cap: ${market_cap:,.0f}")
    
    # Calculate total capital
    total_capital = market_cap + total_debt
    print(f"Total Capital: ${total_capital:,.0f}")
    
    # Calculate weights
    weight_of_equity = market_cap / total_capital
    weight_of_debt = total_debt / total_capital
    print(f"Weight of Equity: {weight_of_equity:.4f}")
    print(f"Weight of Debt: {weight_of_debt:.4f}")
    
    # 4. Calculate WACC
    wacc = (cost_of_equity * weight_of_equity) + (cost_of_debt * weight_of_debt)
    print(f"\nWeighted Average Cost of Capital (WACC): {wacc:.4f} or {wacc*100:.2f}%")
    
    # Calculate alternative cost of equity (using the formula from the question)
    cost_of_operations = cost_of_equity  # Assumption: cost of operations = unlevered cost of equity
    leverage_ratio = total_debt / market_cap
    cost_of_equity_alt = cost_of_operations + leverage_ratio * (cost_of_operations - cost_of_debt)
    print(f"Cost of Equity (alternative formula): {cost_of_equity_alt:.4f} or {cost_of_equity_alt*100:.2f}%")
    
    # Print out balance sheet data
    bs = ticker.balance_sheet
    save_financial_data(bs, ticker_symbol, "balance_sheet")
    
    # Return all calculations
    return {
        'beta': beta,
        'risk_free_rate': risk_free_rate,
        'market_risk_premium': market_risk_premium,
        'cost_of_equity': cost_of_equity,
        'total_debt': total_debt,
        'interest_expense': interest_expense,
        'tax_rate': tax_rate,
        'cost_of_debt_pretax': cost_of_debt_pretax,
        'cost_of_debt': cost_of_debt,
        'market_cap': market_cap,
        'weight_of_equity': weight_of_equity,
        'weight_of_debt': weight_of_debt,
        'wacc': wacc,
        'cost_of_equity_alt': cost_of_equity_alt
    }

def save_financial_data(dataframe, ticker_symbol, data_type):
    """
    Save a financial dataframe to a CSV file
    
    Parameters:
    dataframe (DataFrame): The financial data to save
    ticker_symbol (str): The stock ticker symbol
    data_type (str): Type of data (e.g., 'financials', 'balance_sheet')
    """
    if dataframe is not None and not dataframe.empty:
        filename = f"{ticker_symbol}_{data_type}.csv"
        dataframe.to_csv(filename)
        print(f"Saved {data_type} data to {filename}")
        
        # Create row names file for reference
        with open(f"{ticker_symbol}_{data_type}_rows.txt", "w") as f:
            f.write(f"--- AVAILABLE ROW NAMES IN {data_type.upper()} ---\n")
            for idx in dataframe.index:
                f.write(f"- {idx}\n")
        print(f"Saved row names to {ticker_symbol}_{data_type}_rows.txt")
    else:
        print(f"No {data_type} data available to save")

def save_ticker_info(ticker_data, ticker_symbol):
    """
    Save ticker info data to a JSON file
    
    Parameters:
    ticker_data (dict): The ticker info data
    ticker_symbol (str): The stock ticker symbol
    """
    if ticker_data is not None:
        # Convert any non-serializable objects to strings
        serializable_data = {}
        for key, value in ticker_data.items():
            if isinstance(value, (str, int, float, bool, type(None))):
                serializable_data[key] = value
            else:
                # Convert non-JSON serializable objects to strings
                serializable_data[key] = str(value)
                
        # Save to JSON file
        filename = f"{ticker_symbol}_info.json"
        with open(filename, 'w') as f:
            json.dump(serializable_data, f, indent=4)
        print(f"Saved ticker info to {filename}")
        
        # Also save a plain text version for easy viewing
        with open(f"{ticker_symbol}_info.txt", 'w') as f:
            for key, value in sorted(serializable_data.items()):
                f.write(f"{key}: {value}\n")
        print(f"Saved ticker info to {ticker_symbol}_info.txt")
    else:
        print("No ticker info data available to save")

# Usage example
if __name__ == "__main__":
    ticker = "TSLA"  # Tesla
    
    # For US companies, use S&P 500 as the market index
    result = calculate_wacc(ticker, market_index="^GSPC")
    
    if result is None:
        print("Couldn't calculate WACC due to missing data")
    else:
        print("\nSummary:")
        print(f"WACC: {result['wacc']*100:.2f}%")
        print(f"Cost of Equity: {result['cost_of_equity']*100:.2f}%")
        print(f"Cost of Debt (after tax): {result['cost_of_debt']*100:.2f}%")