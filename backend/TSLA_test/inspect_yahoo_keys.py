import yfinance as yf
import pandas as pd

def inspect_apple_financial_keys():
    """Display all available keys in Apple's Yahoo Finance data"""
    print("Fetching Apple data from Yahoo Finance...")
    aapl = yf.Ticker("AAPL")
    
    # Print available info keys
    print("\n=== INFO KEYS ===")
    info = aapl.info
    print(list(info.keys()))
    
    # Print balance sheet keys
    print("\n=== BALANCE SHEET KEYS ===")
    bs = aapl.balance_sheet
    if not bs.empty:
        print("Annual Balance Sheet Index:")
        print(list(bs.index))
    
    # Print quarterly balance sheet keys
    qbs = aapl.quarterly_balance_sheet
    if not qbs.empty:
        print("\nQuarterly Balance Sheet Index:")
        print(list(qbs.index))
    
    # Print income statement keys
    print("\n=== INCOME STATEMENT KEYS ===")
    income = aapl.financials
    if not income.empty:
        print("Annual Income Statement Index:")
        print(list(income.index))
    
    # Print quarterly income statement keys
    qincome = aapl.quarterly_financials
    if not qincome.empty:
        print("\nQuarterly Income Statement Index:")
        print(list(qincome.index))
    
    # Print cashflow keys
    print("\n=== CASHFLOW KEYS ===")
    cf = aapl.cashflow
    if not cf.empty:
        print("Annual Cashflow Index:")
        print(list(cf.index))
    
    # Print quarterly cashflow keys
    qcf = aapl.quarterly_cashflow
    if not qcf.empty:
        print("\nQuarterly Cashflow Index:")
        print(list(qcf.index))

if __name__ == "__main__":
    inspect_apple_financial_keys() 