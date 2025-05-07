import yfinance as yf
import numpy as np
import pandas as pd
from yahooquery import Ticker
import datetime
from curl_cffi import requests

# Configure requests with Chrome browser impersonation to avoid rate limiting
def get_yf_ticker(symbol):
    session = requests.Session(impersonate="chrome")
    # session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    return yf.Ticker(symbol, session=session)

# Get data
ticker = "9988.HK"
tsla = get_yf_ticker(ticker)

# 1. Cost of Equity Components
# Get beta
beta = tsla.info['beta']
print(f"Beta: {beta}")

# Get risk-free rate (using 10-year Treasury yield as proxy)
treasury = get_yf_ticker("^TNX")
risk_free_rate = treasury.info['regularMarketPrice'] / 100  # Convert to decimal
print(f"Risk-free rate: {risk_free_rate:.4f}")

# Calculate market risk premium using historical data
# Get S&P 500 historical data for the past 5 years
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=5*365)
sp500 = get_yf_ticker("^GSPC")
sp500_data = sp500.history(start=start_date, end=end_date)

# Calculate annual returns
sp500_data['Annual_Return'] = sp500_data['Close'].pct_change(252)
sp500_data = sp500_data.dropna()

# Calculate average annual return (expected market return)
expected_market_return = sp500_data['Annual_Return'].mean()
print(f"Expected Market Return: {expected_market_return:.4f}")

# Calculate market risk premium
market_risk_premium = expected_market_return - risk_free_rate
print(f"Market risk premium: {market_risk_premium:.4f}")

# Calculate cost of equity using CAPM
cost_of_equity = risk_free_rate + beta * market_risk_premium
print(f"Cost of Equity: {cost_of_equity:.4f}")

# 2. Cost of Debt Components
# Get financials
t_query = Ticker(ticker)
balance_sheet = t_query.balance_sheet()
income_stmt = t_query.income_statement()

# Get total debt
total_debt = balance_sheet.loc['TotalDebt'].iloc[-1]
print(f"Total Debt: ${total_debt:,.0f}")

# Get interest expense
interest_expense = income_stmt.loc['InterestExpense'].iloc[-1]
print(f"Interest Expense: ${interest_expense:,.0f}")

# Calculate pre-tax cost of debt
cost_of_debt_pretax = interest_expense / total_debt
print(f"Pre-tax Cost of Debt: {cost_of_debt_pretax:.4f}")

# Get tax rate
income_before_tax = income_stmt.loc['PretaxIncome'].iloc[-1]
income_tax_expense = income_stmt.loc['TaxProvision'].iloc[-1]
tax_rate = income_tax_expense / income_before_tax
print(f"Effective Tax Rate: {tax_rate:.4f}")

# Calculate after-tax cost of debt
cost_of_debt = cost_of_debt_pretax * (1 - tax_rate)
print(f"After-tax Cost of Debt: {cost_of_debt:.4f}")

# 3. Weight Components
# Get market cap (equity value)
market_cap = tsla.info['marketCap']
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