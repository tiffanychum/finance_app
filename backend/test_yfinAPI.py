import yfinance as yf
import numpy as np
import pandas as pd
from yahooquery import Ticker
import datetime
from curl_cffi import requests
import time

# Configure requests with Chrome browser impersonation to avoid rate limiting
def get_yf_ticker(symbol):
    try:
        # Try with curl_cffi first
        session = requests.Session(
            impersonate="chrome110",  # Use specific Chrome version
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://finance.yahoo.com/",
                "DNT": "1"
            }
        )
        return yf.Ticker(symbol, session=session)
    except Exception as e:
        print(f"Error with curl_cffi: {e}")
        # Fall back to standard requests if curl_cffi fails
        import requests as std_requests
        std_session = std_requests.Session()
        std_session.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        return yf.Ticker(symbol, session=std_session)

# Function to get financial data with fallback
def get_financial_data(ticker_symbol):
    print(f"Fetching financial data for {ticker_symbol}...")
    
    # First try yahooquery
    try:
        t_query = Ticker(ticker_symbol)
        
        try:
            balance_sheet = t_query.balance_sheet()
            total_debt = balance_sheet.loc['TotalDebt'].iloc[-1]
            print(f"Total Debt from yahooquery: ${total_debt:,.0f}")
        except Exception as e:
            print(f"Error fetching balance sheet from yahooquery: {e}")
            balance_sheet = None
            total_debt = None
        
        try:
            income_stmt = t_query.income_statement()
            interest_expense = income_stmt.loc['InterestExpense'].iloc[-1]
            income_before_tax = income_stmt.loc['PretaxIncome'].iloc[-1]
            income_tax_expense = income_stmt.loc['TaxProvision'].iloc[-1]
            tax_rate = income_tax_expense / income_before_tax
            print(f"Interest Expense from yahooquery: ${interest_expense:,.0f}")
            print(f"Effective Tax Rate from yahooquery: {tax_rate:.4f}")
        except Exception as e:
            print(f"Error fetching income statement from yahooquery: {e}")
            income_stmt = None
            interest_expense = None
            tax_rate = None
            
    except Exception as e:
        print(f"Error with yahooquery: {e}")
        balance_sheet = None
        income_stmt = None
        total_debt = None
        interest_expense = None
        tax_rate = None
    
    # If yahooquery failed, try yfinance
    if total_debt is None or interest_expense is None or tax_rate is None:
        print("Falling back to yfinance...")
        time.sleep(1)  # Avoid rate limiting
        
        try:
            yf_ticker = get_yf_ticker(ticker_symbol)
            
            # Get total debt from yfinance
            if total_debt is None:
                try:
                    # Try to get from info first
                    total_debt = yf_ticker.info.get('totalDebt', None)
                    
                    # If not available, try balance sheet
                    if total_debt is None:
                        bs_data = yf_ticker.balance_sheet
                        if bs_data is not None and not bs_data.empty:
                            # Try different potential column names for debt
                            debt_cols = ['Total Debt', 'Long Term Debt', 'LongTermDebt']
                            for col in debt_cols:
                                if col in bs_data.index:
                                    total_debt = bs_data.loc[col].iloc[0]
                                    break
                    
                    # If still None, try combining long-term and short-term debt
                    if total_debt is None:
                        long_term_debt = yf_ticker.info.get('longTermDebt', 0)
                        short_term_debt = yf_ticker.info.get('shortTermDebt', 0)
                        total_debt = long_term_debt + short_term_debt
                    
                    if total_debt is not None:
                        print(f"Total Debt from yfinance: ${total_debt:,.0f}")
                except Exception as e:
                    print(f"Error getting debt from yfinance: {e}")
                    
            # Get interest expense and tax rate from yfinance
            if interest_expense is None or tax_rate is None:
                try:
                    income_data = yf_ticker.financials
                    if income_data is not None and not income_data.empty:
                        # Try to find interest expense
                        interest_cols = ['Interest Expense', 'InterestExpense']
                        for col in interest_cols:
                            if col in income_data.index:
                                interest_expense = abs(income_data.loc[col].iloc[0])
                                print(f"Interest Expense from yfinance: ${interest_expense:,.0f}")
                                break
                        
                        # Try to calculate tax rate
                        if tax_rate is None:
                            tax_cols = ['Income Tax Expense', 'TaxProvision', 'IncomeTaxExpense']
                            income_cols = ['Income Before Tax', 'PretaxIncome', 'EBT']
                            
                            tax_expense = None
                            for col in tax_cols:
                                if col in income_data.index:
                                    tax_expense = income_data.loc[col].iloc[0]
                                    break
                                    
                            income_before_tax = None
                            for col in income_cols:
                                if col in income_data.index:
                                    income_before_tax = income_data.loc[col].iloc[0]
                                    break
                            
                            if tax_expense is not None and income_before_tax is not None and income_before_tax != 0:
                                tax_rate = tax_expense / income_before_tax
                                print(f"Effective Tax Rate from yfinance: {tax_rate:.4f}")
                except Exception as e:
                    print(f"Error getting income data from yfinance: {e}")
        
        except Exception as e:
            print(f"Error with yfinance fallback: {e}")
    
    # If still missing data, use defaults
    if total_debt is None:
        total_debt = 1000000000  # Default placeholder
        print(f"Using default Total Debt: ${total_debt:,.0f}")
        
    if interest_expense is None:
        interest_expense = total_debt * 0.04  # Assume 4% interest rate
        print(f"Using default Interest Expense: ${interest_expense:,.0f}")
        
    if tax_rate is None:
        tax_rate = 0.25  # Default tax rate
        print(f"Using default Tax Rate: {tax_rate:.4f}")
    
    return {
        'total_debt': total_debt,
        'interest_expense': interest_expense,
        'tax_rate': tax_rate
    }

