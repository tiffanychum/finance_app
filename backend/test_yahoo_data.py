#!/usr/bin/env python3
"""
Test script to examine Yahoo Finance data structure for different tickers.
This helps diagnose issues with the data format in the fundamental analysis app.
"""

from yahooquery import Ticker
import json
import sys

def test_ticker_data(ticker_symbol):
    """Test data availability for a specific ticker"""
    print(f"\n{'='*80}\nTesting {ticker_symbol}...\n{'='*80}")
    
    try:
        stock = Ticker(ticker_symbol)
        
        # Get basic financial modules
        modules = [
            "incomeStatementHistory", 
            "balanceSheetHistory",
            "financialData",
            "defaultKeyStatistics"
        ]
        
        print(f"Fetching data for {ticker_symbol}...")
        data = stock.get_modules(modules)
        
        ticker_key = ticker_symbol.upper()
        if ticker_key not in data:
            print(f"ERROR: Ticker {ticker_key} not found in data")
            return
        
        # Check for errors in the data
        if isinstance(data.get(ticker_key), str):
            print(f"ERROR: API returned error: {data.get(ticker_key)}")
            return
            
        # Check income statement
        income_data = data.get(ticker_key, {}).get("incomeStatementHistory", {})
        if isinstance(income_data, str):
            print(f"ERROR: Income data is a string: {income_data}")
        else:
            income_statements = income_data.get("incomeStatementHistory", [])
            print(f"Income statements available: {len(income_statements)}")
            
            if income_statements:
                # Print available date format
                endDate = income_statements[0].get("endDate", {})
                print(f"End date format: {type(endDate)}")
                if isinstance(endDate, dict):
                    print(f"End date keys: {endDate.keys()}")
                
                # Print first few keys from income statement
                keys = list(income_statements[0].keys())
                print(f"Income statement keys ({len(keys)}): {keys[:10]}...")
                
                # Check for key income statement fields
                for field in ["totalRevenue", "costOfRevenue", "researchDevelopment", "sellingGeneralAdministrative"]:
                    val = income_statements[0].get(field, "NOT FOUND")
                    val_type = type(val)
                    print(f"Field '{field}': {val_type} {val}")
        
        # Check balance sheet
        balance_data = data.get(ticker_key, {}).get("balanceSheetHistory", {})
        if isinstance(balance_data, str):
            print(f"ERROR: Balance data is a string: {balance_data}")
        else:
            balance_sheets = balance_data.get("balanceSheetHistory", [])
            print(f"Balance sheets available: {len(balance_sheets)}")
            
            if balance_sheets:
                # Print first few keys from balance sheet
                keys = list(balance_sheets[0].keys())
                print(f"Balance sheet keys ({len(keys)}): {keys[:10]}...")
                
                # Check for key balance sheet fields
                for field in ["cash", "totalAssets", "totalLiab", "totalStockholderEquity"]:
                    val = balance_sheets[0].get(field, "NOT FOUND")
                    val_type = type(val)
                    print(f"Field '{field}': {val_type} {val}")
        
        # Summarize financial data availability
        has_financial_data = "financialData" in data.get(ticker_key, {})
        has_key_stats = "defaultKeyStatistics" in data.get(ticker_key, {})
        
        print(f"Financial data available: {has_financial_data}")
        print(f"Key statistics available: {has_key_stats}")
        
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
        results[ticker] = test_ticker_data(ticker)
    
    # Summary
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    for ticker, success in results.items():
        print(f"{ticker}: {'SUCCESS' if success else 'FAILED'}")

if __name__ == "__main__":
    main() 