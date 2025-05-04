"use client";

import { useState, useEffect } from 'react';
import { formatNumber, formatPercent } from '../utils/formatters';

interface ValuationModelsProps {
  ticker: string;
}

interface ResidualEarningsData {
  residual_earnings: {
    value: number;
    formula: string;
    components: {
      net_income: number;
      cost_of_equity: number;
      beginning_book_value: number;
    };
  };
  abnormal_earnings_growth: {
    value: number;
    formula: string;
    components: {
      forward_earnings: number;
      current_earnings: number;
      cost_of_equity: number;
      earnings_growth: number;
    };
  };
  valuation: {
    residual_earnings_valuation: {
      enterprise_value: number;
      per_share_value: number;
      formula: string;
    };
    abnormal_earnings_growth_valuation: {
      enterprise_value: number;
      per_share_value: number;
      formula: string;
    };
    market_comparison: {
      current_price: number;
      book_value_per_share: number;
      eps: number;
      p_b_ratio: number;
      p_e_ratio: number;
    };
  };
}

interface EnterpriseValuationData {
  residual_operating_income: {
    value: number;
    formula: string;
    components: {
      operating_income: number;
      cost_of_operations: number;
      net_operating_assets: number;
    };
  };
  enterprise_valuation: {
    enterprise_value: number;
    equity_value: number;
    equity_value_per_share: number;
    formula: string;
    components: {
      net_operating_assets: number;
      pv_of_reoi: number;
      net_financial_obligations: number;
    };
  };
  market_comparison: {
    current_price: number;
    implied_premium: number;
    implied_discount_percent: number;
  };
  assumptions: {
    growth_rate: number;
    cost_of_operations: number;
  };
}

