import logging
import traceback
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from yahooquery import Ticker
from typing import List, Optional, Dict, Any
import json
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("finance_app")

# Create FastAPI app
app = FastAPI(
    title="Finance App API",
    description="Financial data and analysis API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Finance App API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/stock/{ticker}")
def get_stock_data(ticker: str, modules: Optional[str] = None):
    """
    Get stock data for a specific ticker using yahooquery
    """
    try:
        logger.info(f"Getting stock data for {ticker}")
        stock = Ticker(ticker)
        
        # If modules parameter is provided, get specific modules
        if modules:
            module_list = modules.split(',')
            logger.info(f"Fetching modules: {module_list}")
            data = stock.get_modules(module_list)
        else:
            # Default modules for fundamental analysis
            default_modules = [
                "assetProfile",
                "financialData",
                "defaultKeyStatistics",
                "incomeStatementHistory",
                "balanceSheetHistory",
                "cashflowStatementHistory",
                "recommendationTrend",
                "earnings"
            ]
            logger.info(f"Fetching default modules: {default_modules}")
            data = stock.get_modules(default_modules)
        
        logger.info(f"Successfully retrieved data for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/fundamental-analysis/{ticker}")
def get_fundamental_analysis(ticker: str):
    """
    Get data for all 5 steps of fundamental analysis
    """
    try:
        logger.info(f"Getting fundamental analysis for {ticker}")
        stock = Ticker(ticker)
        
        # Step 1: Knowing the Business
        business_modules = ["assetProfile", "summaryProfile", "industryTrend"]
        logger.info(f"Fetching business modules: {business_modules}")
        business_data = stock.get_modules(business_modules)
        
        # Step 2: Analyzing Information
        financial_modules = [
            "financialData", 
            "incomeStatementHistory", 
            "balanceSheetHistory",
            "cashflowStatementHistory",
            "defaultKeyStatistics"
        ]
        logger.info(f"Fetching financial modules: {financial_modules}")
        financial_data = stock.get_modules(financial_modules)
        
        # Step 3 & 4: Forecasting Payoffs & Convert to Valuation
        valuation_modules = [
            "earnings",
            "earningsTrend",
            "recommendationTrend"
        ]
        logger.info(f"Fetching valuation modules: {valuation_modules}")
        valuation_data = stock.get_modules(valuation_modules)
        
        logger.info(f"Successfully retrieved fundamental analysis for {ticker}")
        return {
            "step1_knowing_business": business_data,
            "step2_analyzing_information": financial_data,
            "step3_4_forecasting_valuation": valuation_data,
            # Step 5 (Trading on Valuation) will be calculated in the frontend
        }
    except Exception as e:
        logger.error(f"Error in fundamental analysis for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/financial_statements/{ticker}")
async def get_financial_statements(ticker: str, enable_cors: bool = Query(False)):
    """
    Get reorganized financial statements for a ticker
    """
    try:
        return reorganize_financial_statements(ticker, enable_cors)
    except Exception as e:
        logger.error(f"Error getting financial statements for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calculate/roce/{ticker}")
