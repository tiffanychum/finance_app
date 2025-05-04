#!/usr/bin/env python3
"""
Test script to directly calculate enterprise valuation for a given ticker.
This bypasses the API infrastructure to identify specific issues with the calculation.
"""

from yahooquery import Ticker
import json
import sys

# Safe get function to handle different data formats
def safe_get(obj, key, default=0):
    """Safely extract values from Yahoo Finance data"""
    val = obj.get(key, default)
    if isinstance(val, dict) and "raw" in val:
        return val.get("raw", default)
    return val or default

def calculate_enterprise_value(ticker_symbol):
    """Calculate enterprise value for a ticker"""
    print(f"\n{'='*80}\nCalculating Enterprise Value for {ticker_symbol}...\n{'='*80}")
    
    try:
        stock = Ticker(ticker_symbol)
        
        # Get necessary financial data
        modules = [
            "incomeStatementHistory", 
            "balanceSheetHistory",
            "financialData",
            "defaultKeyStatistics",
            "earningsTrend"
        ]
        
        print(f"Fetching data for {ticker_symbol}...")
        data = stock.get_modules(modules)
        
        ticker_key = ticker_symbol.upper()
        if ticker_key not in data:
            print(f"ERROR: Ticker {ticker_key} not found in data")
            return
        
        # Extract income statement and balance sheet data
        income_data = data.get(ticker_key, {}).get("incomeStatementHistory", {})
        balance_data = data.get(ticker_key, {}).get("balanceSheetHistory", {})
        
        if isinstance(income_data, str):
            print(f"ERROR: Income data is a string: {income_data}")
            return
            
        if isinstance(balance_data, str):
            print(f"ERROR: Balance data is a string: {balance_data}")
            return
            
        income_statements = income_data.get("incomeStatementHistory", [])
        balance_sheets = balance_data.get("balanceSheetHistory", [])
        
        print(f"Income statements available: {len(income_statements)}")
        print(f"Balance sheets available: {len(balance_sheets)}")
        
        if not income_statements:
            print("ERROR: No income statement data available")
            return
            
        if not balance_sheets:
            print("ERROR: No balance sheet data available")
            return
            
        # Get the most recent statements
        latest_income = income_statements[0]
        latest_balance = balance_sheets[0]
        
        # Calculate key operational metrics
        # 1. Operating Income
        total_revenue = safe_get(latest_income, "totalRevenue")
        cost_of_revenue = safe_get(latest_income, "costOfRevenue")
        gross_margin = total_revenue - cost_of_revenue
        
        rd_expense = safe_get(latest_income, "researchDevelopment")
        sg_expense = safe_get(latest_income, "sellingGeneralAdministrative")
        operating_expenses = rd_expense + sg_expense
        
        core_oi_before_tax = gross_margin - operating_expenses
        
        # Tax estimation
        income_tax_expense = safe_get(latest_income, "incomeTaxExpense")
        income_before_tax = safe_get(latest_income, "incomeBeforeTax")
        tax_rate = income_tax_expense / income_before_tax if income_before_tax else 0.25
        
        tax_on_oi = core_oi_before_tax * tax_rate
        core_oi_after_tax = core_oi_before_tax - tax_on_oi
        
        other_oi = safe_get(latest_income, "otherOperatingExpenses")
        comprehensive_oi = core_oi_after_tax - other_oi
        
        # 2. Net Operating Assets (NOA)
        cash = safe_get(latest_balance, "cash")
        receivables = safe_get(latest_balance, "netReceivables")
        inventory = safe_get(latest_balance, "inventory")
        other_current_assets = safe_get(latest_balance, "otherCurrentAssets")
        ppe = safe_get(latest_balance, "propertyPlantEquipment")
        intangibles = safe_get(latest_balance, "goodWill") + safe_get(latest_balance, "intangibleAssets")
        
        total_operating_assets = cash + receivables + inventory + other_current_assets + ppe + intangibles
        
        accounts_payable = safe_get(latest_balance, "accountsPayable")
        accrued_liabilities = safe_get(latest_balance, "otherCurrentLiab")
        deferred_revenue = safe_get(latest_balance, "deferredLongTermRevenue")
        deferred_tax = safe_get(latest_balance, "deferredLongTermTax")
        
        total_operating_liabilities = accounts_payable + accrued_liabilities + deferred_revenue + deferred_tax
        
        net_operating_assets = total_operating_assets - total_operating_liabilities
        
        # 3. Net Financial Obligations (NFO)
        operating_cash = total_revenue * 0.02  # 2% of revenue for operations
        excess_cash = max(0, cash - operating_cash)
        long_term_investments = safe_get(latest_balance, "longTermInvestments")
        
        total_financial_assets = excess_cash + long_term_investments
        
        short_term_debt = safe_get(latest_balance, "shortLongTermDebt")
        long_term_debt = safe_get(latest_balance, "longTermDebt")
        other_liabilities = safe_get(latest_balance, "otherLiab")
        
        total_financial_obligations = short_term_debt + long_term_debt + other_liabilities
        
        net_financial_obligations = total_financial_obligations - total_financial_assets
        
        # 4. Cost of Capital Estimation
        beta = safe_get(data.get(ticker_key, {}).get("defaultKeyStatistics", {}), "beta", 1.0)
        risk_free_rate = 0.0158  # 1.58% approximation
        market_risk_premium = 0.0502  # 5.02% approximation
        cost_of_equity = risk_free_rate + (beta * market_risk_premium)
        
        # After-tax cost of debt (using 5% pre-tax estimate)
        cost_of_debt = 0.05 * (1 - tax_rate)
        
        # Market values
        current_price = safe_get(data.get(ticker_key, {}).get("financialData", {}), "currentPrice", 0)
        shares_outstanding = safe_get(data.get(ticker_key, {}).get("defaultKeyStatistics", {}), "sharesOutstanding", 0)
        
        market_cap = current_price * shares_outstanding
        market_debt = net_financial_obligations  # Approximated as book value
        
        total_market_value = market_cap + market_debt
        
        # WACC (Cost of operations)
        if total_market_value:
            cost_of_operations = (
                (market_cap / total_market_value) * cost_of_equity + 
                (market_debt / total_market_value) * cost_of_debt
            )
        else:
            cost_of_operations = 0.09  # Default 
        
        # 5. Residual Operating Income
        residual_operating_income = comprehensive_oi - (cost_of_operations * net_operating_assets)
        
        # 6. Growth Rate Estimation
        growth_data = data.get(ticker_key, {}).get("earningsTrend", {}).get("trend", [])
        if growth_data:
            yearly_data = [t for t in growth_data if t.get("period") == "+1y"]
            if yearly_data:
                growth_rate = safe_get(yearly_data[0].get("earningsEstimate", {}), "growth", 0.05)
            else:
                growth_rate = 0.05  # Default
        else:
            growth_rate = 0.05  # Default
        
        # 7. Enterprise Valuation
        if cost_of_operations > growth_rate:
            pv_of_reoi = residual_operating_income / (cost_of_operations - growth_rate)
        else:
            pv_of_reoi = residual_operating_income / 0.02  # Use 2% spread
            
        enterprise_value = net_operating_assets + pv_of_reoi
        
        # 8. Equity Value
        equity_value = enterprise_value - net_financial_obligations
        equity_value_per_share = equity_value / shares_outstanding if shares_outstanding else 0
        
        # Print results
        print("\nOPERATING INCOME CALCULATION:")
        print(f"Total Revenue: ${total_revenue:,.2f}")
        print(f"Cost of Revenue: ${cost_of_revenue:,.2f}")
        print(f"Gross Margin: ${gross_margin:,.2f}")
        print(f"Operating Expenses: ${operating_expenses:,.2f}")
        print(f"Core OI Before Tax: ${core_oi_before_tax:,.2f}")
        print(f"Tax Rate: {tax_rate:.2%}")
        print(f"Core OI After Tax: ${core_oi_after_tax:,.2f}")
        print(f"Comprehensive Operating Income: ${comprehensive_oi:,.2f}")
        
        print("\nNET OPERATING ASSETS CALCULATION:")
        print(f"Total Operating Assets: ${total_operating_assets:,.2f}")
        print(f"Total Operating Liabilities: ${total_operating_liabilities:,.2f}")
        print(f"Net Operating Assets (NOA): ${net_operating_assets:,.2f}")
        
        print("\nNET FINANCIAL OBLIGATIONS CALCULATION:")
        print(f"Total Financial Assets: ${total_financial_assets:,.2f}")
        print(f"Total Financial Obligations: ${total_financial_obligations:,.2f}")
        print(f"Net Financial Obligations (NFO): ${net_financial_obligations:,.2f}")
        
        print("\nCOST OF CAPITAL CALCULATION:")
        print(f"Beta: {beta:.2f}")
        print(f"Cost of Equity: {cost_of_equity:.2%}")
        print(f"Cost of Debt (after tax): {cost_of_debt:.2%}")
        print(f"Cost of Operations (WACC): {cost_of_operations:.2%}")
        
        print("\nRESIDUAL OPERATING INCOME:")
        print(f"Operating Income: ${comprehensive_oi:,.2f}")
        print(f"Capital Charge: ${(cost_of_operations * net_operating_assets):,.2f}")
        print(f"Residual Operating Income: ${residual_operating_income:,.2f}")
        
        print("\nVALUATION RESULTS:")
        print(f"Growth Rate: {growth_rate:.2%}")
        print(f"PV of Future ReOI: ${pv_of_reoi:,.2f}")
        print(f"Enterprise Value: ${enterprise_value:,.2f}")
        print(f"Net Financial Obligations: ${net_financial_obligations:,.2f}")
        print(f"Equity Value: ${equity_value:,.2f}")
        print(f"Shares Outstanding: {shares_outstanding:,.0f}")
        print(f"Equity Value per Share: ${equity_value_per_share:.2f}")
        print(f"Current Market Price: ${current_price:.2f}")
        
        if current_price:
            premium = equity_value_per_share - current_price
            discount_percent = (premium / equity_value_per_share) * 100 if equity_value_per_share else 0
            print(f"Premium/Discount: ${premium:.2f} ({discount_percent:.2f}%)")
        
        return True
    except Exception as e:
        print(f"ERROR: Exception occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """Main function to test tickers"""
    # Default ticker to test
    test_ticker = "AAPL"
    
    # Use command line argument if provided
    if len(sys.argv) > 1:
        test_ticker = sys.argv[1]
    
    calculate_enterprise_value(test_ticker)

if __name__ == "__main__":
    main() 