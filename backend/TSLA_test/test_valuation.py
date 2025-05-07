import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def calculate_residual_earnings_valuation(bs_path, is_path, wacc, info_path=None):
    """
    Calculate residual earnings valuation based on reconciled financial statements
    
    Parameters:
    bs_path (str): Path to reconciled balance sheet CSV
    is_path (str): Path to reconciled income statement CSV
    wacc (float): Weighted Average Cost of Capital (as decimal)
    info_path (str): Path to info JSON file with market data (optional)
    
    Returns:
    DataFrame: Valuation metrics and detailed calculations
    """
    # Load reconciled financial statements
    bs = pd.read_csv(bs_path, index_col=0)
    is_stmt = pd.read_csv(is_path, index_col=0)
    
    # Filter out empty/header rows - handle mixed index types safely
    def is_header_or_empty(idx):
        if isinstance(idx, str):
            return idx.startswith("***") or idx == ""
        return False
    
    bs = bs[~pd.Series(bs.index).apply(is_header_or_empty).values]
    is_stmt = is_stmt[~pd.Series(is_stmt.index).apply(is_header_or_empty).values]
    
    # Extract key metrics
    # Net Operating Assets (NOA)
    noa = bs.loc['C. NET OPERATING ASSETS (5-11)']
    # Ensure NOA is numeric
    noa = pd.to_numeric(noa, errors='coerce')
    
    # Operating Income (OI)
    operating_income = is_stmt.loc['7. Operating Income (Loss)']
    operating_income = pd.to_numeric(operating_income, errors='coerce')
    
    # Common Equity
    common_equity = (
        pd.to_numeric(bs.loc['28. Common Stock'], errors='coerce') + 
        pd.to_numeric(bs.loc['29. Additional Paid-In Capital'], errors='coerce') + 
        pd.to_numeric(bs.loc['30. Retained Earnings'], errors='coerce') +
        pd.to_numeric(bs.loc['31. Other Equity Adjustments'], errors='coerce')
    )
    
    # Get shares outstanding
    if 'Share Issued' in bs.index:
        shares_outstanding = pd.to_numeric(bs.loc['Share Issued'], errors='coerce')
    else:
        # Get from info file if available
        shares_outstanding = None
        if info_path and os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
                shares_outstanding_value = info.get('sharesOutstanding', 3216000000)  # From TSLA_info.json
                shares_outstanding = pd.Series([shares_outstanding_value] * len(bs.columns), index=bs.columns)
    
    # Setup results DataFrame
    columns = list(bs.columns)
    results = pd.DataFrame(index=[
        'A. INPUTS',
        '1. Net Operating Assets (NOA)',
        '2. Operating Income (OI)',
        '3. WACC',
        '4. Common Equity Book Value',
        '5. Shares Outstanding (millions)',
        '',
        'B. RESIDUAL EARNINGS CALCULATION',
        '6. Prior Period NOA',
        '7. Capital Charge (WACC × Prior NOA)',
        '8. Residual Earnings (OI - Capital Charge)',
        '9. Residual Earnings to Sales %',
        '',
        'C. VALUATION',
        '10. Book Value of Common Equity',
        '11. Present Value of RE (RE ÷ WACC)',
        '12. Intrinsic Equity Value (10 + 11)',
        '13. Value per Share',
        '',
        'D. MARKET COMPARISON',
        '14. Current Market Price',
        '15. Market Capitalization',
        '16. Price-to-Book Ratio',
        '17. Price-to-Value Ratio',
        '',
        'E. PERFORMANCE METRICS',
        '18. Return on Net Operating Assets (RNOA)',
        '19. Required Return (WACC × NOA)',
        '20. Economic Value Added',
        '21. Return Spread (RNOA - WACC)',
    ], columns=columns)
    
    # Format headers
    for section in ['A. INPUTS', 'B. RESIDUAL EARNINGS CALCULATION', 'C. VALUATION', 
                   'D. MARKET COMPARISON', 'E. PERFORMANCE METRICS']:
        results.loc[section] = '***' + section + '***'
    
    # Fill inputs section
    results.loc['1. Net Operating Assets (NOA)'] = noa
    results.loc['2. Operating Income (OI)'] = operating_income
    results.loc['3. WACC'] = wacc
    results.loc['4. Common Equity Book Value'] = common_equity
    
    if shares_outstanding is not None:
        results.loc['5. Shares Outstanding (millions)'] = shares_outstanding / 1e6  # Convert to millions
    
    # Calculate prior period NOA (shift values by 1 period)
    prior_noa = pd.Series(index=columns, dtype=float)  # Explicitly create as float type
    for i in range(1, len(columns)):
        try:
            # Explicitly convert to float
            prior_noa[columns[i-1]] = float(noa[columns[i]])
        except (ValueError, TypeError):
            print(f"Warning: Could not convert NOA value for {columns[i]} to float. Setting to NaN.")
            prior_noa[columns[i-1]] = np.nan
    
    # For the last period, we don't have a prior NOA, so leave it NaN
    results.loc['6. Prior Period NOA'] = prior_noa
    
    # Calculate capital charge (WACC × Prior NOA)
    capital_charge = prior_noa * wacc
    results.loc['7. Capital Charge (WACC × Prior NOA)'] = capital_charge
    
    # Calculate residual earnings
    residual_earnings = operating_income - capital_charge
    results.loc['8. Residual Earnings (OI - Capital Charge)'] = residual_earnings
    
    # Residual earnings as % of sales
    revenue = pd.to_numeric(is_stmt.loc['1. Total Revenue'], errors='coerce')
    # Avoid division by zero
    re_to_sales = pd.Series([np.nan] * len(columns), index=columns)
    for i in range(len(columns)):
        if not pd.isna(residual_earnings[columns[i]]) and not pd.isna(revenue[columns[i]]) and revenue[columns[i]] != 0:
            re_to_sales[columns[i]] = (residual_earnings[columns[i]] / revenue[columns[i]]) * 100
    
    results.loc['9. Residual Earnings to Sales %'] = re_to_sales
    
    # Calculate valuation
    results.loc['10. Book Value of Common Equity'] = common_equity
    
    # Present value of residual earnings (Average RE ÷ WACC)
    # Calculate the average of available residual earnings (non-NaN values)
    valid_re = residual_earnings.dropna()
    if len(valid_re) > 0:
        avg_residual_earnings = valid_re.mean()
        # Use the same average RE value for all periods
        pv_residual_earnings = pd.Series([avg_residual_earnings / wacc] * len(columns), index=columns)
        print(f"Average Residual Earnings: ${avg_residual_earnings:,.0f}")
        print(f"Present Value of RE: ${avg_residual_earnings / wacc:,.0f}")
    else:
        pv_residual_earnings = pd.Series([np.nan] * len(columns), index=columns)
        print("Warning: No valid residual earnings available for PV calculation")
    
    results.loc['11. Present Value of RE (RE ÷ WACC)'] = pv_residual_earnings
    
    # Intrinsic equity value (Book Value + PV of RE)
    intrinsic_value = common_equity + pv_residual_earnings
    results.loc['12. Intrinsic Equity Value (10 + 11)'] = intrinsic_value
    
    # Value per share
    if shares_outstanding is not None:
        value_per_share = intrinsic_value / shares_outstanding
        results.loc['13. Value per Share'] = value_per_share
    
    # Get market data if info file is available
    if info_path and os.path.exists(info_path):
        with open(info_path, 'r') as f:
            info = json.load(f)
            current_price = info.get('regularMarketPrice', None)
            market_cap = info.get('marketCap', None)
            
            # Fill market comparison section
            if current_price:
                results.loc['14. Current Market Price'] = pd.Series([current_price] * len(columns), index=columns)
            
            if market_cap:
                results.loc['15. Market Capitalization'] = pd.Series([market_cap] * len(columns), index=columns)
                
            if current_price and not common_equity.empty and shares_outstanding is not None:
                # Price-to-book ratio
                book_per_share = common_equity / shares_outstanding
                price_to_book = pd.Series([current_price / book_per_share[columns[0]]] * len(columns), index=columns)
                results.loc['16. Price-to-Book Ratio'] = price_to_book
                
                # Price-to-value ratio
                price_to_value = pd.Series([current_price / value_per_share[columns[0]]] * len(columns), index=columns)
                results.loc['17. Price-to-Value Ratio'] = price_to_value
    
    # Calculate performance metrics
    # Return on Net Operating Assets (RNOA)
    rnoa = pd.Series([np.nan] * len(columns), index=columns)
    for i in range(len(columns)):
        if not pd.isna(operating_income[columns[i]]) and not pd.isna(noa[columns[i]]) and noa[columns[i]] != 0:
            rnoa[columns[i]] = operating_income[columns[i]] / noa[columns[i]]
    
    results.loc['18. Return on Net Operating Assets (RNOA)'] = rnoa
    
    # Required return
    required_return = noa * wacc
    results.loc['19. Required Return (WACC × NOA)'] = required_return
    
    # Economic Value Added
    eva = operating_income - required_return
    results.loc['20. Economic Value Added'] = eva
    
    # Return spread
    return_spread = rnoa - wacc
    results.loc['21. Return Spread (RNOA - WACC)'] = return_spread
    
    # Save results
    results.to_csv('TSLA_residual_earnings_valuation.csv')
    
    try:
        # Create visual chart of key metrics
        plot_valuation_metrics(results)
    except Exception as e:
        print(f"Warning: Could not create charts: {e}")
    
    return results

