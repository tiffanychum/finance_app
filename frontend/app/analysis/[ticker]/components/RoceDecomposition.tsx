"use client";

import { useState, useEffect } from 'react';
import { formatNumber, formatPercent, formatRatio } from '../utils/formatters';

interface RoceDecompositionProps {
  ticker: string;
}

interface RoceData {
  roce: number;
  rnoa: number;
  flev: number;
  nbc: number;
  spread: number;
  pm: number;
  ato: number;
  ollev: number;
  components: {
    net_income: number;
    operating_income: number;
    net_financial_expense: number;
    common_equity: number;
    net_operating_assets: number;
    net_financial_obligations: number;
    total_revenue: number;
  };
  checks: {
    roce_check: {
      roce: number;
      calculated_roce: number;
      difference: number;
    };
    rnoa_check: {
      rnoa: number;
      calculated_rnoa: number;
      difference: number;
    };
  };
  cost_of_capital: {
    cost_of_equity: number;
    cost_of_debt: number;
    cost_of_operations: number;
  };
}

export default function RoceDecomposition({ ticker }: RoceDecompositionProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<RoceData | null>(null);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const apiBaseUrl = 'http://localhost:8000';
        const response = await fetch(`${apiBaseUrl}/calculate/roce-components/${ticker}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch ROCE data: ${await response.text()}`);
        }
        
        const jsonData = await response.json();
        setData(jsonData);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching ROCE data:', err);
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [ticker]);
  
  if (loading) return <div className="my-4 text-center">Loading ROCE analysis...</div>;
  if (error) return <div className="my-4 text-center text-red-600">Error: {error}</div>;
  if (!data) return <div className="my-4 text-center">No ROCE data available</div>;
  
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">ROCE Decomposition Analysis</h3>
        <p className="mb-4 text-sm text-gray-600">
          Return on Common Equity (ROCE) can be decomposed to understand the drivers of profitability:
          ROCE = RNOA + FLEV × SPREAD
        </p>
        
        {/* ROCE Overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 border rounded-lg bg-green-50">
            <p className="text-sm text-gray-500">Return on Common Equity (ROCE)</p>
            <p className="text-xl font-semibold">{formatPercent(data.roce)}</p>
          </div>
          <div className="p-4 border rounded-lg bg-blue-50">
            <p className="text-sm text-gray-500">Return on Net Operating Assets (RNOA)</p>
            <p className="text-xl font-semibold">{formatPercent(data.rnoa)}</p>
          </div>
          <div className="p-4 border rounded-lg bg-amber-50">
            <p className="text-sm text-gray-500">Financial Leverage Effect</p>
            <p className="text-xl font-semibold">{formatPercent(data.flev * data.spread)}</p>
          </div>
        </div>
        
        {/* ROCE Formula Breakdown */}
        <div className="p-4 border rounded-lg bg-gray-50 mb-6">
          <h4 className="font-medium mb-2">ROCE Formula Verification</h4>
          <p className="text-sm mb-2">ROCE = RNOA + (FLEV × SPREAD)</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-500">RNOA</p>
              <p className="font-medium">{formatPercent(data.rnoa)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">+ (FLEV × SPREAD)</p>
              <p className="font-medium">{formatPercent(data.flev * data.spread)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">= Calculated ROCE</p>
              <p className="font-medium">{formatPercent(data.checks.roce_check.calculated_roce)}</p>
            </div>
          </div>
        </div>
        
        {/* ROCE Components */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Level 1: Operating vs. Financing */}
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2">Level 1: Operating vs. Financing</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">Return on Net Operating Assets (RNOA)</p>
                <p className="font-medium">{formatPercent(data.rnoa)}</p>
                <p className="text-xs text-gray-400">Operating Income / Net Operating Assets</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Financial Leverage (FLEV)</p>
                <p className="font-medium">{formatRatio(data.flev)}</p>
                <p className="text-xs text-gray-400">NFO / CSE</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Spread</p>
                <p className="font-medium">{formatPercent(data.spread)}</p>
                <p className="text-xs text-gray-400">RNOA - NBC</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Net Borrowing Cost (NBC)</p>
                <p className="font-medium">{formatPercent(data.nbc)}</p>
                <p className="text-xs text-gray-400">Net Financial Expense / NFO</p>
              </div>
            </div>
          </div>
          
          {/* Level 2: RNOA Decomposition */}
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2">Level 2: RNOA Decomposition</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">Profit Margin (PM)</p>
                <p className="font-medium">{formatPercent(data.pm)}</p>
                <p className="text-xs text-gray-400">Operating Income / Sales</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Asset Turnover (ATO)</p>
                <p className="font-medium">{formatRatio(data.ato)}</p>
                <p className="text-xs text-gray-400">Sales / Net Operating Assets</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Operating Liability Leverage (OLLEV)</p>
                <p className="font-medium">{formatRatio(data.ollev)}</p>
                <p className="text-xs text-gray-400">Operating Liabilities / NOA</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">RNOA Formula Check</p>
                <p className="font-medium">PM × ATO = {formatPercent(data.checks.rnoa_check.calculated_rnoa)}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Key Components Table */}
        <div className="overflow-x-auto mb-6">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Net Income</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.net_income)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Operating Income</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.operating_income)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Net Financial Expense</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.net_financial_expense)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Common Shareholders' Equity</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.common_equity)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Net Operating Assets</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.net_operating_assets)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Net Financial Obligations</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.net_financial_obligations)}</td>
              </tr>
              <tr>
                <td className="px-6 py-2 whitespace-nowrap text-sm font-medium">Sales Revenue</td>
                <td className="px-6 py-2 whitespace-nowrap text-sm">${formatNumber(data.components.total_revenue)}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        {/* Cost of Capital */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">Cost of Capital</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-500">Cost of Equity (ρE)</p>
              <p className="font-medium">{formatPercent(data.cost_of_capital.cost_of_equity)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Cost of Debt (ρD)</p>
              <p className="font-medium">{formatPercent(data.cost_of_capital.cost_of_debt)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Cost of Operations (ρF)</p>
              <p className="font-medium">{formatPercent(data.cost_of_capital.cost_of_operations)}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 