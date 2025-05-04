import requests
import json
import sys

def test_api_connection():
    """Test basic API connection"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"API Connection: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"API Connection Error: {str(e)}")
        return False

def test_stock_data(ticker="TSLA"):
    """Test getting basic stock data"""
    try:
        response = requests.get(f"http://localhost:8000/stock/{ticker}")
        success = response.status_code == 200
        print(f"Stock Data for {ticker}: {'SUCCESS' if success else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        if success:
            data = response.json()
            print(f"Keys in response: {list(data.get(ticker, {}).keys())}")
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
        return success
    except Exception as e:
        print(f"Stock Data Error: {str(e)}")
        return False

def test_fundamental_analysis(ticker="TSLA"):
    """Test getting fundamental analysis data"""
    try:
        response = requests.get(f"http://localhost:8000/fundamental-analysis/{ticker}")
        success = response.status_code == 200
        print(f"Fundamental Analysis for {ticker}: {'SUCCESS' if success else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        if success:
            data = response.json()
            print("Data received for steps:")
            print(f"- Step 1: {list(data.get('step1_knowing_business', {}).keys())}")
            print(f"- Step 2: {list(data.get('step2_analyzing_information', {}).keys())}")
            print(f"- Steps 3/4: {list(data.get('step3_4_forecasting_valuation', {}).keys())}")
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
        return success
    except Exception as e:
        print(f"Fundamental Analysis Error: {str(e)}")
        return False

def test_roce_calculation(ticker="TSLA"):
    """Test ROCE calculation"""
    try:
        response = requests.get(f"http://localhost:8000/calculate/roce/{ticker}")
        success = response.status_code == 200
        print(f"ROCE Calculation for {ticker}: {'SUCCESS' if success else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        if success:
            data = response.json()
            print(f"ROCE: {data.get('roce')}")
            print(f"Net Income: {data.get('net_income')}")
            print(f"Total Equity: {data.get('total_equity')}")
        else:
            print(f"Error: {response.text}")
        print("-" * 50)
        return success
    except Exception as e:
        print(f"ROCE Calculation Error: {str(e)}")
        return False

if __name__ == "__main__":
    ticker = "TSLA"
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    print(f"Testing API with ticker: {ticker}")
    print("=" * 50)
    
    connection_ok = test_api_connection()
    
    if connection_ok:
        test_stock_data(ticker)
        test_fundamental_analysis(ticker)
        test_roce_calculation(ticker)
    else:
        print("API connection failed. Make sure the server is running.") 