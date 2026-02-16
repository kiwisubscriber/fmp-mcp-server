# FMP Stock Data MCP Server

A remote MCP (Model Context Protocol) server that connects Claude to Financial Modeling Prep stock data.

## Tools Available

- **search_company** — Find ticker symbols by company name
- **screen_stocks** — Screen stocks by country, sector, market cap, dividend yield, beta, etc.
- **get_company_profile** — Company description, sector, market cap, CEO, employees
- **get_income_statement** — Revenue, profits, EPS, EBITDA
- **get_balance_sheet** — Assets, liabilities, equity, debt, goodwill
- **get_cash_flow** — Operating cash flow, capex, FCF, dividends paid, buybacks
- **get_key_metrics** — ROIC, ROE, ROA, PE, PB, dividend yield, payout ratio, EV/EBITDA
- **get_financial_ratios** — Profitability, liquidity, leverage, efficiency, valuation ratios
- **get_financial_scores** — Altman Z-Score, Piotroski F-Score
- **get_financial_growth** — Revenue, earnings, dividend, FCF growth rates
- **get_dividend_history** — Historical dividend payments and dates
- **get_stock_quote** — Current price, volume, 52-week range
- **get_stock_peers** — Comparable companies
- **get_analyst_estimates** — Consensus revenue, EPS, EBITDA estimates
- **get_enterprise_value** — EV breakdown (market cap, debt, cash)
- **get_shares_float** — Float and outstanding shares
- **get_company_rating** — Overall financial rating (S/A/B/C/D)

## Setup

1. Get an API key from [Financial Modeling Prep](https://financialmodelingprep.com)
2. Deploy to Railway (or any cloud platform)
3. Set the `FMP_API_KEY` environment variable
4. Connect the URL to Claude via Settings → Connectors

## Environment Variables

- `FMP_API_KEY` — Your Financial Modeling Prep API key (required)
- `PORT` — Server port (set automatically by Railway)
