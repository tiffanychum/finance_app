"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Search() {
  const [ticker, setTicker] = useState('');
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) {
      router.push(`/analysis/${ticker.trim().toUpperCase()}`);
    }
  };
// test
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 lg:p-24">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-xl w-full">
        <Link 
          href="/"
          className="mb-6 inline-block text-blue-600 hover:underline"
        >
          ← Back to Home
        </Link>
        
        <h1 className="text-3xl font-bold text-center text-gray-800 mb-8">
          Search for a Stock
        </h1>
        
        <form onSubmit={handleSubmit} className="flex flex-col items-center">
          <div className="mb-6 w-full">
            <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-2">
              Enter Stock Ticker Symbol:
            </label>
            <input
              type="text"
              id="ticker"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="e.g., AAPL, MSFT, GOOGL"
              required
            />
          </div>
          
          <button
            type="submit"
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-md shadow-sm transition-all w-full sm:w-auto"
          >
            Analyze Stock
          </button>
        </form>
        
        <div className="mt-10">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">Popular Stocks:</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA'].map((stock) => (
              <Link
                key={stock}
                href={`/analysis/${stock}`}
                className="text-center py-2 px-3 bg-gray-100 hover:bg-gray-200 rounded-md transition-all"
              >
                {stock}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
} 