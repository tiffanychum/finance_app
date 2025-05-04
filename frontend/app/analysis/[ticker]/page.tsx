"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import RestructuredFinancials from './components/RestructuredFinancials';
import RoceDecomposition from './components/RoceDecomposition';
import ValuationModels from './components/ValuationModels';

// Types for our data
interface BusinessData {
  assetProfile?: any;
  summaryProfile?: any;
  industryTrend?: any;
}

interface FinancialData {
  financialData?: any;
  incomeStatementHistory?: any;
  balanceSheetHistory?: any;
  cashflowStatementHistory?: any;
  defaultKeyStatistics?: any;
}

interface ValuationData {
  earnings?: any;
  earningsTrend?: any;
  recommendationTrend?: any;
}

interface FundamentalAnalysisData {
  step1_knowing_business: BusinessData;
  step2_analyzing_information: FinancialData;
  step3_4_forecasting_valuation: ValuationData;
}

interface RoceData {
  roce: number;
  net_income: number;
  total_equity: number;
  total_assets: number;
  total_liabilities: number;
  error?: string;
}

export default function AnalysisPage() {
  const { ticker } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<FundamentalAnalysisData | null>(null);
  const [roceData, setRoceData] = useState<RoceData | null>(null);
  const [activeTab, setActiveTab] = useState(1); // Default to Step 1
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // API endpoint - in a production app, use environment variables
        const apiBaseUrl = 'http://localhost:8000';
        
        console.log(`Fetching data for ${ticker} from ${apiBaseUrl}/fundamental-analysis/${ticker}`);
        
        // Fetch fundamental analysis data
        const analysisResponse = await fetch(`${apiBaseUrl}/fundamental-analysis/${ticker}`);
        if (!analysisResponse.ok) {
          const errorText = await analysisResponse.text();
          throw new Error(`Failed to fetch analysis data: ${errorText}`);
        }
        const analysisData = await analysisResponse.json();
        setAnalysisData(analysisData);
        
        // Fetch ROCE data - handle separately to allow partial page loading if this fails
        try {
          console.log(`Fetching ROCE data for ${ticker}`);
          const roceResponse = await fetch(`${apiBaseUrl}/calculate/roce/${ticker}`);
          const roceData = await roceResponse.json();
          setRoceData(roceData);
        } catch (roceError) {
          console.error("Error fetching ROCE data:", roceError);
          // Set default ROCE data with error message
          setRoceData({
            roce: 0,
            net_income: 0,
            total_equity: 1,
            total_assets: 0,
            total_liabilities: 0,
            error: roceError instanceof Error ? roceError.message : 'Failed to fetch ROCE data'
          });
        }
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching analysis data:", error);
        setError(error instanceof Error ? error.message : 'An unknown error occurred');
        setLoading(false);
      }
    };
    
    fetchData();
  }, [ticker]);
  
  const renderTabContent = () => {
    if (loading) return <div className="text-center py-10">Loading data...</div>;
    if (error) return <div className="text-center py-10 text-red-600">Error: {error}</div>;
    if (!analysisData) return <div className="text-center py-10">No data available</div>;
    
    switch (activeTab) {
      case 1:
        return renderBusinessAnalysis();
      case 2:
        return renderFinancialAnalysis();
      case 3:
        return renderPayoffForecasting();
      case 4:
        return renderValuationAnalysis();
      case 5:
        return renderTradingRecommendation();
      default:
        return <div>Select a tab</div>;
    }
  };
  
  const renderBusinessAnalysis = () => {
    const businessData = analysisData?.step1_knowing_business;
    const profile = businessData?.assetProfile || {};
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Step 1: Knowing the Business</h2>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Company Profile</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="font-medium">Name:</p>
              <p>{profile.name || ticker}</p>
            </div>
            <div>
              <p className="font-medium">Industry:</p>
              <p>{profile.industry || 'N/A'}</p>
            </div>
            <div>
              <p className="font-medium">Sector:</p>
              <p>{profile.sector || 'N/A'}</p>
            </div>
            <div>
              <p className="font-medium">Employees:</p>
              <p>{profile.fullTimeEmployees?.toLocaleString() || 'N/A'}</p>
            </div>
            <div className="md:col-span-2">
              <p className="font-medium">Website:</p>
              <a 
                href={profile.website} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {profile.website || 'N/A'}
              </a>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Business Summary</h3>
          <p className="text-gray-700 whitespace-pre-line">
            {profile.longBusinessSummary || 'No business summary available.'}
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Management</h3>
          {profile.companyOfficers && profile.companyOfficers.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Age</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {profile.companyOfficers.map((officer: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">{officer.name || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{officer.title || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{officer.age || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No management information available.</p>
          )}
        </div>
      </div>
    );
  };
  
  const renderFinancialAnalysis = () => {
    const financialData = analysisData?.step2_analyzing_information;
    const stats = financialData?.defaultKeyStatistics || {};
    const finances = financialData?.financialData || {};
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Step 2: Analyzing Information</h2>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Key Financial Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Revenue (TTM)</p>
              <p className="text-xl font-semibold">${finances.totalRevenue?.toLocaleString() || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Gross Margin</p>
              <p className="text-xl font-semibold">{(finances.grossMargins * 100)?.toFixed(2) || 'N/A'}%</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Operating Margin</p>
              <p className="text-xl font-semibold">{(finances.operatingMargins * 100)?.toFixed(2) || 'N/A'}%</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">EPS (TTM)</p>
              <p className="text-xl font-semibold">${finances.trailingEps?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">P/E Ratio</p>
              <p className="text-xl font-semibold">{stats.trailingPE?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Market Cap</p>
              <p className="text-xl font-semibold">${(stats.marketCap / 1e9)?.toFixed(2) || 'N/A'}B</p>
            </div>
          </div>
        </div>
        
        {/* Add Restructured Financials Component */}
        <RestructuredFinancials ticker={ticker as string} />
        
        {/* Add ROCE Decomposition Analysis */}
        <RoceDecomposition ticker={ticker as string} />
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Financial Health</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Quick Ratio</p>
              <p className="text-xl font-semibold">{finances.quickRatio?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Current Ratio</p>
              <p className="text-xl font-semibold">{finances.currentRatio?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Debt to Equity</p>
              <p className="text-xl font-semibold">{finances.debtToEquity?.toFixed(2) || 'N/A'}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Return on Assets</p>
              <p className="text-xl font-semibold">{(finances.returnOnAssets * 100)?.toFixed(2) || 'N/A'}%</p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  const renderPayoffForecasting = () => {
    const valuationData = analysisData?.step3_4_forecasting_valuation;
    const earnings = valuationData?.earnings?.financialsChart?.yearly || [];
    const earningsTrend = valuationData?.earningsTrend?.trend || [];
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Step 3: Forecasting Payoffs</h2>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Historical Earnings</h3>
          {earnings.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Revenue</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Earnings</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {earnings.map((item: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">{item.date}</td>
                      <td className="px-6 py-4 whitespace-nowrap">${(item.revenue / 1e9).toFixed(2)}B</td>
                      <td className="px-6 py-4 whitespace-nowrap">${(item.earnings / 1e9).toFixed(2)}B</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No historical earnings data available.</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Earnings Forecast</h3>
          {earningsTrend && earningsTrend.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">EPS Estimate</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Growth</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {earningsTrend.map((item: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">{item.period}</td>
                      <td className="px-6 py-4 whitespace-nowrap">${item.earningsEstimate?.avg?.toFixed(2) || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {item.earningsEstimate?.growth ? 
                          `${(item.earningsEstimate.growth * 100).toFixed(2)}%` : 
                          'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No earnings forecast data available.</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Growth Metrics</h3>
          {analysisData?.step2_analyzing_information?.financialData ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-gray-500">Revenue Growth (YoY)</p>
                <p className="text-xl font-semibold">
                  {(analysisData.step2_analyzing_information.financialData.revenueGrowth * 100)?.toFixed(2)}%
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-gray-500">Earnings Growth (YoY)</p>
                <p className="text-xl font-semibold">
                  {(analysisData.step2_analyzing_information.financialData.earningsGrowth * 100)?.toFixed(2)}%
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-gray-500">Free Cash Flow</p>
                <p className="text-xl font-semibold">
                  ${(analysisData.step2_analyzing_information.financialData.freeCashflow / 1e9)?.toFixed(2)}B
                </p>
              </div>
              <div className="p-4 border rounded-lg">
                <p className="text-sm text-gray-500">Operating Cash Flow</p>
                <p className="text-xl font-semibold">
                  ${(analysisData.step2_analyzing_information.financialData.operatingCashflow / 1e9)?.toFixed(2)}B
                </p>
              </div>
            </div>
          ) : (
            <p>Growth metrics not available.</p>
          )}
        </div>
      </div>
    );
  };
  
  const renderValuationAnalysis = () => {
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Step 4: Convert Forecasts to a Valuation</h2>
        
        {/* Add Valuation Models Component */}
        <ValuationModels ticker={ticker as string} />
      </div>
    );
  };
  
  const renderTradingRecommendation = () => {
    const recommendations = analysisData?.step3_4_forecasting_valuation?.recommendationTrend?.trend || [];
    const currentPrice = analysisData?.step2_analyzing_information?.financialData?.currentPrice || 0;
    const targetMeanPrice = analysisData?.step2_analyzing_information?.financialData?.targetMeanPrice || 0;
    const targetHighPrice = analysisData?.step2_analyzing_information?.financialData?.targetHighPrice || 0;
    const targetLowPrice = analysisData?.step2_analyzing_information?.financialData?.targetLowPrice || 0;
    
    // Calculate the upside potential
    const upsidePercentage = ((targetMeanPrice / currentPrice) - 1) * 100;
    
    // Determine recommendation based on upside percentage
    let recommendation = 'HOLD';
    let recommendationColor = 'text-yellow-600';
    
    if (upsidePercentage > 20) {
      recommendation = 'STRONG BUY';
      recommendationColor = 'text-green-600';
    } else if (upsidePercentage > 5) {
      recommendation = 'BUY';
      recommendationColor = 'text-green-600';
    } else if (upsidePercentage < -10) {
      recommendation = 'SELL';
      recommendationColor = 'text-red-600';
    } else if (upsidePercentage < -5) {
      recommendation = 'REDUCE';
      recommendationColor = 'text-red-600';
    }
    
    return (
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">Step 5: Trading on the Valuation</h2>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-6">Price Targets</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Current Price</p>
              <p className="text-xl font-semibold">${currentPrice?.toFixed(2)}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Mean Target</p>
              <p className="text-xl font-semibold">${targetMeanPrice?.toFixed(2)}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">High Target</p>
              <p className="text-xl font-semibold">${targetHighPrice?.toFixed(2)}</p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Low Target</p>
              <p className="text-xl font-semibold">${targetLowPrice?.toFixed(2)}</p>
            </div>
          </div>
          
          <div className="mt-6 p-6 bg-gray-50 rounded-lg border">
            <h4 className="text-lg font-semibold mb-2">Upside Potential:</h4>
            <p className={`text-2xl font-bold ${upsidePercentage >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {upsidePercentage.toFixed(2)}%
            </p>
            
            <h4 className="text-lg font-semibold mt-6 mb-2">Recommendation:</h4>
            <p className={`text-3xl font-bold ${recommendationColor}`}>
              {recommendation}
            </p>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Analyst Recommendations</h3>
          {recommendations.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Period</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strong Buy</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Buy</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Hold</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sell</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Strong Sell</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recommendations.map((item: any, index: number) => (
                    <tr key={index}>
                      <td className="px-6 py-4 whitespace-nowrap">{item.period}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.strongBuy}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.buy}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.hold}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.sell}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{item.strongSell}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>No analyst recommendations available.</p>
          )}
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-semibold mb-4">Risk Assessment</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">Beta</p>
              <p className="text-xl font-semibold">
                {analysisData?.step2_analyzing_information?.defaultKeyStatistics?.beta?.toFixed(2) || 'N/A'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                Beta {'>'}1 indicates higher volatility than the market
              </p>
            </div>
            <div className="p-4 border rounded-lg">
              <p className="text-sm text-gray-500">52-Week Change</p>
              <p className={`text-xl font-semibold ${
                (analysisData?.step2_analyzing_information?.defaultKeyStatistics?.['52WeekChange'] || 0) >= 0 
                ? 'text-green-600' 
                : 'text-red-600'
              }`}>
                {((analysisData?.step2_analyzing_information?.defaultKeyStatistics?.['52WeekChange'] || 0) * 100).toFixed(2)}%
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };
  
  return (
    <div className="min-h-screen bg-gray-50 p-4 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <Link href="/" className="mb-6 inline-block text-blue-600 hover:underline">
          ← Back to Home
        </Link>
        
        <div className="bg-white rounded-xl shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold">
            {ticker} Fundamental Analysis
          </h1>
          <p className="text-gray-600 mt-2">
            Complete analysis using the 5-step fundamental analysis process
          </p>
        </div>
        
        {/* Analysis Tabs */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button 
            onClick={() => setActiveTab(1)}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 1 
                ? 'bg-blue-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            1. Business
          </button>
          <button 
            onClick={() => setActiveTab(2)}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 2 
                ? 'bg-green-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            2. Financials
          </button>
          <button 
            onClick={() => setActiveTab(3)}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 3 
                ? 'bg-amber-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            3. Forecast
          </button>
          <button 
            onClick={() => setActiveTab(4)}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 4 
                ? 'bg-purple-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            4. Valuation
          </button>
          <button 
            onClick={() => setActiveTab(5)}
            className={`px-4 py-2 rounded-md transition-all ${
              activeTab === 5 
                ? 'bg-red-600 text-white' 
                : 'bg-white text-gray-700 hover:bg-gray-100'
            }`}
          >
            5. Trading
          </button>
        </div>
        
        {/* Tab Content */}
        <div className="bg-white rounded-xl shadow-md p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
} 