def plot_valuation_metrics(results):
    """Create visualization of key valuation metrics"""
    # Format numbers as billions/millions
    def billions(x, pos):
        return f'${x/1e9:.1f}B'
    
    def millions(x, pos):
        return f'${x/1e6:.1f}M'
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Get columns with non-NaN values
    columns = [col for col in results.columns if not pd.isna(results.loc['8. Residual Earnings (OI - Capital Charge)', col])]
    
    if not columns:
        print("Warning: Not enough data for plotting")
        return
    
    # 1. Net Operating Assets vs Operating Income
    ax1 = axes[0, 0]
    ax1.bar(columns, results.loc['1. Net Operating Assets (NOA)', columns], color='blue', alpha=0.6, label='Net Operating Assets')
    ax1_2 = ax1.twinx()
    ax1_2.plot(columns, results.loc['2. Operating Income (OI)', columns], color='red', marker='o', label='Operating Income')
    ax1.set_title('Net Operating Assets vs Operating Income')
    ax1.yaxis.set_major_formatter(FuncFormatter(billions))
    ax1_2.yaxis.set_major_formatter(FuncFormatter(billions))
    ax1.set_ylabel('NOA ($B)')
    ax1_2.set_ylabel('Operating Income ($B)')
    ax1.legend(loc='upper left')
    ax1_2.legend(loc='upper right')
    
    # 2. Residual Earnings
    ax2 = axes[0, 1]
    ax2.bar(columns, results.loc['8. Residual Earnings (OI - Capital Charge)', columns], color='green')
    ax2.set_title('Residual Earnings')
    ax2.yaxis.set_major_formatter(FuncFormatter(billions))
    ax2.set_ylabel('$B')
    
    # 3. Book Value vs Intrinsic Value vs Market Value
    ax3 = axes[1, 0]
    width = 0.25  # Narrower bars to fit three
    x = np.arange(len(columns))
    
    # Book Value
    ax3.bar(x - width, results.loc['10. Book Value of Common Equity', columns], width, 
            label='Book Value', color='blue', alpha=0.6)
    
    # Intrinsic Value
    ax3.bar(x, results.loc['12. Intrinsic Equity Value (10 + 11)', columns], width, 
            label='Intrinsic Value', color='green', alpha=0.6)
    
    # Market Value if available
    if '15. Market Capitalization' in results.index and not pd.isna(results.loc['15. Market Capitalization', columns[0]]):
        market_cap = results.loc['15. Market Capitalization', columns[0]]
        # Create a series with the market cap for each period
        market_caps = pd.Series([market_cap] * len(columns), index=columns)
        ax3.bar(x + width, market_caps, width, 
                label=f'Market Value (${market_cap/1e9:.1f}B)', color='red', alpha=0.6)
    
    ax3.set_title('Book Value vs Intrinsic Value vs Market Value')
    ax3.set_xticks(x)
    ax3.set_xticklabels(columns)
    ax3.yaxis.set_major_formatter(FuncFormatter(billions))
    ax3.set_ylabel('$B')
    ax3.legend()
    
    # 4. Value per Share
    ax4 = axes[1, 1]
    ax4.plot(columns, results.loc['13. Value per Share', columns], marker='o', color='purple')
    
    # If market price available, add it to the chart
    if '14. Current Market Price' in results.index and not pd.isna(results.loc['14. Current Market Price', columns[0]]):
        current_price = results.loc['14. Current Market Price', columns[0]]
        ax4.axhline(y=current_price, color='r', linestyle='--', label=f'Current Price (${current_price:.2f})')
    
    ax4.set_title('Value per Share')
    ax4.set_ylabel('$')
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig('TSLA_valuation_charts.png')
    plt.close()

