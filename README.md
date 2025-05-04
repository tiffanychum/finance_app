# Fundamental Analysis App

A comprehensive financial analysis application that implements the 5-step fundamental analysis framework to analyze stocks and calculate their intrinsic value.

## Overview

This application helps investors analyze companies using a structured approach to fundamental analysis. The app separates operations from financing activities to better understand a company's true operational performance and valuation.

### The Five Steps of Fundamental Analysis

1. **Knowing the Business**: Understanding products, technology, competition, management, and the regulatory environment.
2. **Analyzing Information**: Reviewing financial statements and other relevant data, focusing on separating operations from financing.
3. **Forecasting Payoffs**: Predicting future financial performance (e.g., earnings, cash flows).
4. **Convert Forecasts to a Valuation**: Using models to estimate the firm's intrinsic value.
5. **Trading on the Valuation**: Making investment decisions based on comparing the estimated value to the market price.

## Key Features

- **Restructured Financial Statements**: Separates operating activities from financing activities
- **ROCE Decomposition**: Analyzes Return on Common Equity using the formula ROCE = RNOA + (FLEV × SPREAD)
- **Multiple Valuation Models**:
  - Residual Earnings (RE) Model: V₀ = CSE₀ + PV of future RE
  - Abnormal Earnings Growth (AEG) Model: V₀ = Earnings₁/(ρₑ-1) + PV of future AEG
  - Enterprise Valuation using Residual Operating Income (ReOI): V₀ᵒᵖᵉʳᵃᵗⁱᵒⁿˢ = NOA₀ + PV of future ReOI

## Technology Stack

- **Frontend**: Next.js with TypeScript and TailwindCSS
- **Backend**: FastAPI (Python)
- **Data**: Yahoo Finance API via yahooquery

## Getting Started

### Prerequisites

- Node.js (v14+)
- Python (v3.8+)
- npm or yarn

### Installation and Running

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/FinanceApp_v1.git
   cd FinanceApp_v1
   ```

2. Run the application using the run script:
   ```
   ./run.sh
   ```

   This will:
   - Create a Python virtual environment if needed
   - Install backend dependencies
   - Install frontend dependencies
   - Start both the frontend and backend servers

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## Implementation Details

### Financial Statement Reorganization

The app reorganizes traditional financial statements to separate:

- **Operating Activities**: Activities related to the core business operations
  - Operating Assets (OA): Assets used in operations
  - Operating Liabilities (OL): Liabilities from operations
  - Net Operating Assets (NOA): OA - OL
  - Operating Income (OI): Revenue generated from operations

- **Financing Activities**: Activities related to raising capital
  - Financial Assets (FA): Cash and investments not needed for operations
  - Financial Obligations (FO): Debt and other financial liabilities
  - Net Financial Obligations (NFO): FO - FA
  - Net Financial Expense (NFE): Interest and related expenses

### ROCE Decomposition

Return on Common Equity (ROCE) is decomposed using the formula:
```
ROCE = RNOA + (FLEV × SPREAD)
```

Where:
- RNOA (Return on Net Operating Assets) = OI / NOA
- FLEV (Financial Leverage) = NFO / CSE
- SPREAD = RNOA - NBC (Net Borrowing Cost)

RNOA is further decomposed as:
```
RNOA = PM × ATO
```

Where:
- PM (Profit Margin) = OI / Sales
- ATO (Asset Turnover) = Sales / NOA

### Valuation Models

The app implements three main valuation models:

1. **Residual Earnings (RE)** Valuation:
   ```
   V₀ = CSE₀ + PV of future RE
   ```
   Where RE = Earnings - (Cost of Equity × Beginning Book Value)

2. **Abnormal Earnings Growth (AEG)** Valuation:
   ```
   V₀ = Earnings₁/(ρₑ-1) + PV of future AEG
   ```
   Where AEG = Forward Earnings - (Current Earnings × (1 + Cost of Equity))

3. **Enterprise Valuation** using ReOI:
   ```
   V₀ᵒᵖᵉʳᵃᵗⁱᵒⁿˢ = NOA₀ + PV of future ReOI
   V₀ᵉᑫᵘⁱᵗʸ = V₀ᵒᵖᵉʳᵃᵗⁱᵒⁿˢ - NFO
   ```
   Where ReOI = Operating Income - (Cost of Operations × Net Operating Assets)

## License

MIT

## Acknowledgments

Based on the fundamental analysis framework from "Financial Statement Analysis and Security Valuation" by Stephen H. Penman. 