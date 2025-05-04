#!/bin/bash
# Utility script to test Yahoo Finance data for debugging

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
  echo "Creating Python virtual environment..."
  python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing dependencies..."
pip install -q yahooquery fastapi uvicorn

# Define test tickers
TICKERS=("AAPL" "MSFT" "TSLA" "AMZN" "FB" "NVDA" "INTC" "AMD")

# Test the ticker data format
echo "Testing Yahoo Finance data format for multiple tickers..."
python test_yahoo_data.py "${TICKERS[@]}"

# Prompt user to test enterprise valuation for a specific ticker
echo ""
echo "Would you like to test enterprise valuation for a specific ticker? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "Enter ticker symbol (default: AAPL):"
  read -r ticker
  ticker=${ticker:-AAPL}
  echo "Testing enterprise valuation for $ticker..."
  python test_enterprise_valuation.py "$ticker"
fi

# Test the Debug API endpoint
echo ""
echo "Would you like to test the debug API endpoint? (y/N)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
  echo "Starting FastAPI server..."
  uvicorn main:app --host 127.0.0.1 --port 8000 &
  SERVER_PID=$!
  
  # Wait for server to start
  sleep 3
  
  echo "Enter ticker symbol to test (default: AAPL):"
  read -r ticker
  ticker=${ticker:-AAPL}
  
  echo "Testing debug endpoint for $ticker..."
  curl -s "http://127.0.0.1:8000/debug-financial-data/$ticker" | python -m json.tool
  
  # Kill the server
  kill $SERVER_PID
fi

echo "Done!" 