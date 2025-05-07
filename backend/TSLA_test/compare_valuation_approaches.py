import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Import the original valuation function
# This is just for importing, the actual code remains in test_valuation.py
from test_valuation import calculate_residual_earnings_valuation

def comprehensive_tesla_valuation(bs_path, is_path, reasonable_wacc=0.12, info_path=None):
    """
    Calculate Tesla's valuation considering growth prospects and intangible assets
    
    Parameters:
    bs_path (str): Path to reconciled balance sheet CSV
    is_path (str): Path to reconciled income statement CSV 
    reasonable_wacc (float): More reasonable WACC for Tesla (default 12%)
    info_path (str): Path to info JSON file with market data (optional)
    
    Returns:
    dict: Complete valuation results with growth projections
    """
    # Load financial data
    bs = pd.read_csv(bs_path, index_col=0)
    is_stmt = pd.read_csv(is_path, index_col=0)
    
    # Filter out headers
    def is_header_or_empty(idx):
        if isinstance(idx, str):
            return idx.startswith("***") or idx == ""
        return False
    
    bs_filtered = bs[~pd.Series(bs.index).apply(is_header_or_empty).values]
    is_filtered = is_stmt[~pd.Series(is_stmt.index).apply(is_header_or_empty).values]
    
    # Get most recent period data
    most_recent = is_filtered.columns[0]
    
    # Extract key financial data
    revenue = pd.to_numeric(is_filtered.loc['1. Total Revenue', most_recent], errors='coerce')
    operating_income = pd.to_numeric(is_filtered.loc['7. Operating Income (Loss)', most_recent], errors='coerce')
    common_equity = (
        pd.to_numeric(bs_filtered.loc['28. Common Stock', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['29. Additional Paid-In Capital', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['30. Retained Earnings', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['31. Other Equity Adjustments', most_recent], errors='coerce')
    )
    cash = (
        pd.to_numeric(bs_filtered.loc['12. Cash and Cash Equivalents', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['13. Short-term Investments', most_recent], errors='coerce')
    )
    total_debt = (
        pd.to_numeric(bs_filtered.loc['20. Long-term Debt', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['21. Current Debt', most_recent], errors='coerce') +
        pd.to_numeric(bs_filtered.loc['22. Capital Lease Obligations', most_recent], errors='coerce')
    )
    
    # Get shares outstanding
    shares_outstanding = 3216000000  # Default value
    if info_path and os.path.exists(info_path):
        with open(info_path, 'r') as f:
            info = json.load(f)
            shares_outstanding = info.get('sharesOutstanding', shares_outstanding)
    
    # 1. Project future revenue growth by segment
    # Initial segment breakdown (estimated)
    ev_revenue = revenue * 0.85  # 85% from EVs
    software_revenue = revenue * 0.05  # 5% from software/FSD
    energy_revenue = revenue * 0.10  # 10% from energy
    
    # Growth projections for next 10 years
    projection_years = 10
    projections = pd.DataFrame(index=range(projection_years + 1))
    
    # Year 0 (current year)
    projections.loc[0, 'Year'] = most_recent.split('-')[0]
    projections.loc[0, 'EV_Revenue'] = ev_revenue
    projections.loc[0, 'Software_Revenue'] = software_revenue
    projections.loc[0, 'Energy_Revenue'] = energy_revenue
    projections.loc[0, 'Robotaxi_Revenue'] = 0
    projections.loc[0, 'Total_Revenue'] = revenue
    projections.loc[0, 'Operating_Income'] = operating_income
    projections.loc[0, 'Operating_Margin'] = operating_income / revenue
    
    # Growth rates
    ev_growth_rates = [0.25, 0.22, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05]
    software_growth_rates = [0.40, 0.35, 0.30, 0.28, 0.25, 0.20, 0.18, 0.15, 0.12, 0.10]
    energy_growth_rates = [0.45, 0.40, 0.35, 0.30, 0.25, 0.20, 0.18, 0.15, 0.12, 0.10]
    
    # Margin assumptions
    ev_margins = [0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.13, 0.14, 0.14, 0.15]
    software_margins = [0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.80, 0.80, 0.80, 0.80]
    energy_margins = [0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.24, 0.25, 0.25, 0.25]
    robotaxi_margins = [0.0, 0.0, 0.50, 0.60, 0.65, 0.70, 0.75, 0.75, 0.75, 0.75]
    
    # Robotaxi assumptions
    robotaxi_fleet = [0, 0, 10000, 50000, 100000, 250000, 500000, 750000, 1000000, 1250000]
    revenue_per_robotaxi = 30000  # Annual revenue per robotaxi
    
    # Project forward
    for year in range(1, projection_years + 1):
        projections.loc[year, 'Year'] = int(projections.loc[0, 'Year']) + year
        
        # Previous year values
        prev_ev = projections.loc[year-1, 'EV_Revenue']
        prev_software = projections.loc[year-1, 'Software_Revenue']
        prev_energy = projections.loc[year-1, 'Energy_Revenue']
        
        # Apply growth rates
        projections.loc[year, 'EV_Revenue'] = prev_ev * (1 + ev_growth_rates[min(year-1, len(ev_growth_rates)-1)])
        projections.loc[year, 'Software_Revenue'] = prev_software * (1 + software_growth_rates[min(year-1, len(software_growth_rates)-1)])
        projections.loc[year, 'Energy_Revenue'] = prev_energy * (1 + energy_growth_rates[min(year-1, len(energy_growth_rates)-1)])
        
        # Robotaxi revenue starts in year 3
        if year >= 3:
            projections.loc[year, 'Robotaxi_Revenue'] = robotaxi_fleet[min(year-1, len(robotaxi_fleet)-1)] * revenue_per_robotaxi
        else:
            projections.loc[year, 'Robotaxi_Revenue'] = 0
        
        # Total revenue
        projections.loc[year, 'Total_Revenue'] = (
            projections.loc[year, 'EV_Revenue'] + 
            projections.loc[year, 'Software_Revenue'] + 
            projections.loc[year, 'Energy_Revenue'] + 
            projections.loc[year, 'Robotaxi_Revenue']
        )
        
        # Calculate segment operating income
        ev_oi = projections.loc[year, 'EV_Revenue'] * ev_margins[min(year-1, len(ev_margins)-1)]
        software_oi = projections.loc[year, 'Software_Revenue'] * software_margins[min(year-1, len(software_margins)-1)]
        energy_oi = projections.loc[year, 'Energy_Revenue'] * energy_margins[min(year-1, len(energy_margins)-1)]
        robotaxi_oi = projections.loc[year, 'Robotaxi_Revenue'] * robotaxi_margins[min(year-1, len(robotaxi_margins)-1)]
        
        # Total operating income
        projections.loc[year, 'Operating_Income'] = ev_oi + software_oi + energy_oi + robotaxi_oi
        
        # Operating margin
        projections.loc[year, 'Operating_Margin'] = projections.loc[year, 'Operating_Income'] / projections.loc[year, 'Total_Revenue']
    
    # 2. Value intangible assets
    # Brand value (royalty relief method)
    royalty_rate = 0.03  # 3% of revenue
    brand_multiple = 10  # Years to capitalize
    brand_value = revenue * royalty_rate * brand_multiple
    
    # Technology/patents value (capitalized R&D)
    rd_history = [4.54e9, 3.97e9, 3.08e9, 2.59e9, 1.49e9]  # Last 5 years R&D
    tech_value = 0
    for i, rd_spend in enumerate(rd_history):
        success_rate = 0.75  # Assume 75% of R&D creates valuable technology
        remaining_life = max(0, 10 - i) / 10  # Assume 10-year useful life, declining linearly
        tech_value += rd_spend * success_rate * remaining_life
    
    # Network effect value (data advantage)
    miles_driven = 25e9  # 25 billion miles
    data_value_per_mile = 0.005  # $0.005 per mile
    network_value = miles_driven * data_value_per_mile
    
    # Leadership premium
    leadership_premium_rate = 0.15  # 15% premium
    leadership_value = brand_value * leadership_premium_rate
    
    # Total intangible value
    intangible_value = brand_value + tech_value + network_value + leadership_value
    
    # 3. Calculate DCF valuation
    # Free cash flow (simplified as Operating Income * (1-tax rate))
    tax_rate = 0.21  # US corporate tax rate
    projections['FCF'] = projections['Operating_Income'] * (1 - tax_rate)
    
    # Calculate present values
    projections['Discount_Factor'] = 1 / ((1 + reasonable_wacc) ** projections.index)
    projections['PV_FCF'] = projections['FCF'] * projections['Discount_Factor']
    
    # Sum present values of explicit forecast period
    pv_explicit_period = projections['PV_FCF'].sum()
    
    # Terminal value calculation
    terminal_growth_rate = 0.04  # 4%
    final_year = projection_years
    terminal_value = projections.loc[final_year, 'FCF'] * (1 + terminal_growth_rate) / (reasonable_wacc - terminal_growth_rate)
    terminal_value_pv = terminal_value * projections.loc[final_year, 'Discount_Factor']
    
    # Enterprise value from DCF
    dcf_enterprise_value = pv_explicit_period + terminal_value_pv
    
    # Add intangible assets value
    total_enterprise_value = dcf_enterprise_value + intangible_value
    
    # Adjust for net cash/debt
    net_cash = cash - total_debt
    equity_value = total_enterprise_value + net_cash
    
    # Value per share
    growth_value_per_share = equity_value / shares_outstanding
    
    # Get market price
    market_price = None
    if info_path and os.path.exists(info_path):
        with open(info_path, 'r') as f:
            info = json.load(f)
            market_price = info.get('regularMarketPrice')
    
    # Compile results
    results = {
        'Book_Value': common_equity,
        'Book_Value_Per_Share': common_equity / shares_outstanding,
        'DCF_Enterprise_Value': dcf_enterprise_value,
        'PV_Explicit_Period': pv_explicit_period,
        'PV_Terminal_Value': terminal_value_pv,
        'Intangible_Value': intangible_value,
        'Brand_Value': brand_value,
        'Technology_Value': tech_value,
        'Network_Value': network_value,
        'Leadership_Value': leadership_value,
        'Total_Enterprise_Value': total_enterprise_value,
        'Net_Cash': net_cash,
        'Equity_Value': equity_value,
        'Shares_Outstanding': shares_outstanding,
        'Growth_Value_Per_Share': growth_value_per_share,
        'Market_Price': market_price
    }
    
    # Save projections
    projections.to_csv('TSLA_growth_projections.csv')
    
    # Return both results and projections
    return results, projections

def plot_valuation_comparison(traditional_results, growth_results, market_price=None):
    """
    Create a comparison chart showing both valuation approaches side by side
    
    Parameters:
    traditional_results (DataFrame): Results from residual earnings model
    growth_results (dict): Results from growth-based model
    market_price (float): Current market price per share
    """
    # Format numbers as billions
    def billions(x, pos):
        return f'${x/1e9:.1f}B'
    
    # Get relevant values from traditional approach
    most_recent = traditional_results.columns[0]
    second_most_recent = traditional_results.columns[1] if len(traditional_results.columns) > 1 else most_recent
    
    # Choose a column with valid residual earnings (usually second most recent)
    re_column = second_most_recent if pd.isna(traditional_results.loc['8. Residual Earnings (OI - Capital Charge)', most_recent]) else most_recent
    
    trad_book_value = traditional_results.loc['10. Book Value of Common Equity', re_column]
    trad_pv_re = traditional_results.loc['11. Present Value of RE (RE ÷ WACC)', re_column]
    trad_total_value = traditional_results.loc['12. Intrinsic Equity Value (10 + 11)', re_column]
    trad_per_share = traditional_results.loc['13. Value per Share', re_column]
    trad_wacc = traditional_results.loc['3. WACC', re_column]
    
    # Extract growth model values
    growth_book_value = growth_results['Book_Value']
    growth_dcf_explicit = growth_results['PV_Explicit_Period']
    growth_dcf_terminal = growth_results['PV_Terminal_Value']
    growth_intangibles = growth_results['Intangible_Value']
    growth_net_cash = growth_results['Net_Cash']
    growth_total_value = growth_results['Equity_Value']
    growth_per_share = growth_results['Growth_Value_Per_Share']
    
    shares_outstanding = growth_results['Shares_Outstanding']
    
    # Get market capitalization if market price is available
    market_cap = market_price * shares_outstanding if market_price else None
    
    # Create comparison chart - Per Share Values
    plt.figure(figsize=(12, 8))
    
    # Data for the bar chart
    labels = ['Traditional RE\nValuation\n(WACC: {:.2%})'.format(trad_wacc), 
              'Growth-Based\nValuation\n(WACC: 12.00%)']
    values = [trad_per_share, growth_per_share]
    colors = ['blue', 'green']
    
    # Create bars
    bars = plt.bar(labels, values, color=colors, width=0.5, alpha=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 5,
                 f'${height:.2f}', ha='center', va='bottom', fontweight='bold')
    
    # Add horizontal line for market price if available
    if market_price:
        plt.axhline(y=market_price, color='red', linestyle='--', linewidth=2)
        plt.text(0, market_price + 10, f'Current Market Price: ${market_price:.2f}', 
                 color='red', fontweight='bold')
    
    # Chart formatting
    plt.title('Tesla Valuation Comparison - Value Per Share', fontsize=16)
    plt.ylabel('Value Per Share ($)', fontsize=14)
    plt.ylim(0, max(max(values) * 1.2, market_price * 1.2 if market_price else max(values) * 1.2))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save chart
    plt.tight_layout()
    plt.savefig('TSLA_valuation_comparison_per_share.png')
    plt.close()
    
    # Create comparison chart - Value Components
    plt.figure(figsize=(14, 10))
    
    # Data for stacked bar chart
    traditional_components = [
        ('Book Value', trad_book_value),
        ('PV of Residual Earnings', trad_pv_re)
    ]
    
    growth_components = [
        ('Book Value', growth_book_value),
        ('DCF (Explicit Period)', growth_dcf_explicit),
        ('DCF (Terminal Value)', growth_dcf_terminal),
        ('Intangible Assets', growth_intangibles),
        ('Net Cash', growth_net_cash)
    ]
    
    # Create positions for bars
    bar_width = 0.35
    positions = [0, 1]
    
    # Plot traditional valuation components
    bottom = 0
    for i, (name, value) in enumerate(traditional_components):
        plt.bar(positions[0], value, bar_width, bottom=bottom, label=f'Traditional: {name}' if i == 0 else f'_{name}',
                color=f'C{i}', alpha=0.7)
        # Add text label if segment is large enough
        if value > trad_total_value * 0.05:  # Only label if > 5% of total
            plt.text(positions[0], bottom + value/2, f'{name}\n${value/1e9:.1f}B', 
                    ha='center', va='center', fontweight='bold')
        bottom += value
    
    # Plot growth valuation components
    bottom = 0
    for i, (name, value) in enumerate(growth_components):
        plt.bar(positions[1], value, bar_width, bottom=bottom, label=f'Growth: {name}' if i == 0 else f'_{name}',
                color=f'C{i+2}', alpha=0.7)
        # Add text label if segment is large enough
        if value > growth_total_value * 0.05:  # Only label if > 5% of total
            plt.text(positions[1], bottom + value/2, f'{name}\n${value/1e9:.1f}B', 
                    ha='center', va='center', fontweight='bold')
        bottom += value
    
    # Add market cap line if available
    if market_cap:
        plt.axhline(y=market_cap, color='red', linestyle='--', linewidth=2)
        plt.text(0.5, market_cap, f'Market Cap: ${market_cap/1e9:.1f}B', 
                ha='center', va='bottom', color='red', fontweight='bold')
    
    # Chart formatting
    plt.xticks(positions, labels)
    plt.ylabel('Value ($B)', fontsize=14)
    plt.title('Tesla Valuation Comparison - Value Components', fontsize=16)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(billions))
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add total values at the top of each bar
    plt.text(positions[0], trad_total_value, f'Total: ${trad_total_value/1e9:.1f}B', 
             ha='center', va='bottom', fontweight='bold')
    plt.text(positions[1], growth_total_value, f'Total: ${growth_total_value/1e9:.1f}B', 
             ha='center', va='bottom', fontweight='bold')
    
    # Handle legend - combine similar labels
    handles, labels = plt.gca().get_legend_handles_labels()
    filtered_handles = []
    filtered_labels = []
    for handle, label in zip(handles, labels):
        if not label.startswith('_'):
            filtered_handles.append(handle)
            filtered_labels.append(label)
    
    plt.legend(filtered_handles, filtered_labels, loc='upper right')
    
    # Save chart
    plt.tight_layout()
    plt.savefig('TSLA_valuation_comparison_components.png')
    plt.close()

def explain_valuation_difference(traditional_results, growth_results, file_path='TSLA_valuation_difference_explanation.txt'):
    """
    Create a text file explaining the differences between the two valuation approaches
    
    Parameters:
    traditional_results (DataFrame): Results from residual earnings model
    growth_results (dict): Results from growth-based model
    file_path (str): Path to save the explanation
    """
    most_recent = traditional_results.columns[0]
    second_most_recent = traditional_results.columns[1] if len(traditional_results.columns) > 1 else most_recent
    
    # Choose a column with valid residual earnings (usually second most recent)
    re_column = second_most_recent if pd.isna(traditional_results.loc['8. Residual Earnings (OI - Capital Charge)', most_recent]) else most_recent
    
    trad_per_share = traditional_results.loc['13. Value per Share', re_column]
    trad_wacc = traditional_results.loc['3. WACC', re_column]
    trad_rnoa = traditional_results.loc['18. Return on Net Operating Assets (RNOA)', re_column]
    
    # Extract growth model values
    growth_per_share = growth_results['Growth_Value_Per_Share']
    
    # Calculate difference
    difference = growth_per_share - trad_per_share
    percentage_diff = (difference / trad_per_share) * 100
    
    with open(file_path, 'w') as f:
        f.write("# TESLA VALUATION COMPARISON: TRADITIONAL VS. GROWTH-BASED APPROACH\n\n")
        
        f.write("## Summary of Valuation Results\n")
        f.write(f"Traditional Residual Earnings Valuation: ${trad_per_share:.2f} per share\n")
        f.write(f"Growth-Based DCF Valuation: ${growth_per_share:.2f} per share\n")
        f.write(f"Difference: ${difference:.2f} per share ({percentage_diff:.1f}% higher)\n\n")
        
        f.write("## Main Factors Explaining the Difference\n\n")
        
        f.write("### 1. Discount Rate (WACC)\n")
        f.write(f"* Traditional approach uses a high WACC of {trad_wacc:.2%}\n")
        f.write("* Growth-based approach uses a more reasonable WACC of 12.00%\n")
        f.write("* Lower WACC significantly increases present value of future cash flows\n\n")
        
        f.write("### 2. Future Growth Projections\n")
        f.write("* Traditional approach only uses historical residual earnings\n")
        f.write("* Growth-based approach explicitly models future revenue growth:\n")
        f.write("  - EV revenue: 25% → 5% growth over 10 years\n")
        f.write("  - Software/FSD: 40% → 10% growth over 10 years\n")
        f.write("  - Energy storage: 45% → 10% growth over 10 years\n")
        f.write("  - Robotaxi: New revenue stream starting in year 3\n\n")
        
        f.write("### 3. Improving Profit Margins\n")
        f.write(f"* Traditional approach uses historical operating margin ({trad_rnoa:.2%} RNOA)\n")
        f.write("* Growth-based approach models improving margins by segment:\n")
        f.write("  - EV margins: 8% → 15%\n")
        f.write("  - Software margins: 70% → 80%\n")
        f.write("  - Energy margins: 12% → 25%\n")
        f.write("  - Robotaxi margins: 50% → 75%\n\n")
        
        f.write("### 4. Intangible Assets Valuation\n")
        f.write("* Traditional approach ignores intangible assets\n")
        f.write("* Growth-based approach quantifies intangible value:\n")
        f.write(f"  - Brand value: ${growth_results['Brand_Value']/1e9:.1f}B\n")
        f.write(f"  - Technology/patents: ${growth_results['Technology_Value']/1e9:.1f}B\n")
        f.write(f"  - Network effects: ${growth_results['Network_Value']/1e9:.1f}B\n")
        f.write(f"  - Leadership premium: ${growth_results['Leadership_Value']/1e9:.1f}B\n\n")
        
        f.write("### 5. Terminal Value Calculation\n")
        f.write("* Traditional approach has no explicit terminal value\n")
        f.write("* Growth-based approach uses Gordon Growth Model with 4% terminal growth rate\n")
        f.write(f"* Terminal value accounts for ${growth_results['PV_Terminal_Value']/1e9:.1f}B of total value\n\n")
        
        f.write("## Conclusion\n")
        f.write("The significant difference between the two valuations demonstrates how accounting-based\n")
        f.write("valuation methods (like residual earnings) tend to undervalue high-growth, intangible-rich\n")
        f.write("companies like Tesla. The growth-based approach better reflects Tesla's future potential by:\n\n")
        f.write("1. Using a more appropriate discount rate\n")
        f.write("2. Explicitly modeling future growth across multiple segments\n")
        f.write("3. Accounting for improving margins from scale and product mix shift\n")
        f.write("4. Valuing Tesla's significant intangible assets\n")
        f.write("5. Including terminal value that captures long-term growth potential\n\n")
        
        f.write("This explains why Tesla's market valuation is much closer to the growth-based approach\n")
        f.write("than the traditional residual earnings valuation.\n")

# Run both valuation approaches and compare them
def compare_valuation_approaches():
    try:
        # File paths
        bs_path = 'TSLA_reconciled_balance_sheet.csv'
        is_path = 'TSLA_reconciled_income_statement.csv'
        info_path = 'TSLA_info.json'
        
        # Get market price if available
        market_price = None
        if os.path.exists(info_path):
            with open(info_path, 'r') as f:
                info = json.load(f)
                market_price = info.get('regularMarketPrice')
        
        # Run traditional residual earnings valuation
        print("Running traditional residual earnings valuation...")
        traditional_wacc = 0.2774  # 27.74%
        traditional_results = calculate_residual_earnings_valuation(bs_path, is_path, traditional_wacc, info_path)
        
        # Run growth-based valuation with more reasonable WACC
        print("Running growth-based valuation...")
        growth_wacc = 0.12  # 12%
        growth_results, projections = comprehensive_tesla_valuation(bs_path, is_path, growth_wacc, info_path)
        
        # Create comparison visualizations
        print("Creating comparison charts...")
        plot_valuation_comparison(traditional_results, growth_results, market_price)
        
        # Generate explanation of differences
        print("Generating explanation of valuation differences...")
        explain_valuation_difference(traditional_results, growth_results)
        
        # Print summary of comparison
        most_recent = traditional_results.columns[0]
        second_most_recent = traditional_results.columns[1] if len(traditional_results.columns) > 1 else most_recent
        
        # Choose a column with valid residual earnings (usually second most recent)
        re_column = second_most_recent if pd.isna(traditional_results.loc['8. Residual Earnings (OI - Capital Charge)', most_recent]) else most_recent
        
        trad_per_share = traditional_results.loc['13. Value per Share', re_column]
        growth_per_share = growth_results['Growth_Value_Per_Share']
        
        print("\n=== TESLA VALUATION COMPARISON ===")
        print(f"Traditional Approach (WACC: {traditional_wacc:.2%}): ${trad_per_share:.2f} per share")
        print(f"Growth-Based Approach (WACC: {growth_wacc:.2%}): ${growth_per_share:.2f} per share")
        
        difference = growth_per_share - trad_per_share
        percentage_diff = (difference / trad_per_share) * 100
        print(f"Difference: ${difference:.2f} per share ({percentage_diff:.1f}% higher)")
        
        if market_price:
            trad_ratio = market_price / trad_per_share
            growth_ratio = market_price / growth_per_share
            
            print(f"\nCurrent Market Price: ${market_price:.2f}")
            print(f"Market Price / Traditional Value: {trad_ratio:.2f}x")
            print(f"Market Price / Growth-Based Value: {growth_ratio:.2f}x")
            
            if growth_ratio > 1.2:
                conclusion = "OVERVALUED"
            elif growth_ratio < 0.8:
                conclusion = "UNDERVALUED"
            else:
                conclusion = "FAIRLY VALUED"
                
            print(f"Tesla appears to be {conclusion} even using the growth-based approach")
        
        print("\nDetailed comparison saved to:")
        print("- TSLA_valuation_comparison_per_share.png")
        print("- TSLA_valuation_comparison_components.png")
        print("- TSLA_valuation_difference_explanation.txt")
        
    except Exception as e:
        print(f"Error in comparison: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_valuation_approaches() 