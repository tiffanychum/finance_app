"use client";

import { useState, useEffect } from 'react';
import { formatNumber, formatPercent } from '../utils/formatters';

interface RestructuredFinancialsProps {
  ticker: string;
}

interface StructuredData {
  operating_income: any;
  financial_expense: any;
  operating_assets: any;
  operating_liabilities: any;
  financial_assets: any;
  financial_obligations: any;
  summary: {
    net_operating_assets: number;
    net_financial_obligations: number;
    common_equity: number;
    accounting_check: any;
  };
}

export default function RestructuredFinancials({ ticker }: RestructuredFinancialsProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<StructuredData | null>(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const apiBaseUrl = 'http://localhost:8000';
        const response = await fetch(`${apiBaseUrl}/restructured-financials/${ticker}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch restructured financials: ${await response.text()}`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching restructured financials:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [ticker]);
  
  if (loading) return <div className="my-4 text-center">Loading restructured financial data...</div>;
  if (error) return <div className="my-4 text-center text-red-600">Error: {error}</div>;
  if (!data) return <div className="my-4 text-center">No restructured financial data available</div>;
  
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Restructured Financial Statements</h3>
        <p className="mb-4 text-sm text-gray-600">
          Following fundamental analysis principles, we separate operating activities from financing activities
          to better understand the sources of company performance.
        </p>
        
        {/* Summary Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 border rounded-lg bg-blue-50">
            <p className="text-sm text-gray-500">Net Operating Assets (NOA)</p>
            <p className="text-xl font-semibold">${formatNumber(data.summary.net_operating_assets)}</p>
          </div>
          <div className="p-4 border rounded-lg bg-red-50">
            <p className="text-sm text-gray-500">Net Financial Obligations (NFO)</p>
            <p className="text-xl font-semibold">${formatNumber(data.summary.net_financial_obligations)}</p>
          </div>
          <div className="p-4 border rounded-lg bg-green-50">
            <p className="text-sm text-gray-500">Common Equity (CSE)</p>
            <p className="text-xl font-semibold">${formatNumber(data.summary.common_equity)}</p>
          </div>
        </div>
        
        {/* Accounting Equation Check */}
        <div className="p-4 border rounded-lg bg-gray-50 mb-6">
          <p className="text-sm font-medium">Accounting Equation: NOA = NFO + CSE</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-2">
            <div>
              <p className="text-sm text-gray-500">NOA</p>
              <p className="font-medium">${formatNumber(data.summary.net_operating_assets)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">NFO + CSE</p>
              <p className="font-medium">${formatNumber(data.summary.accounting_check.nfo_plus_cse)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Difference</p>
              <p className="font-medium">${formatNumber(data.summary.accounting_check.difference)}</p>
            </div>
          </div>
        </div>
        
        {/* Tab System for Details */}
        <div className="mb-4">
          <ul className="flex flex-wrap -mb-px border-b">
            <li className="mr-2">
              <button 
                onClick={() => document.getElementById('income-statement')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-block p-3 text-blue-600 hover:text-blue-800 border-b-2 border-blue-600 focus:outline-none"
              >
                Income Statement
              </button>
            </li>
            <li className="mr-2">
              <button 
                onClick={() => document.getElementById('balance-sheet')?.scrollIntoView({ behavior: 'smooth' })}
                className="inline-block p-3 text-blue-600 hover:text-blue-800 border-b border-transparent hover:border-blue-300 focus:outline-none"
              >
                Balance Sheet
              </button>
            </li>
          </ul>
        </div>
        
        {/* Restructured Income Statement */}
        <div id="income-statement" className="mb-6">
          <h4 className="text-lg font-medium mb-4">Restructured Income Statement</h4>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-50">
                    Operating Activities
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Sales Revenue</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_income.sales_revenue)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Cost of Sales</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.operating_income.cost_of_sales)})
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Gross Margin</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">${formatNumber(data.operating_income.gross_margin)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Research & Development</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.operating_income.research_development)})
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Selling, General & Admin</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.operating_income.selling_general_admin)})
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Core Operating Income (Before Tax)</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">${formatNumber(data.operating_income.core_oi_before_tax)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Tax on Operating Income</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.operating_income.tax_on_oi)})
                  </td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Core Operating Income (After Tax)</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">${formatNumber(data.operating_income.core_oi_after_tax)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Other Operating Items</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.operating_income.other_oi)})
                  </td>
                </tr>
                <tr className="bg-blue-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Comprehensive Operating Income</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.operating_income.comprehensive_oi)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-red-50">
                    Financing Activities
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Interest Expense</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm text-red-600">
                    (${formatNumber(data.financial_expense.interest_expense)})
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Interest Income</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_expense.interest_income)}</td>
                </tr>
                <tr className="bg-gray-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Net Interest Expense</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">
                    (${formatNumber(data.financial_expense.net_interest_expense)})
                  </td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Tax Benefit</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_expense.tax_benefit)}</td>
                </tr>
                <tr className="bg-red-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">After-tax Net Financial Expense</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">
                    (${formatNumber(data.financial_expense.after_tax_nfe)})
                  </td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-green-50">
                    Net Income
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr className="bg-green-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">
                    Comprehensive Income (OI - NFE)
                  </td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">
                    ${formatNumber(data.operating_income.comprehensive_oi - data.financial_expense.after_tax_nfe)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        
        {/* Restructured Balance Sheet */}
        <div id="balance-sheet" className="mb-6">
          <h4 className="text-lg font-medium mb-4">Restructured Balance Sheet</h4>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-50">
                    Operating Assets
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Cash (Operating)</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.cash_and_equivalents)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Accounts Receivable</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.accounts_receivable)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Inventory</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.inventory)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Other Current Assets</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.other_current_assets)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Property, Plant & Equipment</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.ppe_net)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Intangible Assets</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_assets.intangible_assets)}</td>
                </tr>
                <tr className="bg-blue-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Total Operating Assets</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.operating_assets.total_operating_assets)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-100">
                    Operating Liabilities
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Accounts Payable</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_liabilities.accounts_payable)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Accrued Liabilities</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_liabilities.accrued_liabilities)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Deferred Revenue</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_liabilities.deferred_revenue)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Deferred Tax Liabilities</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.operating_liabilities.deferred_tax_liabilities)}</td>
                </tr>
                <tr className="bg-blue-100">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Total Operating Liabilities</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.operating_liabilities.total_operating_liabilities)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-blue-200">
                    Net Operating Assets (NOA)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr className="bg-blue-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Net Operating Assets</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.summary.net_operating_assets)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-red-50">
                    Financial Assets
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Excess Cash</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_assets.excess_cash)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Long-term Investments</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_assets.long_term_investments)}</td>
                </tr>
                <tr className="bg-red-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Total Financial Assets</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.financial_assets.total_financial_assets)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-red-100">
                    Financial Obligations
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Short-term Debt</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_obligations.short_term_debt)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Long-term Debt</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_obligations.long_term_debt)}</td>
                </tr>
                <tr>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Other Financial Liabilities</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.financial_obligations.other_liabilities)}</td>
                </tr>
                <tr className="bg-red-100">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Total Financial Obligations</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.financial_obligations.total_financial_obligations)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-red-200">
                    Net Financial Obligations (NFO)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr className="bg-red-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Net Financial Obligations</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.summary.net_financial_obligations)}</td>
                </tr>
              </tbody>
              
              <thead className="bg-gray-50">
                <tr>
                  <th colSpan={2} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider bg-green-50">
                    Common Shareholders' Equity (CSE)
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                <tr className="bg-green-50">
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">Common Shareholders' Equity</td>
                  <td className="px-6 py-2 whitespace-nowrap text-sm font-bold">${formatNumber(data.summary.common_equity)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
} 