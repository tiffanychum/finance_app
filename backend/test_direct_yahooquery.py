#!/usr/bin/env python3
"""
Test script to verify direct yahooquery financial data methods.
"""

from yahooquery import Ticker
import pandas as pd
import sys

def test_direct_financial_data(ticker_symbol):
    """Test direct yahooquery methods for a specific ticker"""
    print(f"\n{'='*80}\nTesting direct yahooquery methods for {ticker_symbol}...\n{'='*80}")
    
    try:
        stock = Ticker(ticker_symbol)
        
        # Test balance_sheet() method
        print("\nTesting balance_sheet() method...")
        balance_sheet = stock.balance_sheet(frequency='a')
        if isinstance(balance_sheet, str):
            print(f"ERROR: balance_sheet returned an error string: {balance_sheet}")
        elif balance_sheet.empty:
            print("WARNING: balance_sheet returned an empty DataFrame")
        else:
            print(f"SUCCESS: balance_sheet returned a DataFrame with {len(balance_sheet)} rows")
            print(f"Columns: {list(balance_sheet.columns)[:10]}...")
            print(f"First row sample: {dict(list(balance_sheet.iloc[0].items())[:5])}...")
        
        # Test income_statement() method
        print("\nTesting income_statement() method...")
        income_statement = stock.income_statement(frequency='a')
        if isinstance(income_statement, str):
            print(f"ERROR: income_statement returned an error string: {income_statement}")
        elif income_statement.empty:
            print("WARNING: income_statement returned an empty DataFrame")
        else:
            print(f"SUCCESS: income_statement returned a DataFrame with {len(income_statement)} rows")
            print(f"Columns: {list(income_statement.columns)[:10]}...")
            print(f"First row sample: {dict(list(income_statement.iloc[0].items())[:5])}...")
        
        # Test cash_flow() method
        print("\nTesting cash_flow() method...")
        cash_flow = stock.cash_flow(frequency='a')
        if isinstance(cash_flow, str):
            print(f"ERROR: cash_flow returned an error string: {cash_flow}")
        elif cash_flow.empty:
            print("WARNING: cash_flow returned an empty DataFrame")
        else:
            print(f"SUCCESS: cash_flow returned a DataFrame with {len(cash_flow)} rows")
            print(f"Columns: {list(cash_flow.columns)[:10]}...")
            print(f"First row sample: {dict(list(cash_flow.iloc[0].items())[:5])}...")
        
        # Test financial_data property
        print("\nTesting financial_data property...")
        financial_data = stock.financial_data
        if isinstance(financial_data, str):
            print(f"ERROR: financial_data returned an error string: {financial_data}")
        elif not financial_data:
            print("WARNING: financial_data returned empty data")
        else:
            print(f"SUCCESS: financial_data returned data")
            ticker_key = ticker_symbol.upper()
            if ticker_key in financial_data:
                print(f"Sample data: {dict(list(financial_data[ticker_key].items())[:5])}...")
            else:
                print(f"WARNING: Ticker {ticker_key} not found in financial_data")
        
        # Test key_stats property
        print("\nTesting key_stats property...")
        key_stats = stock.key_stats
        if isinstance(key_stats, str):
            print(f"ERROR: key_stats returned an error string: {key_stats}")
        elif not key_stats:
            print("WARNING: key_stats returned empty data")
        else:
            print(f"SUCCESS: key_stats returned data")
            ticker_key = ticker_symbol.upper()
            if ticker_key in key_stats:
                print(f"Sample data: {dict(list(key_stats[ticker_key].items())[:5])}...")
            else:
                print(f"WARNING: Ticker {ticker_key} not found in key_stats")
                
        return True
    except Exception as e:
        print(f"ERROR: Exception occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Main function to test multiple tickers"""
    # Default test tickers - mix of large, medium and small companies
    test_tickers = ["AAPL", "TSLA", "MSFT", "XOM", "NVDA", "WMT"]
    
    # Use command line arguments if provided
    if len(sys.argv) > 1:
        test_tickers = sys.argv[1:]
    
    print(f"Testing {len(test_tickers)} tickers: {', '.join(test_tickers)}")
    
    # Test each ticker
    results = {}
    for ticker in test_tickers:
        results[ticker] = test_direct_financial_data(ticker)
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for ticker, success in results.items():
        print(f"{ticker}: {'SUCCESS' if success else 'FAILED'}")

if __name__ == "__main__":
    main() 