export default function ValuationModels({ ticker }: ValuationModelsProps) {
  const [activeTab, setActiveTab] = useState('re');
  const [loadingRE, setLoadingRE] = useState(true);
  const [loadingEV, setLoadingEV] = useState(true);
  const [errorRE, setErrorRE] = useState<string | null>(null);
  const [errorEV, setErrorEV] = useState<string | null>(null);
  const [reData, setReData] = useState<ResidualEarningsData | null>(null);
  const [evData, setEvData] = useState<EnterpriseValuationData | null>(null);
  
  useEffect(() => {
    const fetchResidualEarningsData = async () => {
      try {
        setLoadingRE(true);
        setErrorRE(null);
        const apiBaseUrl = 'http://localhost:8000';
        const response = await fetch(`${apiBaseUrl}/calculate/residual-earnings/${ticker}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch residual earnings data: ${await response.text()}`);
        }
        
        const jsonData = await response.json();
        setReData(jsonData);
        setLoadingRE(false);
      } catch (err) {
        console.error('Error fetching residual earnings data:', err);
        setErrorRE(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoadingRE(false);
      }
    };
    
    const fetchEnterpriseValuationData = async () => {
      try {
        setLoadingEV(true);
        setErrorEV(null);
        const apiBaseUrl = 'http://localhost:8000';
        const response = await fetch(`${apiBaseUrl}/enterprise-valuation/${ticker}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch enterprise valuation data: ${await response.text()}`);
        }
        
        const jsonData = await response.json();
        setEvData(jsonData);
        setLoadingEV(false);
      } catch (err) {
        console.error('Error fetching enterprise valuation data:', err);
        setErrorEV(err instanceof Error ? err.message : 'An unknown error occurred');
        setLoadingEV(false);
      }
    };
    
    fetchResidualEarningsData();
    fetchEnterpriseValuationData();
  }, [ticker]);
  
  const renderResidualEarningsTab = () => {
    if (loadingRE) return <div className="my-4 text-center">Loading residual earnings analysis...</div>;
    if (errorRE) return <div className="my-4 text-center text-red-600">Error: {errorRE}</div>;
    if (!reData) return <div className="my-4 text-center">No residual earnings data available</div>;
    
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Residual Earnings Analysis */}
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2">Residual Earnings (RE) Analysis</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">Residual Earnings</p>
                <p className="font-medium">${formatNumber(reData.residual_earnings.value)}</p>
                <p className="text-xs text-gray-400">{reData.residual_earnings.formula}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Components</p>
                <p className="text-xs text-gray-500">Net Income: ${formatNumber(reData.residual_earnings.components.net_income)}</p>
                <p className="text-xs text-gray-500">Cost of Equity: {formatPercent(reData.residual_earnings.components.cost_of_equity)}</p>
                <p className="text-xs text-gray-500">Book Value: ${formatNumber(reData.residual_earnings.components.beginning_book_value)}</p>
              </div>
            </div>
          </div>
          
          {/* Abnormal Earnings Growth */}
          <div className="p-4 border rounded-lg">
            <h4 className="font-medium mb-2">Abnormal Earnings Growth (AEG) Analysis</h4>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">Abnormal Earnings Growth</p>
                <p className="font-medium">${formatNumber(reData.abnormal_earnings_growth.value)}</p>
                <p className="text-xs text-gray-400">{reData.abnormal_earnings_growth.formula}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Components</p>
                <p className="text-xs text-gray-500">Forward Earnings: ${formatNumber(reData.abnormal_earnings_growth.components.forward_earnings)}</p>
                <p className="text-xs text-gray-500">Current Earnings: ${formatNumber(reData.abnormal_earnings_growth.components.current_earnings)}</p>
                <p className="text-xs text-gray-500">Earnings Growth: {formatPercent(reData.abnormal_earnings_growth.components.earnings_growth)}</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Valuation Results */}
        <div className="p-6 border rounded-lg bg-blue-50">
          <h4 className="font-semibold mb-4">Valuation Results</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* RE Valuation */}
            <div className="p-4 border rounded-lg bg-white">
              <h5 className="font-medium mb-2">Residual Earnings Valuation</h5>
              <p className="text-xs text-gray-500 mb-2">{reData.valuation.residual_earnings_valuation.formula}</p>
              <div className="space-y-1">
                <p className="text-sm">Enterprise Value: ${formatNumber(reData.valuation.residual_earnings_valuation.enterprise_value)}</p>
                <p className="text-2xl font-bold text-blue-800">${formatNumber(reData.valuation.residual_earnings_valuation.per_share_value)} per share</p>
              </div>
            </div>
            
            {/* AEG Valuation */}
            <div className="p-4 border rounded-lg bg-white">
              <h5 className="font-medium mb-2">Abnormal Earnings Growth Valuation</h5>
              <p className="text-xs text-gray-500 mb-2">{reData.valuation.abnormal_earnings_growth_valuation.formula}</p>
              <div className="space-y-1">
                <p className="text-sm">Enterprise Value: ${formatNumber(reData.valuation.abnormal_earnings_growth_valuation.enterprise_value)}</p>
                <p className="text-2xl font-bold text-blue-800">${formatNumber(reData.valuation.abnormal_earnings_growth_valuation.per_share_value)} per share</p>
              </div>
            </div>
          </div>
          
          {/* Market Comparison */}
          <div className="p-4 border rounded-lg bg-white">
            <h5 className="font-medium mb-2">Market Comparison</h5>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Current Market Price</p>
                <p className="text-xl font-semibold">${formatNumber(reData.valuation.market_comparison.current_price)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Book Value Per Share</p>
                <p className="text-lg font-medium">${formatNumber(reData.valuation.market_comparison.book_value_per_share)}</p>
                <p className="text-xs text-gray-500">P/B Ratio: {formatNumber(reData.valuation.market_comparison.p_b_ratio)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Earnings Per Share</p>
                <p className="text-lg font-medium">${formatNumber(reData.valuation.market_comparison.eps)}</p>
                <p className="text-xs text-gray-500">P/E Ratio: {formatNumber(reData.valuation.market_comparison.p_e_ratio)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderEnterpriseValuationTab = () => {
    if (loadingEV) return <div className="my-4 text-center">Loading enterprise valuation analysis...</div>;
    if (errorEV) return <div className="my-4 text-center text-red-600">Error: {errorEV}</div>;
    if (!evData) return <div className="my-4 text-center">No enterprise valuation data available</div>;
    
    return (
      <div className="space-y-6">
        {/* ReOI Analysis */}
        <div className="p-4 border rounded-lg">
          <h4 className="font-medium mb-2">Residual Operating Income (ReOI) Analysis</h4>
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-500">Residual Operating Income</p>
              <p className="font-medium">${formatNumber(evData.residual_operating_income.value)}</p>
              <p className="text-xs text-gray-400">{evData.residual_operating_income.formula}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Components</p>
              <p className="text-xs text-gray-500">Operating Income: ${formatNumber(evData.residual_operating_income.components.operating_income)}</p>
              <p className="text-xs text-gray-500">Cost of Operations: {formatPercent(evData.residual_operating_income.components.cost_of_operations)}</p>
              <p className="text-xs text-gray-500">Net Operating Assets: ${formatNumber(evData.residual_operating_income.components.net_operating_assets)}</p>
            </div>
          </div>
        </div>
        
        {/* Enterprise Valuation Results */}
        <div className="p-6 border rounded-lg bg-blue-50">
          <h4 className="font-semibold mb-4">Enterprise Valuation Results</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Enterprise Value */}
            <div className="p-4 border rounded-lg bg-white">
              <h5 className="font-medium mb-2">Enterprise Value</h5>
              <p className="text-xs text-gray-500 mb-2">{evData.enterprise_valuation.formula}</p>
              <div className="space-y-1">
                <p className="text-sm">Net Operating Assets: ${formatNumber(evData.enterprise_valuation.components.net_operating_assets)}</p>
                <p className="text-sm">+ PV of ReOI: ${formatNumber(evData.enterprise_valuation.components.pv_of_reoi)}</p>
                <p className="text-xl font-bold">= ${formatNumber(evData.enterprise_valuation.enterprise_value)}</p>
              </div>
            </div>
            
            {/* Equity Value */}
            <div className="p-4 border rounded-lg bg-white">
              <h5 className="font-medium mb-2">Equity Value</h5>
              <p className="text-xs text-gray-500 mb-2">Enterprise Value - Net Financial Obligations</p>
              <div className="space-y-1">
                <p className="text-sm">Enterprise Value: ${formatNumber(evData.enterprise_valuation.enterprise_value)}</p>
                <p className="text-sm">- Net Financial Obligations: ${formatNumber(evData.enterprise_valuation.components.net_financial_obligations)}</p>
                <p className="text-xl font-bold">= ${formatNumber(evData.enterprise_valuation.equity_value)}</p>
                <p className="text-2xl font-bold text-blue-800">${formatNumber(evData.enterprise_valuation.equity_value_per_share)} per share</p>
              </div>
            </div>
          </div>
          
          {/* Market Comparison */}
          <div className="p-4 border rounded-lg bg-white">
            <h5 className="font-medium mb-2">Market Comparison</h5>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500">Current Market Price</p>
                <p className="text-xl font-semibold">${formatNumber(evData.market_comparison.current_price)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Implied Premium/Discount</p>
                <p className={`text-lg font-medium ${evData.market_comparison.implied_premium > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${formatNumber(evData.market_comparison.implied_premium)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Discount Percentage</p>
                <p className={`text-lg font-medium ${evData.market_comparison.implied_discount_percent > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercent(evData.market_comparison.implied_discount_percent / 100)}
                </p>
              </div>
            </div>
          </div>
          
          {/* Assumptions */}
          <div className="mt-4 p-4 border rounded-lg bg-gray-50">
            <h5 className="font-medium mb-2">Key Assumptions</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500">Cost of Operations</p>
                <p className="text-lg font-medium">{formatPercent(evData.assumptions.cost_of_operations)}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Long-term Growth Rate</p>
                <p className="text-lg font-medium">{formatPercent(evData.assumptions.growth_rate)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold mb-4">Valuation Models</h3>
        
        {/* Tabs */}
        <div className="mb-6">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
              <button
                onClick={() => setActiveTab('re')}
                className={`${
                  activeTab === 're'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Residual Earnings Valuation
              </button>
              <button
                onClick={() => setActiveTab('ev')}
                className={`${
                  activeTab === 'ev'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
              >
                Enterprise Valuation
              </button>
            </nav>
          </div>
        </div>
        
        {/* Tab Content */}
        {activeTab === 're' ? renderResidualEarningsTab() : renderEnterpriseValuationTab()}
      </div>
    </div>
  );
} 