def calculate_roce(ticker: str):
    """
    Calculate ROCE (Return on Common Equity) for a ticker
    """
    try:
        logger.info(f"Calculating ROCE for {ticker}")
        stock = Ticker(ticker)
        
        # Get financial data using direct methods
        try:
            # Get income statement
            income_statement = stock.income_statement(frequency='a')
            if isinstance(income_statement, str) or income_statement.empty:
                logger.warning(f"No income statement data for {ticker}")
                raise ValueError(f"No income statement data available for {ticker}")
                
            # Get balance sheet
            balance_sheet = stock.balance_sheet(frequency='a')
            if isinstance(balance_sheet, str) or balance_sheet.empty:
                logger.warning(f"No balance sheet data for {ticker}")
                raise ValueError(f"No balance sheet data available for {ticker}")
                
            # Get the most recent year's data
            latest_income = income_statement.sort_values('asOfDate', ascending=False).iloc[0]
            latest_balance = balance_sheet.sort_values('asOfDate', ascending=False).iloc[0]
            
            # Extract net income
            net_income = None
            for income_field in ['NetIncome', 'netIncome']:
                if income_field in latest_income:
                    net_income = latest_income[income_field]
                    if isinstance(net_income, pd.Series) and 'reportedValue' in net_income:
                        net_income = net_income['reportedValue']
                    break
            
            # Extract total equity
            total_equity = None
            for equity_field in ['StockholdersEquity', 'totalStockholderEquity']:
                if equity_field in latest_balance:
                    total_equity = latest_balance[equity_field]
                    if isinstance(total_equity, pd.Series) and 'reportedValue' in total_equity:
                        total_equity = total_equity['reportedValue']
                    break
            
            # Calculate ROCE
            if not net_income or not total_equity or total_equity == 0:
                logger.warning(f"Cannot calculate ROCE for {ticker}: net_income={net_income}, total_equity={total_equity}")
                raise ValueError(f"Cannot calculate ROCE for {ticker}: missing data")
                
            roce = net_income / total_equity
            
            # Return the results
            return {
                "ticker": ticker,
                "roce": roce,
                "net_income": net_income,
                "total_equity": total_equity,
                "year": str(latest_income.get('asOfDate'))
            }
                
        except Exception as e:
            logger.error(f"Error calculating ROCE for {ticker}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error calculating ROCE: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in ROCE calculation for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def reorganize_financial_statements(ticker, enable_cors=False):
    """
    Reorganize financial statements for a ticker.
    Returns structured financial data organized by statement type and date.
    """
    logger.info(f"Getting financial statements for {ticker}")
    try:
        stock = Ticker(ticker, asynchronous=False)
        
        # Get financial data using direct methods instead of all_financial_data()
        try:
            # Get individual statements directly
            income_statement = stock.income_statement(frequency='a')
            balance_sheet = stock.balance_sheet(frequency='a')
            cash_flow = stock.cash_flow(frequency='a')
            
            # Check for valid data
            if isinstance(income_statement, str) or income_statement.empty:
                logger.warning(f"No income statement data for {ticker}")
            if isinstance(balance_sheet, str) or balance_sheet.empty:
                logger.warning(f"No balance sheet data for {ticker}")
            if isinstance(cash_flow, str) or cash_flow.empty:
                logger.warning(f"No cash flow data for {ticker}")
                
            # Get quote data
            try:
                quote_data = stock.price
                if isinstance(quote_data, str):
                    logger.warning(f"Quote data is a string, not a dictionary: {quote_data}")
                    quote_data = {}
                elif not quote_data or (isinstance(quote_data, dict) and ticker not in quote_data):
                    logger.warning(f"No quote data available for {ticker}")
                    quote_data = {}
            except Exception as e:
                logger.warning(f"Error getting quote data: {str(e)}")
                quote_data = {}
            
            # Process financial data - organize by statement type and date
            grouped_data = {}
            
            # Process income statement
            if not isinstance(income_statement, str) and not income_statement.empty:
                income_by_date = {}
                for _, row in income_statement.iterrows():
                    date = row.get('asOfDate')
                    if date:
                        date_str = str(date.date()) if hasattr(date, 'date') else str(date)
                        if date_str not in income_by_date:
                            income_by_date[date_str] = {}
                        income_by_date[date_str][row.get('dataCode')] = row.get('reportedValue')
                grouped_data["income_statement"] = income_by_date
                
            # Process balance sheet
            if not isinstance(balance_sheet, str) and not balance_sheet.empty:
                balance_by_date = {}
                for _, row in balance_sheet.iterrows():
                    date = row.get('asOfDate')
                    if date:
                        date_str = str(date.date()) if hasattr(date, 'date') else str(date)
                        if date_str not in balance_by_date:
                            balance_by_date[date_str] = {}
                        balance_by_date[date_str][row.get('dataCode')] = row.get('reportedValue')
                grouped_data["balance_sheet"] = balance_by_date
                
            # Process cash flow
            if not isinstance(cash_flow, str) and not cash_flow.empty:
                cash_flow_by_date = {}
                for _, row in cash_flow.iterrows():
                    date = row.get('asOfDate')
                    if date:
                        date_str = str(date.date()) if hasattr(date, 'date') else str(date)
                        if date_str not in cash_flow_by_date:
                            cash_flow_by_date[date_str] = {}
                        cash_flow_by_date[date_str][row.get('dataCode')] = row.get('reportedValue')
                grouped_data["cash_flow"] = cash_flow_by_date
            
            # Get market data if available
            market_data = {}
            if quote_data and ticker in quote_data:
                # Check if quote_data[ticker] is a dictionary, not a string
                ticker_data = quote_data[ticker]
                if isinstance(ticker_data, dict):
                    market_data = {
                        "price": ticker_data.get("regularMarketPrice", None),
                        "marketCap": ticker_data.get("marketCap", None),
                        "currency": ticker_data.get("currency", "USD"),
                    }
                else:
                    logger.warning(f"Quote data for {ticker} is not in the expected format: {ticker_data}")
                    # Set default market data
                    market_data = {
                        "price": None,
                        "marketCap": None,
                        "currency": "USD",
                    }
            
            # Return organized data
            restructured_financial_data = {
                "ticker": ticker,
                "financialStatements": grouped_data,
                "marketData": market_data,
                "operating_income": {
                    "sales_revenue": 0,
                    "cost_of_sales": 0,
                    "gross_margin": 0,
                    "research_development": 0,
                    "selling_general_admin": 0,
                    "core_oi_before_tax": 0,
                    "tax_on_oi": 0,
                    "core_oi_after_tax": 0,
                    "other_oi": 0,
                    "comprehensive_oi": 0
                },
                "financial_expense": {
                    "interest_expense": 0,
                    "interest_income": 0,
                    "net_interest_expense": 0,
                    "tax_benefit": 0,
                    "after_tax_nfe": 0
                },
                "summary": {
                    "net_operating_assets": 1,
                    "net_financial_obligations": 1,
                    "common_equity": 1,
                    "accounting_check": {
                        "nfo_plus_cse": 2,  # Default value 
                        "total_assets": 1,   # Default value
                        "difference": 1      # Default value
                    }
                },
                "operating_assets": {
                    "cash_and_equivalents": 0,
                    "accounts_receivable": 0,
                    "inventory": 0,
                    "other_current_assets": 0,
                    "ppe_net": 0,
                    "intangible_assets": 0,
                    "total_operating_assets": 1
                },
                "operating_liabilities": {
                    "accounts_payable": 0,
                    "accrued_liabilities": 0,
                    "deferred_revenue": 0,
                    "deferred_tax_liabilities": 0,
                    "total_operating_liabilities": 1
                },
                "financial_assets": {
                    "excess_cash": 0,
                    "long_term_investments": 0,
                    "total_financial_assets": 0
                },
                "financial_obligations": {
                    "short_term_debt": 0,
                    "long_term_debt": 0,
                    "other_liabilities": 0,
                    "total_financial_obligations": 0
                }
            }
            
            # Try to extract key metrics for ROCE calculation
            try:
                # Get the most recent year
                years = sorted(grouped_data.get("income_statement", {}).keys(), reverse=True)
                if years:
                    latest_year = years[0]
                    income_data = grouped_data.get("income_statement", {}).get(latest_year, {})
                    
                    # Operating income approximation
                    if "OperatingIncome" in income_data:
                        restructured_financial_data["operating_income"]["comprehensive_oi"] = income_data["OperatingIncome"]
                    elif "EBIT" in income_data:
                        restructured_financial_data["operating_income"]["comprehensive_oi"] = income_data["EBIT"]
                    
                    # Revenue
                    if "TotalRevenue" in income_data:
                        restructured_financial_data["operating_income"]["sales_revenue"] = income_data["TotalRevenue"]
                    
                    # Cost of sales
                    if "CostOfRevenue" in income_data:
                        restructured_financial_data["operating_income"]["cost_of_sales"] = income_data["CostOfRevenue"]
                    
                    # Calculate gross margin
                    sales = restructured_financial_data["operating_income"]["sales_revenue"]
                    cost = restructured_financial_data["operating_income"]["cost_of_sales"]
                    restructured_financial_data["operating_income"]["gross_margin"] = sales - cost
                    
                    # R&D
                    if "ResearchDevelopment" in income_data:
                        restructured_financial_data["operating_income"]["research_development"] = income_data["ResearchDevelopment"]
                    
                    # SG&A
                    if "SellingGeneralAdministrative" in income_data:
                        restructured_financial_data["operating_income"]["selling_general_admin"] = income_data["SellingGeneralAdministrative"]
                    
                    # Calculate before-tax income
                    gross_margin = restructured_financial_data["operating_income"]["gross_margin"]
                    r_and_d = restructured_financial_data["operating_income"]["research_development"]
                    sg_and_a = restructured_financial_data["operating_income"]["selling_general_admin"]
                    restructured_financial_data["operating_income"]["core_oi_before_tax"] = gross_margin - r_and_d - sg_and_a
                    
                    # Tax
                    if "TaxProvision" in income_data:
                        # Allocate taxes proportionally to operating income
                        total_income = income_data.get("PretaxIncome", 0)
                        if total_income:
                            tax_rate = income_data["TaxProvision"] / total_income
                            operating_income_tax = restructured_financial_data["operating_income"]["core_oi_before_tax"] * tax_rate
                            restructured_financial_data["operating_income"]["tax_on_oi"] = operating_income_tax
                    
                    # After tax operating income
                    before_tax = restructured_financial_data["operating_income"]["core_oi_before_tax"]
                    tax = restructured_financial_data["operating_income"]["tax_on_oi"]
                    restructured_financial_data["operating_income"]["core_oi_after_tax"] = before_tax - tax
                    
                    # Set comprehensive OI to be the same as core OI after tax
                    restructured_financial_data["operating_income"]["comprehensive_oi"] = restructured_financial_data["operating_income"]["core_oi_after_tax"]
                    
                    # Financial expense
                    if "InterestExpense" in income_data:
                        restructured_financial_data["financial_expense"]["interest_expense"] = abs(income_data["InterestExpense"])
                    
                    if "InterestIncome" in income_data:
                        restructured_financial_data["financial_expense"]["interest_income"] = income_data["InterestIncome"]
                    
                    # Net interest expense
                    interest_expense = restructured_financial_data["financial_expense"]["interest_expense"]
                    interest_income = restructured_financial_data["financial_expense"]["interest_income"]
                    restructured_financial_data["financial_expense"]["net_interest_expense"] = interest_expense - interest_income
                    
                    # Tax benefit on interest
                    if "TaxProvision" in income_data and "PretaxIncome" in income_data and income_data["PretaxIncome"] != 0:
                        effective_tax_rate = income_data["TaxProvision"] / income_data["PretaxIncome"]
                        tax_benefit = restructured_financial_data["financial_expense"]["net_interest_expense"] * effective_tax_rate
                        restructured_financial_data["financial_expense"]["tax_benefit"] = tax_benefit
                    
                    # After tax NFE
                    net_interest = restructured_financial_data["financial_expense"]["net_interest_expense"]
                    tax_benefit = restructured_financial_data["financial_expense"]["tax_benefit"]
                    restructured_financial_data["financial_expense"]["after_tax_nfe"] = net_interest - tax_benefit
                    
                    # Balance sheet data
                    if latest_year in grouped_data.get("balance_sheet", {}):
                        balance_data = grouped_data.get("balance_sheet", {}).get(latest_year, {})
                        
                        # Common equity
                        if "StockholdersEquity" in balance_data:
                            restructured_financial_data["summary"]["common_equity"] = balance_data["StockholdersEquity"]
                        
                        # Assets and liabilities approximation
                        if "TotalAssets" in balance_data:
                            # Operating assets
                            
                            # Cash - allocate 20% as operating
                            if "CashAndCashEquivalents" in balance_data:
                                restructured_financial_data["operating_assets"]["cash_and_equivalents"] = balance_data["CashAndCashEquivalents"] * 0.2
                            
                            # Accounts receivable
                            if "AccountsReceivable" in balance_data:
                                restructured_financial_data["operating_assets"]["accounts_receivable"] = balance_data["AccountsReceivable"]
                            
                            # Inventory
                            if "Inventory" in balance_data:
                                restructured_financial_data["operating_assets"]["inventory"] = balance_data["Inventory"]
                            
                            # Other current assets
                            if "OtherCurrentAssets" in balance_data:
                                restructured_financial_data["operating_assets"]["other_current_assets"] = balance_data["OtherCurrentAssets"]
                            
                            # PPE
                            if "PropertyPlantEquipment" in balance_data:
                                restructured_financial_data["operating_assets"]["ppe_net"] = balance_data["PropertyPlantEquipment"]
                            
                            # Intangible assets
                            if "IntangibleAssets" in balance_data:
                                restructured_financial_data["operating_assets"]["intangible_assets"] = balance_data["IntangibleAssets"]
                            elif "Goodwill" in balance_data:
                                # If intangibles not separately reported, use goodwill as approximation
                                restructured_financial_data["operating_assets"]["intangible_assets"] = balance_data["Goodwill"]
                            
                            # Total operating assets - ensure it matches individual components
                            restructured_financial_data["operating_assets"]["total_operating_assets"] = (
                                restructured_financial_data["operating_assets"]["cash_and_equivalents"] +
                                restructured_financial_data["operating_assets"]["accounts_receivable"] +
                                restructured_financial_data["operating_assets"]["inventory"] +
                                restructured_financial_data["operating_assets"]["other_current_assets"] +
                                restructured_financial_data["operating_assets"]["ppe_net"] +
                                restructured_financial_data["operating_assets"]["intangible_assets"]
                            )
                        
                        if "TotalLiabilities" in balance_data:
                            # Operating liabilities
                            
                            # Accounts payable
                            if "AccountsPayable" in balance_data:
                                restructured_financial_data["operating_liabilities"]["accounts_payable"] = balance_data["AccountsPayable"]
                            
                            # Accrued liabilities
                            if "AccruedLiabilities" in balance_data:
                                restructured_financial_data["operating_liabilities"]["accrued_liabilities"] = balance_data["AccruedLiabilities"]
                            elif "OtherCurrentLiabilities" in balance_data:
                                # If not available, use other current liabilities
                                restructured_financial_data["operating_liabilities"]["accrued_liabilities"] = balance_data["OtherCurrentLiabilities"]
                            
                            # Deferred revenue
                            if "DeferredRevenue" in balance_data:
                                restructured_financial_data["operating_liabilities"]["deferred_revenue"] = balance_data["DeferredRevenue"]
                            
                            # Deferred tax liabilities
                            if "DeferredTaxLiabilities" in balance_data:
                                restructured_financial_data["operating_liabilities"]["deferred_tax_liabilities"] = balance_data["DeferredTaxLiabilities"]
                            
                            # Total operating liabilities - ensure it matches individual components
                            restructured_financial_data["operating_liabilities"]["total_operating_liabilities"] = (
                                restructured_financial_data["operating_liabilities"]["accounts_payable"] +
                                restructured_financial_data["operating_liabilities"]["accrued_liabilities"] +
                                restructured_financial_data["operating_liabilities"]["deferred_revenue"] +
                                restructured_financial_data["operating_liabilities"]["deferred_tax_liabilities"]
                            )
                        
                        # Net values
                        restructured_financial_data["summary"]["net_operating_assets"] = (
                            restructured_financial_data["operating_assets"]["total_operating_assets"] - 
                            restructured_financial_data["operating_liabilities"]["total_operating_liabilities"]
                        )
                        
                        # Financial obligations (debt)
                        if "TotalDebt" in balance_data:
                            restructured_financial_data["summary"]["net_financial_obligations"] = balance_data["TotalDebt"]
                            
                            # Try to break down debt into short-term and long-term
                            if "ShortTermDebt" in balance_data:
                                restructured_financial_data["financial_obligations"]["short_term_debt"] = balance_data["ShortTermDebt"]
                            
                            if "LongTermDebt" in balance_data:
                                restructured_financial_data["financial_obligations"]["long_term_debt"] = balance_data["LongTermDebt"]
                            else:
                                # If long term debt not available, estimate from total debt
                                short_term = restructured_financial_data["financial_obligations"]["short_term_debt"]
                                restructured_financial_data["financial_obligations"]["long_term_debt"] = balance_data["TotalDebt"] - short_term
                                
                            # Update total financial obligations
                            restructured_financial_data["financial_obligations"]["total_financial_obligations"] = balance_data["TotalDebt"]
                        
                        # Try to extract financial assets
                        if "CashAndCashEquivalents" in balance_data:
                            # Assume 20% of cash is operational, 80% is excess
                            total_cash = balance_data["CashAndCashEquivalents"]
                            restructured_financial_data["financial_assets"]["excess_cash"] = total_cash * 0.8
                            
                        if "LongTermInvestments" in balance_data:
                            restructured_financial_data["financial_assets"]["long_term_investments"] = balance_data["LongTermInvestments"]
                            
                        # Update total financial assets
                        restructured_financial_data["financial_assets"]["total_financial_assets"] = (
                            restructured_financial_data["financial_assets"]["excess_cash"] +
                            restructured_financial_data["financial_assets"]["long_term_investments"]
                        )
                        
                        # Update accounting check values
                        nfo = restructured_financial_data["summary"]["net_financial_obligations"]
                        cse = restructured_financial_data["summary"]["common_equity"]
                        total_assets = restructured_financial_data["operating_assets"]["total_operating_assets"]
                        
                        # NFO + CSE should theoretically equal Total Assets
                        restructured_financial_data["summary"]["accounting_check"]["nfo_plus_cse"] = nfo + cse
                        restructured_financial_data["summary"]["accounting_check"]["total_assets"] = total_assets
                        restructured_financial_data["summary"]["accounting_check"]["difference"] = (nfo + cse) - total_assets
            except Exception as e:
                logger.warning(f"Error extracting key metrics: {str(e)}")
            
            return restructured_financial_data
        except Exception as e:
            logger.error(f"Error processing financial data: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to process financial data for {ticker}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error reorganizing financial statements: {str(e)}")
        logger.error(traceback.format_exc())
        raise ValueError(f"Failed to process financial data for {ticker}: {str(e)}")

@app.get("/restructured-financials/{ticker}")
def get_restructured_financials(ticker: str):
    """
    Get restructured financial statements separating operating from financing activities
    """
    try:
        logger.info(f"Getting restructured financials for {ticker}")
        
        # Reorganize the financial statements using direct methods
        restructured_data = reorganize_financial_statements(ticker)
        if "error" in restructured_data:
            raise HTTPException(status_code=500, detail=restructured_data["error"])
            
        return restructured_data
        
    except Exception as e:
        logger.error(f"Error getting restructured financials for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/calculate/roce-components/{ticker}")
def calculate_roce_components(ticker: str):
    """
    Calculate ROCE and its components using the framework from the notes
    """
    try:
        logger.info(f"Calculating ROCE components for {ticker}")
        stock = Ticker(ticker)
        
        # Use the more reliable direct methods instead of restructured financials
        try:
            # Fetch income statement and balance sheet directly
            income_statement = stock.income_statement(frequency='a')
            if isinstance(income_statement, str) or income_statement.empty:
                logger.warning(f"No income statement data for {ticker}")
                raise ValueError(f"No income statement data available for {ticker}")
                
            balance_sheet = stock.balance_sheet(frequency='a')
            if isinstance(balance_sheet, str) or balance_sheet.empty:
                logger.warning(f"No balance sheet data for {ticker}")
                raise ValueError(f"No balance sheet data available for {ticker}")
                
            # Get the most recent year's data
            latest_income = income_statement.sort_values('asOfDate', ascending=False).iloc[0]
            latest_balance = balance_sheet.sort_values('asOfDate', ascending=False).iloc[0]
            
            # Extract operating income and net income
            operating_income = 0
            net_income = 0
            for field in ['OperatingIncome', 'EBIT']:
                if field in latest_income and latest_income[field]:
                    operating_income = latest_income[field]
                    break
            
            for field in ['NetIncome']:
                if field in latest_income and latest_income[field]:
                    net_income = latest_income[field]
                    break
            
            # Extract revenue
            total_revenue = 0
            for field in ['TotalRevenue']:
                if field in latest_income and latest_income[field]:
                    total_revenue = latest_income[field]
                    break
            
            # Extract balance sheet values
            common_equity = 0
            for field in ['StockholdersEquity', 'TotalEquity']:
                if field in latest_balance and latest_balance[field]:
                    common_equity = latest_balance[field]
                    break
            
            total_assets = 0
            for field in ['TotalAssets']:
                if field in latest_balance and latest_balance[field]:
                    total_assets = latest_balance[field]
                    break
                    
            total_liabilities = 0
            for field in ['TotalLiabilities']:
                if field in latest_balance and latest_balance[field]:
                    total_liabilities = latest_balance[field]
                    break
            
            net_debt = 0
            for field in ['TotalDebt']:
                if field in latest_balance and latest_balance[field]:
                    net_debt = latest_balance[field]
                    break
                    
            # Calculate derived values
            net_operating_assets = total_assets - total_liabilities if total_assets and total_liabilities else 1
            net_financial_obligations = net_debt if net_debt else 1
            net_financial_expense = operating_income - net_income if operating_income and net_income else 0
            
            # Get additional financial data
            financial_data = stock.financial_data
            key_stats = stock.key_stats

            # Calculate ROCE and its components
            roce = net_income / common_equity if common_equity else 0
            
            # Return on Net Operating Assets (RNOA)
            rnoa = operating_income / net_operating_assets if net_operating_assets else 0
            
            # Financial Leverage (FLEV)
            flev = net_financial_obligations / common_equity if common_equity else 0
            
            # Net Borrowing Cost (NBC)
            nbc = net_financial_expense / net_financial_obligations if net_financial_obligations else 0
            
            # SPREAD
            spread = rnoa - nbc
            
            # Verify ROCE formula: ROCE = RNOA + (FLEV * SPREAD)
            calculated_roce = rnoa + (flev * spread)
            roce_check = {
                "roce": roce,
                "calculated_roce": calculated_roce,
                "difference": roce - calculated_roce
            }
            
            # Calculate Profit Margin (PM) and Asset Turnover (ATO)
            pm = operating_income / total_revenue if total_revenue else 0
            ato = total_revenue / net_operating_assets if net_operating_assets else 0
            
            # Verify RNOA formula: RNOA = PM * ATO
            calculated_rnoa = pm * ato
            rnoa_check = {
                "rnoa": rnoa,
                "calculated_rnoa": calculated_rnoa,
                "difference": rnoa - calculated_rnoa
            }
            
            # Operating Liability Leverage (OLLEV)
            operating_liabilities = total_liabilities if total_liabilities else 0
            operating_assets = total_assets if total_assets else 1
            
            ollev = operating_liabilities / net_operating_assets if net_operating_assets else 0
            
            # Get market data from financial_data and key_stats
            current_price = 0
            if financial_data is not None:
                if isinstance(financial_data, str):
                    logger.warning(f"Financial data is a string, not a dictionary: {financial_data}")
                else:
                    try:
                        ticker_key = ticker.upper()
                        if ticker_key in financial_data:
                            if isinstance(financial_data[ticker_key], dict):
                                current_price = financial_data[ticker_key].get('currentPrice', 0)
                            else:
                                logger.warning(f"Financial data for {ticker_key} is not a dictionary: {financial_data[ticker_key]}")
                    except Exception as e:
                        logger.warning(f"Could not extract current price from financial_data: {str(e)}")
            
            shares_outstanding = 0
            if key_stats is not None:
                if isinstance(key_stats, str):
                    logger.warning(f"Key stats is a string, not a dictionary: {key_stats}")
                else:
                    try:
                        ticker_key = ticker.upper()
                        if ticker_key in key_stats:
                            if isinstance(key_stats[ticker_key], dict):
                                shares_outstanding = key_stats[ticker_key].get('sharesOutstanding', 0)
                            else:
                                logger.warning(f"Key stats for {ticker_key} is not a dictionary: {key_stats[ticker_key]}")
                    except Exception as e:
                        logger.warning(f"Could not extract shares outstanding from key_stats: {str(e)}")
            
            # Market capitalization
            market_cap = current_price * shares_outstanding
            
            # Debt at market value (approximated as book value)
            market_debt = net_financial_obligations
            
            # Cost of capital estimates (simplified)
            cost_of_debt_pretax = 0.05  # 5% pre-tax
            tax_rate = 0.25  # Assumed 25% tax rate
            cost_of_debt = cost_of_debt_pretax * (1 - tax_rate)  # After-tax cost of debt
            
            # Cost of equity (using CAPM approximation)
            beta = 1.0  # Default beta
            if key_stats is not None and not isinstance(key_stats, str):
                try:
                    ticker_key = ticker.upper()
                    if ticker_key in key_stats:
                        beta_value = key_stats[ticker_key].get('beta', 1.0)
                        if beta_value is not None:
                            beta = beta_value
                except:
                    logger.warning(f"Could not extract beta from key_stats")
                    
            risk_free_rate = 0.0158  # 1.58% approximation
            market_risk_premium = 0.0502  # 5.02% approximation
            cost_of_equity = risk_free_rate + (beta * market_risk_premium)
            
            # Cost of capital for operations (WACC)
            total_market_value = market_cap + market_debt
            cost_of_operations = (
                (market_cap / total_market_value) * cost_of_equity + 
                (market_debt / total_market_value) * cost_of_debt
            ) if total_market_value else 0.09  # Default to 9% if can't calculate
            
            return {
                "roce": roce,
                "rnoa": rnoa,
                "flev": flev,
                "nbc": nbc,
                "spread": spread,
                "pm": pm,
                "ato": ato,
                "ollev": ollev,
                "components": {
                    "net_income": net_income,
                    "operating_income": operating_income,
                    "net_financial_expense": net_financial_expense,
                    "common_equity": common_equity,
                    "net_operating_assets": net_operating_assets,
                    "net_financial_obligations": net_financial_obligations,
                    "total_revenue": total_revenue
                },
                "checks": {
                    "roce_check": roce_check,
                    "rnoa_check": rnoa_check
                },
                "cost_of_capital": {
                    "cost_of_equity": cost_of_equity,
                    "cost_of_debt": cost_of_debt,
                    "cost_of_operations": cost_of_operations
                }
            }
        except Exception as inner_e:
            logger.error(f"Error in ROCE calculations: {str(inner_e)}")
            raise ValueError(f"Error calculating ROCE: {str(inner_e)}")
    except Exception as e:
        logger.error(f"Error calculating ROCE components for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating ROCE components: {str(e)}")

@app.get("/calculate/residual-earnings/{ticker}")
def calculate_residual_earnings(ticker: str):
    """
    Calculate Residual Earnings (RE) and Abnormal Earnings Growth (AEG)
    """
    try:
        logger.info(f"Calculating residual earnings for {ticker}")
        
        # Get ROCE components first
        roce_data = calculate_roce_components(ticker)
        
        # Extract necessary values
        common_equity = roce_data["components"]["common_equity"]
        net_income = roce_data["components"]["net_income"]
        cost_of_equity = roce_data["cost_of_capital"]["cost_of_equity"]
        
        # Calculate Residual Earnings (RE)
        residual_earnings = net_income - ((cost_of_equity) * common_equity)
        
        # For Abnormal Earnings Growth (AEG), we need growth forecasts
        # Get earnings estimates from earnings_trend
        stock = Ticker(ticker)
        earnings_trend = stock.earnings_trend
        
        ticker_key = ticker.upper()
        earnings_growth = 0.10  # Default to 10% if not available
        
        # Try to extract growth rate from earnings trend
        if earnings_trend is not None:
            if isinstance(earnings_trend, str):
                logger.warning(f"Earnings trend is a string, not a dictionary: {earnings_trend}")
            elif ticker_key in earnings_trend:
                if isinstance(earnings_trend[ticker_key], dict):
                    trend_data = earnings_trend[ticker_key].get('trend', [])
                    if trend_data and len(trend_data) >= 2:
                        # Get yearly growth rate if available
                        yearly_data = [t for t in trend_data if t.get('period') == '+1y']
                        if yearly_data and isinstance(yearly_data[0], dict) and 'earningsEstimate' in yearly_data[0]:
                            earnings_estimate = yearly_data[0]['earningsEstimate']
                            if isinstance(earnings_estimate, dict) and 'growth' in earnings_estimate:
                                earnings_growth = earnings_estimate['growth']
                else:
                    logger.warning(f"Earnings trend for {ticker_key} is not a dictionary: {earnings_trend[ticker_key]}")
            else:
                logger.warning(f"No earnings trend data found for {ticker_key}")
        
        # Calculate forward earnings
        forward_earnings = net_income * (1 + earnings_growth)
        
        # Calculate Abnormal Earnings Growth (AEG)
        normal_earnings_growth = net_income * cost_of_equity
        aeg = forward_earnings - (net_income * (1 + cost_of_equity))
        
        # Calculate Present Value components for simple valuation
        # For a proper valuation, we would need multiple year forecasts
        required_return = cost_of_equity
        
        # Simple RE valuation (assuming constant RE)
        if required_return > earnings_growth:
            pv_of_re = residual_earnings / (required_return - earnings_growth)
        else:
            pv_of_re = residual_earnings / 0.02  # Default to 2% spread if growth exceeds required return
            
        intrinsic_value_re = common_equity + pv_of_re
        
        # Simple AEG valuation (assuming constant AEG)
        capitalized_forward_earnings = forward_earnings / required_return
        
        if required_return > earnings_growth:
            pv_of_aeg = aeg / (required_return - earnings_growth)
        else:
            pv_of_aeg = aeg / 0.02  # Default to 2% spread
            
        intrinsic_value_aeg = capitalized_forward_earnings + pv_of_aeg
        
        # Get market data from financial_data and key_stats
        stock = Ticker(ticker)
        financial_data = stock.financial_data
        key_stats = stock.key_stats
        
        shares_outstanding = 0
        current_price = 0
        
        if financial_data is not None:
            if isinstance(financial_data, str):
                logger.warning(f"Financial data is a string, not a dictionary: {financial_data}")
            else:
                try:
                    if ticker_key in financial_data:
                        if isinstance(financial_data[ticker_key], dict):
                            current_price = financial_data[ticker_key].get('currentPrice', 0)
                        else:
                            logger.warning(f"Financial data for {ticker_key} is not a dictionary: {financial_data[ticker_key]}")
                except Exception as e:
                    logger.warning(f"Could not extract current price from financial_data: {str(e)}")
        
        if key_stats is not None:
            if isinstance(key_stats, str):
                logger.warning(f"Key stats is a string, not a dictionary: {key_stats}")
            else:
                try:
                    if ticker_key in key_stats:
                        if isinstance(key_stats[ticker_key], dict):
                            shares_outstanding = key_stats[ticker_key].get('sharesOutstanding', 0)
                        else:
                            logger.warning(f"Key stats for {ticker_key} is not a dictionary: {key_stats[ticker_key]}")
                except Exception as e:
                    logger.warning(f"Could not extract shares outstanding from key_stats: {str(e)}")
        
        # Per share values
        if shares_outstanding:
            book_value_per_share = common_equity / shares_outstanding
            eps = net_income / shares_outstanding
            intrinsic_value_per_share_re = intrinsic_value_re / shares_outstanding
            intrinsic_value_per_share_aeg = intrinsic_value_aeg / shares_outstanding
        else:
            book_value_per_share = 0
            eps = 0
            intrinsic_value_per_share_re = 0
            intrinsic_value_per_share_aeg = 0
        
        return {
            "residual_earnings": {
                "value": residual_earnings,
                "formula": "Net Income - (Cost of Equity * Beginning Book Value)",
                "components": {
                    "net_income": net_income,
                    "cost_of_equity": cost_of_equity,
                    "beginning_book_value": common_equity
                }
            },
            "abnormal_earnings_growth": {
                "value": aeg,
                "formula": "Forward Earnings - (Current Earnings * (1 + Cost of Equity))",
                "components": {
                    "forward_earnings": forward_earnings,
                    "current_earnings": net_income,
                    "cost_of_equity": cost_of_equity,
                    "earnings_growth": earnings_growth
                }
            },
            "valuation": {
                "residual_earnings_valuation": {
                    "enterprise_value": intrinsic_value_re,
                    "per_share_value": intrinsic_value_per_share_re,
                    "formula": "Book Value + PV of Future Residual Earnings"
                },
                "abnormal_earnings_growth_valuation": {
                    "enterprise_value": intrinsic_value_aeg,
                    "per_share_value": intrinsic_value_per_share_aeg,
                    "formula": "Capitalized Forward Earnings + PV of Future AEG"
                },
                "market_comparison": {
                    "current_price": current_price,
                    "book_value_per_share": book_value_per_share,
                    "eps": eps,
                    "p_b_ratio": current_price / book_value_per_share if book_value_per_share else 0,
                    "p_e_ratio": current_price / eps if eps else 0
                }
            }
        }
    except Exception as e:
        logger.error(f"Error calculating residual earnings for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating residual earnings: {str(e)}")

@app.get("/api/v1/enterprise_valuation/{ticker}")
async def enterprise_valuation(ticker: str):
    """
    Calculate enterprise valuation metrics for a given ticker
    """
    try:
        logger.info(f"Getting enterprise valuation for {ticker}")
        
        # Get stock price data
        stock = Ticker(ticker)
        price_data = stock.price
        
        # Check if price_data is a valid response
        if isinstance(price_data, str):
            raise ValueError(f"Error getting price data: {price_data}")
            
        if isinstance(price_data, dict) and "error" in price_data:
            raise ValueError(f"Error getting price data: {price_data['error']}")
        
        if not price_data or ticker not in price_data:
            raise ValueError(f"No price data available for {ticker}")
            
        # Check if the ticker data is a dictionary
        if not isinstance(price_data[ticker], dict):
            raise ValueError(f"Price data for {ticker} is not in the expected format: {price_data[ticker]}")
        
        # Get market data
        market_cap = price_data[ticker].get("marketCap")
        current_price = price_data[ticker].get("regularMarketPrice")
        
        if not market_cap or not current_price:
            raise ValueError(f"Missing market cap or price data for {ticker}")
        
        # Get financial statements
        financial_data = await get_financial_statements(ticker, enable_cors=False)
        statements = financial_data.get("financialStatements", {})
        
        # Check if we have both balance sheet and income statement data
        if not statements.get("balance_sheet") or not statements.get("income_statement"):
            missing = []
            if not statements.get("balance_sheet"):
                missing.append("balance sheet")
            if not statements.get("income_statement"):
                missing.append("income statement")
            raise ValueError(f"Missing {', '.join(missing)} data for {ticker}")
        
        # Find the most recent year that has both income statement and balance sheet data
        available_years = sorted([
            year for year in statements["balance_sheet"].keys() 
            if year in statements["income_statement"].keys()
        ], reverse=True)
        
        if not available_years:
            raise ValueError(f"No matching years with complete financial data for {ticker}")
        
        year = available_years[0]
        logger.info(f"Using financial data from year: {year}")
        
        # Get balance sheet items
        balance_sheet = statements["balance_sheet"][year]
        
        # Extract values using different possible keys based on data format
        # For direct method data format
        if isinstance(balance_sheet, dict) and "dataCode" not in balance_sheet:
            # Using get_modules format
            total_debt = extract_value(balance_sheet, ["totalDebt", "longTermDebt"])
            cash_and_equivalents = extract_value(balance_sheet, ["cash", "cashAndCashEquivalents"])
        else:
            # Using direct methods format
            total_debt = extract_direct_value(balance_sheet, ["TotalDebt", "LongTermDebt"])
            cash_and_equivalents = extract_direct_value(balance_sheet, ["Cash", "CashAndCashEquivalents"])
        
        # Get income statement items
        income_statement = statements["income_statement"][year]
        
        # Extract values depending on format
        if isinstance(income_statement, dict) and "dataCode" not in income_statement:
            # Using get_modules format
            revenue = extract_value(income_statement, ["totalRevenue"])
            net_income = extract_value(income_statement, ["netIncome"])
            ebit = extract_value(income_statement, ["ebit", "operatingIncome"])
            
            # Calculate EBITDA if not directly available
            if "ebitda" in income_statement:
                ebitda = extract_value(income_statement, ["ebitda"])
            else:
                depreciation = extract_value(income_statement, ["depreciation"])
                ebitda = ebit + (depreciation if depreciation else 0)
        else:
            # Using direct methods format
            revenue = extract_direct_value(income_statement, ["TotalRevenue"])
            net_income = extract_direct_value(income_statement, ["NetIncome"])
            ebit = extract_direct_value(income_statement, ["EBIT", "OperatingIncome"])
            
            # Calculate EBITDA if not directly available
            ebitda_val = extract_direct_value(income_statement, ["EBITDA"])
            if ebitda_val:
                ebitda = ebitda_val
            else:
                depreciation = extract_direct_value(income_statement, ["Depreciation"])
                ebitda = ebit + (depreciation if depreciation else 0)
        
        # Calculate Enterprise Value
        enterprise_value = market_cap + total_debt - cash_and_equivalents
        
        # Calculate valuation ratios
        ev_to_revenue = enterprise_value / revenue if revenue and revenue != 0 else None
        ev_to_ebit = enterprise_value / ebit if ebit and ebit != 0 else None
        ev_to_ebitda = enterprise_value / ebitda if ebitda and ebitda != 0 else None
        price_to_earnings = current_price / (net_income / price_data[ticker].get("sharesOutstanding")) if net_income and net_income != 0 and price_data[ticker].get("sharesOutstanding") else None
        
        # Format values for display (to millions)
        formatted_market_cap = round(market_cap / 1_000_000, 2)
        formatted_enterprise_value = round(enterprise_value / 1_000_000, 2)
        formatted_revenue = round(revenue / 1_000_000, 2)
        formatted_ebit = round(ebit / 1_000_000, 2) if ebit else None
        formatted_ebitda = round(ebitda / 1_000_000, 2) if ebitda else None
        formatted_net_income = round(net_income / 1_000_000, 2)
        
        # Format ratios (2 decimal places)
        formatted_ev_to_revenue = round(ev_to_revenue, 2) if ev_to_revenue else None
        formatted_ev_to_ebit = round(ev_to_ebit, 2) if ev_to_ebit else None
        formatted_ev_to_ebitda = round(ev_to_ebitda, 2) if ev_to_ebitda else None
        formatted_price_to_earnings = round(price_to_earnings, 2) if price_to_earnings else None
        
        # Build response
        response = {
            "ticker": ticker,
            "year": year,
            "market_metrics": {
                "current_price": round(current_price, 2),
                "market_cap_millions": formatted_market_cap,
                "enterprise_value_millions": formatted_enterprise_value
            },
            "financial_metrics": {
                "revenue_millions": formatted_revenue,
                "ebit_millions": formatted_ebit,
                "ebitda_millions": formatted_ebitda,
                "net_income_millions": formatted_net_income
            },
            "valuation_ratios": {
                "ev_to_revenue": formatted_ev_to_revenue,
                "ev_to_ebit": formatted_ev_to_ebit,
                "ev_to_ebitda": formatted_ev_to_ebitda,
                "price_to_earnings": formatted_price_to_earnings
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating enterprise valuation for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to safely extract values from nested dictionaries for direct method data
def extract_direct_value(data, keys):
    """
    Extract a value from a dictionary using a list of possible keys
    Returns the first value found or None if no keys match
    """
    if not data:
        return None
    
    for key in keys:
        if key in data:
            return data[key]
    
    return None

# Helper function to safely extract values from nested dictionaries for get_modules data
def extract_value(data, keys):
    """
    Extract a value from a nested dictionary using a list of possible keys
    Returns the first value found or None if no keys match
    """
    if not data:
        return None
    
    for key in keys:
        if key in data:
            if isinstance(data[key], dict) and "raw" in data[key]:
                return data[key]["raw"]
            else:
                return data[key]
    
    return None

@app.get("/debug-financial-data/{ticker}")
def debug_financial_data(ticker: str):
    """
    Debug endpoint that returns raw financial data from Yahoo Finance
    to help understand the structure for operational reorganization
    """
    try:
        logger.info(f"Getting debug financial data for {ticker}")
        stock = Ticker(ticker)
        
        # Get financial data using direct methods
        try:
            income_statement = stock.income_statement(frequency='a')
            balance_sheet = stock.balance_sheet(frequency='a')
            cash_flow = stock.cash_flow(frequency='a')
            financial_data = stock.financial_data
            key_stats = stock.key_stats
            
            # Create a dictionary of available data
            debug_info = {
                "ticker": ticker.upper(),
                "data_available": {
                    "income_statement_available": not income_statement.empty if not isinstance(income_statement, str) else False,
                    "balance_sheet_available": not balance_sheet.empty if not isinstance(balance_sheet, str) else False,
                    "cash_flow_available": not cash_flow.empty if not isinstance(cash_flow, str) else False,
                    "financial_data_available": ticker.upper() in financial_data if not isinstance(financial_data, str) else False,
                    "key_stats_available": ticker.upper() in key_stats if not isinstance(key_stats, str) else False
                }
            }
            
            # Add statement counts
            if not isinstance(income_statement, str) and not income_statement.empty:
                debug_info["income_statement_info"] = {
                    "row_count": len(income_statement),
                    "columns": list(income_statement.columns),
                    "sample_row": income_statement.iloc[0].to_dict() if not income_statement.empty else {}
                }
            
            if not isinstance(balance_sheet, str) and not balance_sheet.empty:
                debug_info["balance_sheet_info"] = {
                    "row_count": len(balance_sheet),
                    "columns": list(balance_sheet.columns),
                    "sample_row": balance_sheet.iloc[0].to_dict() if not balance_sheet.empty else {}
                }
            
            if not isinstance(cash_flow, str) and not cash_flow.empty:
                debug_info["cash_flow_info"] = {
                    "row_count": len(cash_flow),
                    "columns": list(cash_flow.columns),
                    "sample_row": cash_flow.iloc[0].to_dict() if not cash_flow.empty else {}
                }
                
            # Add financial data and key stats sample if available
            if not isinstance(financial_data, str) and ticker.upper() in financial_data:
                debug_info["financial_data_sample"] = financial_data[ticker.upper()]
                
            if not isinstance(key_stats, str) and ticker.upper() in key_stats:
                debug_info["key_stats_sample"] = key_stats[ticker.upper()]
            
            logger.info(f"Successfully retrieved debug data for {ticker}")
            return debug_info
        except Exception as inner_e:
            logger.error(f"Error fetching specific data: {str(inner_e)}")
            return {"error": f"Error fetching specific financial data: {str(inner_e)}"}
            
    except Exception as e:
        logger.error(f"Error fetching debug data for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching debug data: {str(e)}")

@app.get("/api/financial-ratios/{ticker}")
async def get_financial_ratios(ticker: str):
    """
    Get key financial ratios for a company
    """
    try:
        financial_data = await get_financial_statements(ticker, enable_cors=False)
        ratios = extract_financial_ratios(financial_data)
        
        if not ratios:
            raise ValueError(f"Could not calculate financial ratios for {ticker}")
            
        return {
            "ticker": ticker,
            "ratios": ratios
        }
    except Exception as e:
        logger.error(f"Error calculating financial ratios for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

async def extract_financial_ratios(financials):
    """
    Extract and calculate key financial ratios from reorganized financial data
    """
    ratios = {}
    
    # Get most recent financial data
    try:
        if not financials or not financials.get('financialStatements'):
            return {}
            
        statements = financials['financialStatements']
        
        # Organize by year instead of by statement
        years = {}
        for statement_type, statement_data in statements.items():
            for date, data in statement_data.items():
                if date not in years:
                    years[date] = {}
                years[date][statement_type] = data
        
        # Get the most recent year with all statements
        recent_years = sorted(years.keys(), reverse=True)
        if not recent_years:
            return {}
            
        # Find the most recent year that has all statement types
        complete_year = None
        for year in recent_years:
            if len(years[year].keys()) >= 3:  # Has income, balance sheet, and cash flow
                complete_year = year
                break
                
        if not complete_year:
            return {}
            
        year_data = years[complete_year]
        
        # Extract key metrics from income statement
        income = year_data.get('income_statement', {})
        revenue = income.get('TotalRevenue', 0)
        gross_profit = income.get('GrossProfit', 0)
        operating_income = income.get('OperatingIncome', 0)
        net_income = income.get('NetIncome', 0)
        ebitda = income.get('EBITDA', 0)
        
        # Extract key metrics from balance sheet
        balance = year_data.get('balance_sheet', {})
        total_assets = balance.get('TotalAssets', 0)
        current_assets = balance.get('CurrentAssets', 0)
        total_liabilities = balance.get('TotalLiabilities', 0)
        current_liabilities = balance.get('CurrentLiabilities', 0)
        total_equity = balance.get('StockholdersEquity', 0)
        cash = balance.get('CashAndCashEquivalents', 0)
        
        # Extract key metrics from cash flow
        cash_flow = year_data.get('cash_flow', {})
        operating_cash_flow = cash_flow.get('OperatingCashFlow', 0)
        capital_expenditure = cash_flow.get('CapitalExpenditure', 0)
        free_cash_flow = operating_cash_flow - abs(capital_expenditure)
        
        # Calculate ratios
        ratios = {
            "profitability": {
                "grossMargin": gross_profit / revenue if revenue else None,
                "operatingMargin": operating_income / revenue if revenue else None,
                "netMargin": net_income / revenue if revenue else None,
                "returnOnAssets": net_income / total_assets if total_assets else None,
                "returnOnEquity": net_income / total_equity if total_equity else None
            },
            "liquidity": {
                "currentRatio": current_assets / current_liabilities if current_liabilities else None,
                "quickRatio": (current_assets - balance.get('Inventory', 0)) / current_liabilities if current_liabilities else None,
                "cashRatio": cash / current_liabilities if current_liabilities else None
            },
            "efficiency": {
                "assetTurnover": revenue / total_assets if total_assets else None,
                "inventoryTurnover": revenue / balance.get('Inventory', 1) if balance.get('Inventory', 0) else None,
                "daysInventory": 365 / (revenue / balance.get('Inventory', 1)) if revenue and balance.get('Inventory', 0) else None
            },
            "cashFlow": {
                "operatingCashFlowToRevenue": operating_cash_flow / revenue if revenue else None,
                "freeCashFlowToRevenue": free_cash_flow / revenue if revenue else None,
                "cashFlowToDebt": operating_cash_flow / balance.get('TotalDebt', 1) if balance.get('TotalDebt', 0) else None
            },
            "growth": {}  # Would need multiple years of data to calculate growth rates
        }
        
        # Add year information
        ratios["year"] = complete_year
        
        return ratios
        
    except Exception as e:
        logger.error(f"Error calculating financial ratios: {str(e)}")
        return {}

@app.get("/api/valuation/{ticker}")
async def get_enterprise_valuation(ticker: str):
    """
    Calculate enterprise valuation metrics for a company
    """
    try:
        # Get stock data
        stock = Ticker(ticker)
        
        # Get price data
        price_data = stock.price
        
        # Check if price_data is a valid response
        if isinstance(price_data, str):
            raise ValueError(f"Error getting price data: {price_data}")
            
        if not price_data or ticker not in price_data:
            raise ValueError(f"No price data available for {ticker}")
            
        # Check if the ticker data is a dictionary
        if not isinstance(price_data[ticker], dict):
            raise ValueError(f"Price data for {ticker} is not in the expected format: {price_data[ticker]}")
            
        market_price = price_data[ticker].get('regularMarketPrice', None)
        market_cap = price_data[ticker].get('marketCap', None)
        
        if not market_price or not market_cap:
            raise ValueError(f"Missing market data for {ticker}")
            
        # Get financial statements
        financial_data = await get_financial_statements(ticker, enable_cors=False)
        if not financial_data or not financial_data.get('financialStatements'):
            raise ValueError(f"No financial statement data available for {ticker}")
        
        # Organize by year instead of by statement
        statements = financial_data['financialStatements']
        years = {}
        for statement_type, statement_data in statements.items():
            for date, data in statement_data.items():
                if date not in years:
                    years[date] = {}
                years[date][statement_type] = data
        
        # Get the most recent year with all statements
        recent_years = sorted(years.keys(), reverse=True)
        if not recent_years:
            raise ValueError(f"No yearly financial data available for {ticker}")
            
        # Find the most recent year that has income statement and balance sheet
        complete_year = None
        for year in recent_years:
            if 'income_statement' in years[year] and 'balance_sheet' in years[year]:
                complete_year = year
                break
                
        if not complete_year:
            raise ValueError(f"No complete financial data available for {ticker}")
            
        year_data = years[complete_year]
        
        # Get income statement data
        income = year_data.get('income_statement', {})
        revenue = income.get('TotalRevenue', 0)
        ebit = income.get('OperatingIncome', 0) 
        net_income = income.get('NetIncome', 0)
        ebitda = income.get('EBITDA', 0)
        
        # Get balance sheet data
        balance = year_data.get('balance_sheet', {})
        total_debt = balance.get('TotalDebt', 0)
        cash_equivalents = balance.get('CashAndCashEquivalents', 0)
        
        # Calculate enterprise value
        enterprise_value = market_cap + total_debt - cash_equivalents
        
        # Calculate valuation ratios
        ev_to_revenue = enterprise_value / revenue if revenue else None
        ev_to_ebit = enterprise_value / ebit if ebit else None
        ev_to_ebitda = enterprise_value / ebitda if ebitda else None
        price_to_earnings = market_cap / net_income if net_income else None
        
        # Format all financial values to millions for readability
        def format_to_millions(value):
            if value is None:
                return None
            return round(value / 1000000, 2)
        
        # Create response
        response = {
            "ticker": ticker,
            "year": complete_year,
            "market_metrics": {
                "price": market_price,
                "market_cap": format_to_millions(market_cap),
                "enterprise_value": format_to_millions(enterprise_value)
            },
            "financial_metrics": {
                "revenue": format_to_millions(revenue),
                "ebit": format_to_millions(ebit),
                "ebitda": format_to_millions(ebitda),
                "net_income": format_to_millions(net_income),
                "total_debt": format_to_millions(total_debt),
                "cash": format_to_millions(cash_equivalents)
            },
            "valuation_ratios": {
                "ev_to_revenue": round(ev_to_revenue, 2) if ev_to_revenue else None,
                "ev_to_ebit": round(ev_to_ebit, 2) if ev_to_ebit else None,
                "ev_to_ebitda": round(ev_to_ebitda, 2) if ev_to_ebitda else None,
                "price_to_earnings": round(price_to_earnings, 2) if price_to_earnings else None
            }
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating enterprise valuation for {ticker}: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 