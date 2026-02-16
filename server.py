import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP(
    "FMP Stock Data",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
    instructions=(
        "Financial data tools powered by Financial Modeling Prep. "
        "Use these tools to screen stocks, get financial statements, key metrics, "
        "ratios, scores, dividends, and quotes for any publicly traded company globally.\n\n"
        "For Japanese stocks use exchange 'JPX' or country 'JP'.\n"
        "For Swiss/Liechtenstein stocks use exchange 'SIX' or country 'CH'.\n"
        "For Singapore stocks use exchange 'SGX' or country 'SG'.\n"
        "For UK stocks use exchange 'LSE' or country 'GB'.\n"
        "For Australian stocks use exchange 'ASX' or country 'AU'.\n"
        "For German stocks use exchange 'XETRA' or country 'DE'.\n"
        "For French stocks use exchange 'EURONEXT' or country 'FR'.\n"
    ),
)

FMP_API_KEY = os.environ.get("FMP_API_KEY", "")
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


async def fmp_get(endpoint: str, params: dict | None = None) -> list | dict:
    """Make a GET request to the FMP API."""
    if not FMP_API_KEY:
        return {"error": "FMP_API_KEY environment variable not set"}

    request_params = params.copy() if params else {}
    request_params["apikey"] = FMP_API_KEY

    async with httpx.AsyncClient(timeout=30) as client:
        url = f"{FMP_BASE_URL}/{endpoint}"
        response = await client.get(url, params=request_params)

        if response.status_code == 401:
            return {"error": "Invalid FMP API key"}
        if response.status_code == 403:
            return {"error": "FMP API access denied - may need upgraded plan"}
        if response.status_code == 429:
            return {"error": "FMP API rate limit reached - try again later"}

        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# Tool: Search for a company by name
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_company(query: str, limit: int = 10) -> str:
    """Search for a company by name to find its ticker symbol.

    Useful for finding the correct ticker for international companies.
    Example: search 'Tokio Marine' to find '8766.T'
    Example: search 'Shin-Etsu' to find '4063.T'
    Example: search 'Liechtensteinische Landesbank' to find 'LLBN.SW'
    """
    data = await fmp_get("search", {"query": query, "limit": limit})
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Screen stocks
# ---------------------------------------------------------------------------
@mcp.tool()
async def screen_stocks(
    country: str | None = None,
    sector: str | None = None,
    industry: str | None = None,
    exchange: str | None = None,
    market_cap_more_than: int | None = None,
    market_cap_less_than: int | None = None,
    dividend_more_than: float | None = None,
    dividend_less_than: float | None = None,
    beta_more_than: float | None = None,
    beta_less_than: float | None = None,
    volume_more_than: int | None = None,
    price_more_than: float | None = None,
    price_less_than: float | None = None,
    limit: int = 50,
) -> str:
    """Screen stocks by fundamental criteria.

    Sectors: Technology, Healthcare, Financial Services, Consumer Cyclical,
    Consumer Defensive, Industrials, Energy, Basic Materials, Real Estate,
    Utilities, Communication Services

    Exchanges: NYSE, NASDAQ, AMEX, EURONEXT, TSX, LSE, XETRA, NSE, SGX,
    HKEX, JPX, SIX, ASX

    Countries: US, GB, JP, CH, SG, HK, AU, DE, FR, CA, IN (ISO 2-letter)

    Returns list of matching stocks with symbol, name, market cap, sector,
    industry, beta, price, dividend yield, volume, exchange, country.
    """
    params: dict = {"limit": limit}

    if country:
        params["country"] = country
    if sector:
        params["sector"] = sector
    if industry:
        params["industry"] = industry
    if exchange:
        params["exchange"] = exchange
    if market_cap_more_than is not None:
        params["marketCapMoreThan"] = market_cap_more_than
    if market_cap_less_than is not None:
        params["marketCapLessThan"] = market_cap_less_than
    if dividend_more_than is not None:
        params["dividendMoreThan"] = dividend_more_than
    if dividend_less_than is not None:
        params["dividendLessThan"] = dividend_less_than
    if beta_more_than is not None:
        params["betaMoreThan"] = beta_more_than
    if beta_less_than is not None:
        params["betaLessThan"] = beta_less_than
    if volume_more_than is not None:
        params["volumeMoreThan"] = volume_more_than
    if price_more_than is not None:
        params["priceMoreThan"] = price_more_than
    if price_less_than is not None:
        params["priceLessThan"] = price_less_than

    data = await fmp_get("stock-screener", params)
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Company profile
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_company_profile(symbol: str) -> str:
    """Get company profile: description, sector, industry, market cap, CEO,
    employees, website, country, currency, exchange, and key statistics.

    International ticker examples:
    - Japan: '8766.T' (Tokio Marine), '4063.T' (Shin-Etsu)
    - SIX Swiss: 'LLBN.SW' (Liechtensteinische Landesbank)
    - Singapore: 'D05.SI' (DBS Group)
    - UK: 'GSK.L' (GSK)
    - Australia: 'BHP.AX' (BHP)
    - Germany: 'SAP.DE' (SAP)
    - France: 'SAN.PA' (Sanofi)
    """
    data = await fmp_get(f"profile/{symbol}")
    if isinstance(data, list) and len(data) > 0:
        return json.dumps(data[0], indent=2)
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Income statement
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_income_statement(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get income statement data.

    Args:
        symbol: Stock ticker (e.g. 'AAPL', '8766.T')
        period: 'annual' or 'quarter'
        limit: Number of periods (default 5)

    Returns revenue, cost of revenue, gross profit, operating expenses,
    operating income, net income, EPS, diluted EPS, EBITDA, and more.
    """
    data = await fmp_get(
        f"income-statement/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Balance sheet
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_balance_sheet(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get balance sheet data.

    Returns total assets, current assets, cash, total liabilities,
    current liabilities, total debt, total equity, goodwill,
    intangible assets, shares outstanding, and more.
    """
    data = await fmp_get(
        f"balance-sheet-statement/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Cash flow statement
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_cash_flow(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get cash flow statement.

    Returns operating cash flow, capital expenditure, free cash flow,
    dividends paid, share repurchases (buybacks), acquisitions,
    debt repayment, and more.
    """
    data = await fmp_get(
        f"cash-flow-statement/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Key metrics
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_key_metrics(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get key financial metrics.

    Returns ROIC, ROE, ROA, revenue per share, net income per share,
    operating cash flow per share, free cash flow per share, book value
    per share, debt to equity, debt to assets, interest coverage,
    PE ratio, PB ratio, dividend yield, payout ratio, enterprise value,
    EV/EBITDA, EV/FCF, earnings yield, FCF yield, and more.
    """
    data = await fmp_get(
        f"key-metrics/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Financial ratios
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_financial_ratios(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get financial ratios.

    Profitability: gross margin, operating margin, net margin, ROE, ROA, ROIC
    Liquidity: current ratio, quick ratio, cash ratio
    Leverage: debt/equity, debt/assets, interest coverage
    Efficiency: asset turnover, inventory turnover, receivables turnover
    Valuation: PE, PB, P/S, P/FCF, EV/EBITDA, PEG
    Dividends: dividend yield, payout ratio, dividend per share
    """
    data = await fmp_get(
        f"ratios/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Financial scores (Piotroski, Altman Z)
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_financial_scores(symbol: str) -> str:
    """Get financial health scores.

    Returns Altman Z-Score and Piotroski F-Score.
    Altman Z-Score: >2.99 safe, 1.8-2.99 grey zone, <1.8 distress
    Piotroski F-Score: 7-9 strong, 4-6 moderate, 0-3 weak
    """
    data = await fmp_get("score", {"symbol": symbol})
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Financial growth rates
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_financial_growth(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get financial growth rates.

    Returns revenue growth, net income growth, EPS growth, dividend growth,
    operating cash flow growth, free cash flow growth, gross profit growth,
    debt growth, shares outstanding growth, and more.

    Useful for checking if dividend growth is outpacing FCF growth.
    """
    data = await fmp_get(
        f"financial-growth/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Dividend history
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_dividend_history(symbol: str) -> str:
    """Get historical dividend payments.

    Returns list of dividend payments with declaration date, record date,
    payment date, and amount. Useful for assessing dividend consistency,
    growth track record, and identifying any cuts or freezes.
    """
    data = await fmp_get(f"historical-price-full/stock_dividend/{symbol}")
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Current stock quote
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """Get current stock quote and key stats.

    Returns current price, change, percent change, volume, avg volume,
    market cap, PE ratio, EPS, 52-week high/low, dividend yield,
    shares outstanding, and more.

    Accepts multiple comma-separated symbols: 'AAPL,MSFT,GOOGL'
    """
    data = await fmp_get(f"quote/{symbol}")
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Peer companies
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_stock_peers(symbol: str) -> str:
    """Get peer/comparable companies.

    Returns list of ticker symbols in the same sector/industry.
    Useful for finding comparables for valuation analysis.
    """
    data = await fmp_get("stock_peers", {"symbol": symbol})
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Analyst estimates
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_analyst_estimates(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get analyst consensus estimates.

    Returns estimated revenue, EPS, EBITDA, net income, SGA expense
    with high/low/average/number of analysts for each metric.
    """
    data = await fmp_get(
        f"analyst-estimates/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Enterprise value
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_enterprise_value(
    symbol: str, period: str = "annual", limit: int = 5
) -> str:
    """Get enterprise value breakdown.

    Returns market cap, total debt, cash and equivalents, minority interest,
    preferred stock, enterprise value, shares outstanding, and stock price.
    """
    data = await fmp_get(
        f"enterprise-values/{symbol}", {"period": period, "limit": limit}
    )
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Shares float
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_shares_float(symbol: str) -> str:
    """Get shares float and outstanding data.

    Returns free float, float shares, outstanding shares.
    Useful for checking share dilution trends over time.
    """
    data = await fmp_get("shares_float", {"symbol": symbol})
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Tool: Rating
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_company_rating(symbol: str) -> str:
    """Get company rating based on financial indicators.

    Returns overall rating and individual scores for DCF, ROE, ROA,
    DE (debt/equity), PE, and PB ratios. Each scored as S/A/B/C/D.
    """
    data = await fmp_get(f"rating/{symbol}")
    return json.dumps(data, indent=2)


# ---------------------------------------------------------------------------
# Run the server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
