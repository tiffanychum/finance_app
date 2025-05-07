import pandas as pd

def reconcile_tesla_income_statement(csv_path):
    """
    Reconciles Tesla's income statement into a clear operating vs non-operating format
    
    Parameters:
    csv_path (str): Path to Tesla financials CSV file
    
    Returns:
    DataFrame: Reorganized consolidated income statement
    """
    # Load data
    df = pd.read_csv(csv_path, index_col=0)
    
    # Create new consolidated format
    consolidated = pd.DataFrame(index=[
        'A. OPERATING ACTIVITIES',
        '1. Total Revenue',
        '2. Cost of Revenue',
        '3. Gross Profit',
        '4. Research & Development',
        '5. Selling, General & Admin',
        '6. Total Operating Expenses',
        '7. Operating Income (Loss)',
        '',
        'B. NON-OPERATING ACTIVITIES',
        '8. Interest Income',
        '9. Interest Expense',
        '10. Net Interest Income',
        '11. Special Items & Restructuring',
        '12. Other Non-Operating Income',
        '13. Net Non-Operating Income (Loss)',
        '',
        'C. CONSOLIDATED RESULTS',
        '14. Pretax Income',
        '15. Income Tax Provision',
        '16. Effective Tax Rate',
        '17. Net Income',
        '',
        'D. RECONCILIATION CHECK',
        '18. Operating + Non-Operating Income',
        '19. Reported Pretax Income',
        '20. Difference (should be near zero)',
        '21. Net Income After Tax Calculated',
        '22. Reported Net Income',
        '23. Difference (should be near zero)'
    ], columns=df.columns)
    
    # Fill in operating section
    consolidated.loc['1. Total Revenue'] = df.loc['Total Revenue']
    consolidated.loc['2. Cost of Revenue'] = df.loc['Cost Of Revenue']
    consolidated.loc['3. Gross Profit'] = df.loc['Gross Profit']
    consolidated.loc['4. Research & Development'] = df.loc['Research And Development']
    consolidated.loc['5. Selling, General & Admin'] = df.loc['Selling General And Administration']
    consolidated.loc['6. Total Operating Expenses'] = df.loc['Operating Expense']
    consolidated.loc['7. Operating Income (Loss)'] = df.loc['Operating Income']
    
    # Fill in non-operating section
    consolidated.loc['8. Interest Income'] = df.loc['Interest Income Non Operating']
    consolidated.loc['9. Interest Expense'] = df.loc['Interest Expense Non Operating']
    consolidated.loc['10. Net Interest Income'] = df.loc['Net Non Operating Interest Income Expense']
    
    # Special items - combine restructuring and special charges
    special_items = df.loc['Special Income Charges'] + df.loc['Restructuring And Mergern Acquisition']
    consolidated.loc['11. Special Items & Restructuring'] = special_items
    
    consolidated.loc['12. Other Non-Operating Income'] = df.loc['Other Non Operating Income Expenses']
    
    # Calculate net non-operating income
    net_non_operating = (df.loc['Net Non Operating Interest Income Expense'] + 
                         df.loc['Other Non Operating Income Expenses'])
    consolidated.loc['13. Net Non-Operating Income (Loss)'] = net_non_operating
    
    # Fill in consolidated results
    consolidated.loc['14. Pretax Income'] = df.loc['Pretax Income']
    consolidated.loc['15. Income Tax Provision'] = df.loc['Tax Provision']
    
    # Calculate effective tax rate
    effective_tax_rate = df.loc['Tax Provision'] / df.loc['Pretax Income']
    consolidated.loc['16. Effective Tax Rate'] = effective_tax_rate
    
    consolidated.loc['17. Net Income'] = df.loc['Net Income']
    
    # Reconciliation checks
    calculated_pretax = df.loc['Operating Income'] + net_non_operating
    consolidated.loc['18. Operating + Non-Operating Income'] = calculated_pretax
    consolidated.loc['19. Reported Pretax Income'] = df.loc['Pretax Income']
    consolidated.loc['20. Difference (should be near zero)'] = calculated_pretax - df.loc['Pretax Income']
    
    calculated_net_income = df.loc['Pretax Income'] - df.loc['Tax Provision'] + df.loc['Minority Interests']
    consolidated.loc['21. Net Income After Tax Calculated'] = calculated_net_income
    consolidated.loc['22. Reported Net Income'] = df.loc['Net Income']
    consolidated.loc['23. Difference (should be near zero)'] = calculated_net_income - df.loc['Net Income']
    
    # Format with section headers
    for section in ['A. OPERATING ACTIVITIES', 'B. NON-OPERATING ACTIVITIES', 'C. CONSOLIDATED RESULTS', 'D. RECONCILIATION CHECK']:
        # Make section headers bold by adding a marker (can be replaced with actual formatting)
        consolidated.loc[section] = '***' + section + '***'
    
    # Save reconciled statement
    consolidated.to_csv('TSLA_reconciled_income_statement.csv')
    
    return consolidated

# Usage
tesla_is = reconcile_tesla_income_statement('TSLA_financials.csv')
print("Reconciled Income Statement saved to TSLA_reconciled_income_statement.csv")