# Get data
ticker = "TSLA"
tsla = get_yf_ticker(ticker)

# 1. Cost of Equity Components
# Get beta
beta = tsla.info.get('beta', None)
if beta is None:
    print("Beta not available, using default of 1.2 for tech company")
    beta = 1.2
else:
    print(f"Beta: {beta}")

# Get risk-free rate (using 10-year Treasury yield as proxy)
try:
    treasury = get_yf_ticker("^TNX")
    risk_free_rate = treasury.info.get('regularMarketPrice', None)
    if risk_free_rate is None:
        print("Risk-free rate not available, using default of 3.5%")
        risk_free_rate = 0.035
    else:
        risk_free_rate = risk_free_rate / 100  # Convert to decimal
except Exception as e:
    print(f"Error getting risk-free rate: {e}")
    risk_free_rate = 0.035  # Default value
print(f"Risk-free rate: {risk_free_rate:.4f}")

# Calculate market risk premium using historical data
try:
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=5*365)
    market_index = get_yf_ticker("^HSI")  # Hang Seng for HK stocks
    market_data = market_index.history(start=start_date, end=end_date)
    
    # Calculate monthly returns and annualize
    market_data['Monthly_Return'] = market_data['Close'].pct_change(21)
    market_data = market_data.dropna()
    expected_market_return = ((1 + market_data['Monthly_Return'].mean()) ** 12) - 1
    print(f"Expected Market Return: {expected_market_return:.4f}")
    
    # Calculate market risk premium
    market_risk_premium = expected_market_return - risk_free_rate
except Exception as e:
    print(f"Error calculating market risk premium: {e}")
    market_risk_premium = 0.055  # Default value
print(f"Market risk premium: {market_risk_premium:.4f}")

# Calculate cost of equity using CAPM
cost_of_equity = risk_free_rate + beta * market_risk_premium
print(f"Cost of Equity: {cost_of_equity:.4f}")

# 2. Cost of Debt Components
# Get financial data with fallback between yahooquery and yfinance
financial_data = get_financial_data(ticker)
total_debt = financial_data['total_debt']
interest_expense = financial_data['interest_expense']
tax_rate = financial_data['tax_rate']

# Calculate pre-tax cost of debt
if total_debt == 0:
    cost_of_debt_pretax = 0
else:
    cost_of_debt_pretax = interest_expense / total_debt
print(f"Pre-tax Cost of Debt: {cost_of_debt_pretax:.4f}")

# Calculate after-tax cost of debt
cost_of_debt = cost_of_debt_pretax * (1 - tax_rate)
print(f"After-tax Cost of Debt: {cost_of_debt:.4f}")

# 3. Weight Components
# Get market cap (equity value)
market_cap = tsla.info.get('marketCap', None)
if market_cap is None:
    shares_outstanding = tsla.info.get('sharesOutstanding', 0)
    current_price = tsla.info.get('regularMarketPrice', 0)
    market_cap = shares_outstanding * current_price
    if market_cap == 0:
        market_cap = total_debt * 3  # Default fallback assuming 3:1 equity:debt ratio
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

# Optional: Alternative calculation using the formula from the question
# Assuming ρF (cost of operations) is similar to cost of equity before leverage adjustment
cost_of_operations = cost_of_equity
leverage_ratio = total_debt / market_cap
cost_of_equity_alt = cost_of_operations + leverage_ratio * (cost_of_operations - cost_of_debt)
print(f"\nCost of Equity (alternative formula): {cost_of_equity_alt:.4f} or {cost_of_equity_alt*100:.2f}%")