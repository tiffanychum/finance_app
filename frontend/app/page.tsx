import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 lg:p-24">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-5xl w-full">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
          Fundamental Analysis App
        </h1>
        <p className="text-gray-600 text-center mb-10">
          Analyze stocks using the 5-step fundamental analysis process
        </p>
        
        <div className="mb-10">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">The Five Steps of Fundamental Analysis:</h2>
          <div className="space-y-3">
            <div className="p-3 bg-blue-50 rounded-lg border border-blue-100">
              <p className="font-medium">1. Knowing the Business</p>
              <p className="text-sm text-gray-600">Understanding products, technology, competition, management, and the regulatory environment</p>
            </div>
            <div className="p-3 bg-green-50 rounded-lg border border-green-100">
              <p className="font-medium">2. Analyzing Information</p>
              <p className="text-sm text-gray-600">Reviewing financial statements and other relevant data</p>
            </div>
            <div className="p-3 bg-amber-50 rounded-lg border border-amber-100">
              <p className="font-medium">3. Forecasting Payoffs</p>
              <p className="text-sm text-gray-600">Predicting future financial performance (e.g., earnings, cash flows)</p>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg border border-purple-100">
              <p className="font-medium">4. Convert Forecasts to a Valuation</p>
              <p className="text-sm text-gray-600">Using models to estimate the firm's intrinsic value</p>
            </div>
            <div className="p-3 bg-red-50 rounded-lg border border-red-100">
              <p className="font-medium">5. Trading on the Valuation</p>
              <p className="text-sm text-gray-600">Making investment decisions based on comparing the estimated value to the market price</p>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <p className="mb-4 text-lg font-medium">Get started with TSLA (Tesla) or enter another stock symbol:</p>
          <div className="flex justify-center gap-4">
            <Link 
              href="/analysis/TSLA" 
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm transition-all"
            >
              Analyze TSLA
            </Link>
            <Link 
              href="/search" 
              className="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium rounded-md shadow-sm transition-all"
            >
              Search Other Stocks
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