# Use the provided WACC of 27.74%
wacc = 0.2774  # 27.74% as specified by user

# Calculate valuation
try:
    valuation = calculate_residual_earnings_valuation(
        'TSLA_reconciled_balance_sheet.csv', 
        'TSLA_reconciled_income_statement.csv', 
        wacc,
        'TSLA_info.json'
    )
    
    # Print summary of most recent period
    most_recent = valuation.columns[0]
    print(f"\n=== TESLA RESIDUAL EARNINGS VALUATION ({most_recent}) ===")
    print(f"Net Operating Assets (NOA): ${valuation.loc['1. Net Operating Assets (NOA)', most_recent]:,.0f}")
    print(f"Operating Income (OI): ${valuation.loc['2. Operating Income (OI)', most_recent]:,.0f}")
    print(f"WACC: {valuation.loc['3. WACC', most_recent]:.2%}")
    
    if not pd.isna(valuation.loc['8. Residual Earnings (OI - Capital Charge)', most_recent]):
        print(f"Residual Earnings: ${valuation.loc['8. Residual Earnings (OI - Capital Charge)', most_recent]:,.0f}")
        print(f"Book Value: ${valuation.loc['10. Book Value of Common Equity', most_recent]:,.0f}")
        print(f"Present Value of Residual Earnings: ${valuation.loc['11. Present Value of RE (RE ÷ WACC)', most_recent]:,.0f}")
        print(f"Intrinsic Equity Value: ${valuation.loc['12. Intrinsic Equity Value (10 + 11)', most_recent]:,.0f}")
        print(f"Value per Share: ${valuation.loc['13. Value per Share', most_recent]:.2f}")
    else:
        print("Note: Cannot calculate residual earnings for the most recent period (requires prior period NOA)")
        # Try using the second most recent period if available
        if len(valuation.columns) > 1:
            second_period = valuation.columns[1]
            if not pd.isna(valuation.loc['8. Residual Earnings (OI - Capital Charge)', second_period]):
                print(f"\nUsing second most recent period ({second_period}) for valuation:")
                print(f"Residual Earnings: ${valuation.loc['8. Residual Earnings (OI - Capital Charge)', second_period]:,.0f}")
                print(f"Book Value: ${valuation.loc['10. Book Value of Common Equity', second_period]:,.0f}")
                print(f"Present Value of RE: ${valuation.loc['11. Present Value of RE (RE ÷ WACC)', second_period]:,.0f}")
                print(f"Intrinsic Equity Value: ${valuation.loc['12. Intrinsic Equity Value (10 + 11)', second_period]:,.0f}")
                print(f"Value per Share: ${valuation.loc['13. Value per Share', second_period]:.2f}")
    
    if '14. Current Market Price' in valuation.index and not pd.isna(valuation.loc['14. Current Market Price', most_recent]):
        market_price = valuation.loc['14. Current Market Price', most_recent]
        print(f"Current Market Price: ${market_price:.2f}")
        
        # Find a valid period for price-to-value comparison
        valid_period = None
        for col in valuation.columns:
            if not pd.isna(valuation.loc['13. Value per Share', col]):
                valid_period = col
                break
                
        if valid_period:
            price_to_value = market_price / valuation.loc['13. Value per Share', valid_period]
            if price_to_value > 1.2:
                conclusion = "OVERVALUED"
            elif price_to_value < 0.8:
                conclusion = "UNDERVALUED"
            else:
                conclusion = "FAIRLY VALUED"
            
            print(f"Price/Value Ratio: {price_to_value:.2f}")
            print(f"Valuation Assessment: {conclusion}")
    
    print("\nDetailed results saved to TSLA_residual_earnings_valuation.csv")
    
except Exception as e:
    print(f"Error in valuation calculation: {e}")
    import traceback
    traceback.print_exc()