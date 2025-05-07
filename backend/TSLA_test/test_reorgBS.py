import pandas as pd
import numpy as np

def reconcile_tesla_balance_sheet(csv_path):
    """
    Reconciles Tesla's balance sheet into operating vs non-operating categories
    
    Parameters:
    csv_path (str): Path to Tesla balance sheet CSV file
    
    Returns:
    DataFrame: Reorganized consolidated balance sheet
    """
    # Load data
    bs = pd.read_csv(csv_path, index_col=0)
    
    # Fill NaN values with 0 to prevent propagation of NaN
    bs = bs.fillna(0)
    
    # Create new consolidated format
    consolidated = pd.DataFrame(index=[
        'A. OPERATING ASSETS',
        '1. Property, Plant & Equipment (Net)',
        '2. Inventory',
        '  - Raw Materials',
        '  - Work In Process',
        '  - Finished Goods',
        '  - Other Inventories',
        '3. Accounts Receivable',
        '4. Other Operating Assets',
        '5. TOTAL OPERATING ASSETS',
        '',
        'B. OPERATING LIABILITIES',
        '6. Accounts Payable',
        '7. Accrued Expenses',
        '8. Operating Provisions',
        '9. Deferred Revenue (Current)',
        '10. Other Operating Liabilities',
        '11. TOTAL OPERATING LIABILITIES',
        '',
        'C. NET OPERATING ASSETS (5-11)',
        '',
        'D. NON-OPERATING ASSETS',
        '12. Cash and Cash Equivalents',
        '13. Short-term Investments',
        '14. Goodwill and Intangibles',
        '15. Tax Assets',
        '16. Construction in Progress',
        '17. Other Non-Operating Assets',
        '18. Unclassified Assets (Balancing)',
        '19. TOTAL NON-OPERATING ASSETS',
        '',
        'E. NON-OPERATING LIABILITIES',
        '20. Long-term Debt',
        '21. Current Debt',
        '22. Capital Lease Obligations',
        '23. Deferred Revenue (Non-Current)',
        '24. Deferred Tax Liabilities',
        '25. Non-Current Accrued Expenses',
        '26. Other Non-Operating Liabilities',
        '27. TOTAL NON-OPERATING LIABILITIES',
        '',
        'F. NET NON-OPERATING ASSETS (19-27)',
        '',
        'G. TOTAL NET ASSETS (C+F)',
        '',
        'H. EQUITY',
        '28. Common Stock',
        '29. Additional Paid-In Capital',
        '30. Retained Earnings',
        '31. Other Equity Adjustments',
        '32. Minority Interest',
        '33. TOTAL EQUITY',
        '',
        'I. RECONCILIATION',
        '34. Total Net Assets',
        '35. Total Equity',
        '36. Difference (should be near zero)',
        '37. Original BS Assets',
        '38. Original BS Liabilities + Equity',
        '39. Original BS Difference'
    ], columns=bs.columns)
    
    # Fill in operating assets
    # Remove Construction in Progress from PPE
    construction_in_progress = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Construction In Progress' in bs.index:
        construction_in_progress = bs.loc['Construction In Progress'].fillna(0)
    
    consolidated.loc['1. Property, Plant & Equipment (Net)'] = bs.loc['Net PPE'] - construction_in_progress
    
    # Inventory breakdown
    consolidated.loc['  - Raw Materials'] = bs.loc['Raw Materials']
    consolidated.loc['  - Work In Process'] = bs.loc['Work In Process']
    consolidated.loc['  - Finished Goods'] = bs.loc['Finished Goods']
    consolidated.loc['  - Other Inventories'] = bs.loc['Other Inventories']
    consolidated.loc['2. Inventory'] = bs.loc['Inventory']
    
    consolidated.loc['3. Accounts Receivable'] = bs.loc['Accounts Receivable']
    
    # Other operating assets (prepaid + other current that aren't financial)
    other_op_assets = bs.loc['Other Current Assets']
    if 'Prepaid Assets' in bs.index:
        other_op_assets = bs.loc['Prepaid Assets']
    consolidated.loc['4. Other Operating Assets'] = other_op_assets
    
    # Calculate total operating assets
    total_op_assets = (
        consolidated.loc['1. Property, Plant & Equipment (Net)'] + 
        bs.loc['Inventory'] + 
        bs.loc['Accounts Receivable'] + 
        other_op_assets
    )
    consolidated.loc['5. TOTAL OPERATING ASSETS'] = total_op_assets
    
    # Fill in operating liabilities
    consolidated.loc['6. Accounts Payable'] = bs.loc['Accounts Payable']
    consolidated.loc['7. Accrued Expenses'] = bs.loc['Current Accrued Expenses']
    consolidated.loc['8. Operating Provisions'] = bs.loc['Current Provisions']
    consolidated.loc['9. Deferred Revenue (Current)'] = bs.loc['Current Deferred Revenue']
    
    # Other operating liabilities
    if 'Other Current Liabilities' in bs.index:
        other_op_liab = bs.loc['Other Current Liabilities']
    else:
        other_op_liab = pd.Series([0] * len(bs.columns), index=bs.columns)
    consolidated.loc['10. Other Operating Liabilities'] = other_op_liab
    
    # Calculate total operating liabilities
    total_op_liab = (
        bs.loc['Accounts Payable'] + 
        bs.loc['Current Accrued Expenses'] + 
        bs.loc['Current Provisions'] + 
        bs.loc['Current Deferred Revenue'] + 
        other_op_liab
    )
    consolidated.loc['11. TOTAL OPERATING LIABILITIES'] = total_op_liab
    
    # Calculate net operating assets
    net_op_assets = total_op_assets - total_op_liab
    consolidated.loc['C. NET OPERATING ASSETS (5-11)'] = net_op_assets
    
    # Fill in non-operating assets
    consolidated.loc['12. Cash and Cash Equivalents'] = bs.loc['Cash And Cash Equivalents']
    consolidated.loc['13. Short-term Investments'] = bs.loc['Other Short Term Investments']
    consolidated.loc['14. Goodwill and Intangibles'] = bs.loc['Goodwill And Other Intangible Assets']
    
    # Tax assets
    tax_assets = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Non Current Deferred Taxes Assets' in bs.index:
        tax_assets = bs.loc['Non Current Deferred Taxes Assets'].fillna(0)
    consolidated.loc['15. Tax Assets'] = tax_assets
    
    # Construction in Progress - separate from PPE
    consolidated.loc['16. Construction in Progress'] = construction_in_progress
    
    # Other non-operating assets
    other_non_op_assets = bs.loc['Other Non Current Assets'].fillna(0)
    consolidated.loc['17. Other Non-Operating Assets'] = other_non_op_assets
    
    # Calculate initial non-operating assets total (before balancing)
    initial_non_op_assets = (
        bs.loc['Cash And Cash Equivalents'] + 
        bs.loc['Other Short Term Investments'] + 
        bs.loc['Goodwill And Other Intangible Assets'] +
        tax_assets +
        construction_in_progress +
        other_non_op_assets
    )
    
    # Fill in non-operating liabilities
    consolidated.loc['20. Long-term Debt'] = bs.loc['Long Term Debt']
    consolidated.loc['21. Current Debt'] = bs.loc['Current Debt']
    
    # Capital lease obligations - handle safely
    ltcl = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Long Term Capital Lease Obligation' in bs.index:
        ltcl = bs.loc['Long Term Capital Lease Obligation'].fillna(0)
        
    ccl = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Current Capital Lease Obligation' in bs.index:
        ccl = bs.loc['Current Capital Lease Obligation'].fillna(0)
        
    consolidated.loc['22. Capital Lease Obligations'] = ltcl + ccl
    
    # Add Non-Current Deferred Revenue separately
    non_current_deferred_revenue = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Non Current Deferred Revenue' in bs.index:
        non_current_deferred_revenue = bs.loc['Non Current Deferred Revenue'].fillna(0)
    consolidated.loc['23. Deferred Revenue (Non-Current)'] = non_current_deferred_revenue
    
    # Tax liabilities
    tax_liab = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Non Current Deferred Taxes Liabilities' in bs.index:
        tax_liab = bs.loc['Non Current Deferred Taxes Liabilities'].fillna(0)
    consolidated.loc['24. Deferred Tax Liabilities'] = tax_liab
    
    # Non-Current Accrued Expenses
    non_current_accrued = pd.Series([0] * len(bs.columns), index=bs.columns)
    if 'Non Current Accrued Expenses' in bs.index:
        non_current_accrued = bs.loc['Non Current Accrued Expenses'].fillna(0)
    consolidated.loc['25. Non-Current Accrued Expenses'] = non_current_accrued
    
    # Other non-operating liabilities (long-term provisions + other non-current)
    other_non_op_liab = bs.loc['Long Term Provisions'].fillna(0)
    if 'Other Non Current Liabilities' in bs.index:
        other_non_op_liab += bs.loc['Other Non Current Liabilities'].fillna(0)
    
    # Add other non-current deferred liabilities if present
    if 'Non Current Deferred Liabilities' in bs.index and 'Non Current Deferred Revenue' in bs.index:
        # Don't double count revenue
        other_deferred_liab = (bs.loc['Non Current Deferred Liabilities'] - bs.loc['Non Current Deferred Revenue']).fillna(0)
        other_non_op_liab += other_deferred_liab
    
    consolidated.loc['26. Other Non-Operating Liabilities'] = other_non_op_liab
    
    # Calculate total non-operating liabilities
    total_non_op_liab = (
        bs.loc['Long Term Debt'] + 
        bs.loc['Current Debt'] + 
        consolidated.loc['22. Capital Lease Obligations'] +
        non_current_deferred_revenue +
        tax_liab +
        non_current_accrued +
        other_non_op_liab
    )
    consolidated.loc['27. TOTAL NON-OPERATING LIABILITIES'] = total_non_op_liab
    
    # Get total equity
    total_equity = bs.loc['Total Equity Gross Minority Interest']
    
    # Calculate unclassified assets to balance the equation
    # Assets = Liabilities + Equity
    # So: Total Assets = Total Liabilities + Total Equity
    #     Total Operating Assets + Total Non-Operating Assets = Total Operating Liabilities + Total Non-Operating Liabilities + Total Equity
    #     Total Non-Operating Assets = Total Operating Liabilities + Total Non-Operating Liabilities + Total Equity - Total Operating Assets
    
    required_total_assets = total_op_liab + total_non_op_liab + total_equity
    unclassified_assets = required_total_assets - total_op_assets - initial_non_op_assets
    consolidated.loc['18. Unclassified Assets (Balancing)'] = unclassified_assets
    
    # Calculate total non-operating assets including unclassified
    total_non_op_assets = initial_non_op_assets + unclassified_assets
    consolidated.loc['19. TOTAL NON-OPERATING ASSETS'] = total_non_op_assets
    
    # Calculate net non-operating assets
    net_non_op_assets = total_non_op_assets - total_non_op_liab
    consolidated.loc['F. NET NON-OPERATING ASSETS (19-27)'] = net_non_op_assets
    
    # Debug NaN values
    print("Checking for NaN values in key components:")
    print(f"Net Operating Assets: {net_op_assets.isnull().sum()} NaN values")
    print(f"Net Non-Operating Assets: {net_non_op_assets.isnull().sum()} NaN values")
    
    # Ensure no NaN values in components before final calculation
    net_op_assets = net_op_assets.fillna(0)
    net_non_op_assets = net_non_op_assets.fillna(0)
    
    # Calculate total net assets
    total_net_assets = net_op_assets + net_non_op_assets
    consolidated.loc['G. TOTAL NET ASSETS (C+F)'] = total_net_assets
    
    # Fill in equity
    consolidated.loc['28. Common Stock'] = bs.loc['Common Stock']
    consolidated.loc['29. Additional Paid-In Capital'] = bs.loc['Additional Paid In Capital']
    consolidated.loc['30. Retained Earnings'] = bs.loc['Retained Earnings']
    consolidated.loc['31. Other Equity Adjustments'] = bs.loc['Other Equity Adjustments']
    consolidated.loc['32. Minority Interest'] = bs.loc['Minority Interest']
    
    # Calculate total equity
    consolidated.loc['33. TOTAL EQUITY'] = total_equity
    
    # Print components for verification
    print("\nKey Components:")
    print(f"Total Operating Assets: {total_op_assets.iloc[0]:,.0f}")
    print(f"Total Operating Liabilities: {total_op_liab.iloc[0]:,.0f}")
    print(f"Net Operating Assets: {net_op_assets.iloc[0]:,.0f}")
    print(f"Initial Non-Operating Assets: {initial_non_op_assets.iloc[0]:,.0f}")
    print(f"Unclassified Assets: {unclassified_assets.iloc[0]:,.0f}")
    print(f"Total Non-Operating Assets: {total_non_op_assets.iloc[0]:,.0f}")
    print(f"Total Non-Operating Liabilities: {total_non_op_liab.iloc[0]:,.0f}")
    print(f"Net Non-Operating Assets: {net_non_op_assets.iloc[0]:,.0f}")
    print(f"Total Net Assets: {total_net_assets.iloc[0]:,.0f}")
    print(f"Total Equity: {total_equity.iloc[0]:,.0f}")
    
    # Completeness check
    print("\nCompleteness Check:")
    total_assets_original = bs.loc['Total Assets']
    total_liab_equity_original = bs.loc['Total Liabilities Net Minority Interest'] + bs.loc['Total Equity Gross Minority Interest']
    diff_original = total_assets_original - total_liab_equity_original
    
    print(f"Original BS Total Assets: {total_assets_original.iloc[0]:,.0f}")
    print(f"Original BS Total Liabilities + Equity: {total_liab_equity_original.iloc[0]:,.0f}")
    print(f"Original BS Difference: {diff_original.iloc[0]:,.0f}")
    
    # Reconciliation
    consolidated.loc['34. Total Net Assets'] = total_net_assets
    consolidated.loc['35. Total Equity'] = total_equity
    consolidated.loc['36. Difference (should be near zero)'] = total_net_assets - total_equity
    consolidated.loc['37. Original BS Assets'] = total_assets_original
    consolidated.loc['38. Original BS Liabilities + Equity'] = total_liab_equity_original
    consolidated.loc['39. Original BS Difference'] = diff_original
    
    print(f"\nReconciliation: Total Net Assets: {total_net_assets.iloc[0]:,.0f}, Total Equity: {total_equity.iloc[0]:,.0f}")
    print(f"Difference: {(total_net_assets - total_equity).iloc[0]:,.0f}")
    
    # Format with section headers
    for section in ['A. OPERATING ASSETS', 'B. OPERATING LIABILITIES', 'D. NON-OPERATING ASSETS', 
                   'E. NON-OPERATING LIABILITIES', 'H. EQUITY', 'I. RECONCILIATION']:
        consolidated.loc[section] = '***' + section + '***'
    
    # Save reconciled statement
    consolidated.to_csv('TSLA_reconciled_balance_sheet.csv')
    
    return consolidated

# Usage
tesla_bs = reconcile_tesla_balance_sheet('TSLA_balance_sheet.csv')
print("Reconciled Balance Sheet saved to TSLA_reconciled_balance_sheet.csv")