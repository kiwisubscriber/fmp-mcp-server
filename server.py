import os
import json
import yfinance as yf
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP(
    "Stock Data",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 8000)),
    instructions=(
        "Free global stock data tools powered by Yahoo Finance. "
        "Use these tools to get financial statements, key metrics, "
        "ratios, dividends, and quotes for any publicly traded company globally.\n\n"
        "Ticker format examples:\n"
        "- US: 'AAPL', 'MSFT', 'COP'\n"
        "- Japan: '8766.T' (Tokio Marine), '4063.T' (Shin-Etsu), '8001.T' (ITOCHU)\n"
        "- Swiss/Liechtenstein: 'LLBN.SW' (LLB), 'NESN.SW' (Nestle)\n"
        "- Singapore: 'D05.SI' (DBS), 'O39.SI' (OCBC)\n"
        "- UK: 'GSK.L' (GSK), 'AZN.L' (AstraZeneca)\n"
        "- Australia: 'BHP.AX' (BHP), 'CBA.AX' (CommBank)\n"
        "- Germany: 'SAP.DE' (SAP)\n"
        "- France: 'SAN.PA' (Sanofi)\n"
        "- Hong Kong: '0005.HK' (HSBC)\n"
    ),
)


def safe_json(data) -> str:
    """Convert data to JSON, handling NaN and other non-serializable values."""
    if data is None:
        return json.dumps({"error": "No data returned"})
    if hasattr(data, "to_dict"):
        data = data.to_dict()
    return json.dumps(data, indent=2, default=str)


def ticker_info(symbol: str) -> dict:
    """Get ticker info with error handling."""
    try:
        t = yf.Ticker(symbol)
        info = t.info
        if not info or info.get("trailingPegRatio") is None and len(info) < 5:
            return {"error": f"No data found for {symbol}. Check the ticker symbol."}
        return info
    except Exception as e:
        return {"error": f"Failed to fetch data for {symbol}: {str(e)}"}


# ---------------------------------------------------------------------------
# Tool: Search for a company ticker
# ---------------------------------------------------------------------------
@mcp.tool()
async def search_company(query: str) -> str:
    """Search for a company by name to find its ticker symbol.

    Uses Yahoo Finance search. Returns matching tickers with names and exchanges.
    Example: search 'Tokio Marine' to find '8766.T'
    """
    try:
        results = yf.Search(query)
        quotes = []
        if hasattr(results, "quotes") and results.quotes:
            for q in results.quotes[:10]:
                quotes.append({
                    "symbol": q.get("symbol", ""),
                    "name": q.get("shortname", q.get("longname", "")),
                    "exchange": q.get("exchange", ""),
                    "type": q.get("quoteType", ""),
                })
        return json.dumps(quotes, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Search failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Company profile
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_company_profile(symbol: str) -> str:
    """Get company profile and key statistics.

    Returns sector, industry, country, market cap, employees, description,
    currency, exchange, dividend yield, PE ratio, beta, 52-week range, and more.

    Use exchange suffixes: .T (Japan), .SW (Swiss), .SI (Singapore),
    .L (UK), .AX (Australia), .DE (Germany), .PA (France), .HK (Hong Kong)
    """
    info = ticker_info(symbol)
    if "error" in info:
        return json.dumps(info)

    profile = {
        "symbol": symbol,
        "name": info.get("longName", ""),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "country": info.get("country", ""),
        "currency": info.get("currency", ""),
        "exchange": info.get("exchange", ""),
        "marketCap": info.get("marketCap"),
        "employees": info.get("fullTimeEmployees"),
        "website": info.get("website", ""),
        "description": info.get("longBusinessSummary", ""),
        "beta": info.get("beta"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "dividendYield": info.get("dividendYield"),
        "dividendRate": info.get("dividendRate"),
        "payoutRatio": info.get("payoutRatio"),
        "priceToBook": info.get("priceToBook"),
        "enterpriseValue": info.get("enterpriseValue"),
        "profitMargins": info.get("profitMargins"),
        "grossMargins": info.get("grossMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        "debtToEquity": info.get("debtToEquity"),
        "currentRatio": info.get("currentRatio"),
        "quickRatio": info.get("quickRatio"),
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        "totalRevenue": info.get("totalRevenue"),
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "targetMeanPrice": info.get("targetMeanPrice"),
        "recommendationKey": info.get("recommendationKey"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        "currentPrice": info.get("currentPrice"),
        "sharesOutstanding": info.get("sharesOutstanding"),
        "floatShares": info.get("floatShares"),
        "heldPercentInsiders": info.get("heldPercentInsiders"),
        "heldPercentInstitutions": info.get("heldPercentInstitutions"),
        "shortRatio": info.get("shortRatio"),
        "shortPercentOfFloat": info.get("shortPercentOfFloat"),
    }
    return json.dumps(profile, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool: Income statement
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_income_statement(
    symbol: str, period: str = "annual"
) -> str:
    """Get income statement data.

    Args:
        symbol: Stock ticker (e.g. 'AAPL', '8766.T')
        period: 'annual' or 'quarterly'

    Returns revenue, cost of revenue, gross profit, operating income,
    net income, EPS, EBITDA, and more for the last 4 periods.
    """
    try:
        t = yf.Ticker(symbol)
        if period == "quarterly":
            df = t.quarterly_financials
        else:
            df = t.financials

        if df is None or df.empty:
            return json.dumps({"error": f"No income statement data for {symbol}"})

        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d")
            result[period_key] = {}
            for idx in df.index:
                val = df.loc[idx, col]
                result[period_key][idx] = None if str(val) == "nan" else val

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Balance sheet
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_balance_sheet(
    symbol: str, period: str = "annual"
) -> str:
    """Get balance sheet data.

    Returns total assets, current assets, cash, total liabilities,
    current liabilities, total debt, total equity, goodwill,
    intangible assets, shares outstanding, and more.
    """
    try:
        t = yf.Ticker(symbol)
        if period == "quarterly":
            df = t.quarterly_balance_sheet
        else:
            df = t.balance_sheet

        if df is None or df.empty:
            return json.dumps({"error": f"No balance sheet data for {symbol}"})

        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d")
            result[period_key] = {}
            for idx in df.index:
                val = df.loc[idx, col]
                result[period_key][idx] = None if str(val) == "nan" else val

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Cash flow statement
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_cash_flow(
    symbol: str, period: str = "annual"
) -> str:
    """Get cash flow statement.

    Returns operating cash flow, capital expenditure, free cash flow,
    dividends paid, share repurchases (buybacks), acquisitions,
    debt repayment, and more.
    """
    try:
        t = yf.Ticker(symbol)
        if period == "quarterly":
            df = t.quarterly_cashflow
        else:
            df = t.cashflow

        if df is None or df.empty:
            return json.dumps({"error": f"No cash flow data for {symbol}"})

        result = {}
        for col in df.columns:
            period_key = col.strftime("%Y-%m-%d")
            result[period_key] = {}
            for idx in df.index:
                val = df.loc[idx, col]
                result[period_key][idx] = None if str(val) == "nan" else val

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Key metrics from info
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_key_metrics(symbol: str) -> str:
    """Get key financial metrics and valuation ratios.

    Returns PE, forward PE, PEG, P/B, P/S, EV/EBITDA, EV/Revenue,
    dividend yield, payout ratio, ROE, ROA, profit margins,
    debt/equity, current ratio, free cash flow, and more.
    """
    info = ticker_info(symbol)
    if "error" in info:
        return json.dumps(info)

    metrics = {
        "symbol": symbol,
        "name": info.get("longName", ""),
        "currency": info.get("currency", ""),
        "currentPrice": info.get("currentPrice"),
        "marketCap": info.get("marketCap"),
        # Valuation
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "pegRatio": info.get("pegRatio"),
        "priceToBook": info.get("priceToBook"),
        "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),
        "enterpriseToRevenue": info.get("enterpriseToRevenue"),
        "enterpriseToEbitda": info.get("enterpriseToEbitda"),
        "enterpriseValue": info.get("enterpriseValue"),
        "trailingEps": info.get("trailingEps"),
        "forwardEps": info.get("forwardEps"),
        "earningsYield": round(1 / info["trailingPE"], 4) if info.get("trailingPE") and info["trailingPE"] > 0 else None,
        # Profitability
        "grossMargins": info.get("grossMargins"),
        "operatingMargins": info.get("operatingMargins"),
        "profitMargins": info.get("profitMargins"),
        "returnOnEquity": info.get("returnOnEquity"),
        "returnOnAssets": info.get("returnOnAssets"),
        # Balance sheet
        "debtToEquity": info.get("debtToEquity"),
        "currentRatio": info.get("currentRatio"),
        "quickRatio": info.get("quickRatio"),
        "totalDebt": info.get("totalDebt"),
        "totalCash": info.get("totalCash"),
        "totalCashPerShare": info.get("totalCashPerShare"),
        "bookValue": info.get("bookValue"),
        # Cash flow
        "freeCashflow": info.get("freeCashflow"),
        "operatingCashflow": info.get("operatingCashflow"),
        # Dividends
        "dividendYield": info.get("dividendYield"),
        "dividendRate": info.get("dividendRate"),
        "payoutRatio": info.get("payoutRatio"),
        "exDividendDate": info.get("exDividendDate"),
        "lastDividendValue": info.get("lastDividendValue"),
        "lastDividendDate": info.get("lastDividendDate"),
        "fiveYearAvgDividendYield": info.get("fiveYearAvgDividendYield"),
        # Growth
        "revenueGrowth": info.get("revenueGrowth"),
        "earningsGrowth": info.get("earningsGrowth"),
        "earningsQuarterlyGrowth": info.get("earningsQuarterlyGrowth"),
        "revenueQuarterlyGrowth": info.get("revenueQuarterlyGrowth"),
        # Revenue
        "totalRevenue": info.get("totalRevenue"),
        "revenuePerShare": info.get("revenuePerShare"),
        # Risk
        "beta": info.get("beta"),
        "shortRatio": info.get("shortRatio"),
        "shortPercentOfFloat": info.get("shortPercentOfFloat"),
        # Shares
        "sharesOutstanding": info.get("sharesOutstanding"),
        "floatShares": info.get("floatShares"),
        "heldPercentInsiders": info.get("heldPercentInsiders"),
        "heldPercentInstitutions": info.get("heldPercentInstitutions"),
        # Analyst
        "targetMeanPrice": info.get("targetMeanPrice"),
        "targetHighPrice": info.get("targetHighPrice"),
        "targetLowPrice": info.get("targetLowPrice"),
        "recommendationKey": info.get("recommendationKey"),
        "numberOfAnalystOpinions": info.get("numberOfAnalystOpinions"),
    }
    return json.dumps(metrics, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool: Dividend history
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_dividend_history(symbol: str) -> str:
    """Get historical dividend payments.

    Returns list of dividend payments with dates and amounts.
    Useful for assessing dividend consistency, growth track record,
    and identifying any cuts or freezes.
    """
    try:
        t = yf.Ticker(symbol)
        divs = t.dividends

        if divs is None or divs.empty:
            return json.dumps({"symbol": symbol, "dividends": [], "message": "No dividend history found"})

        result = {
            "symbol": symbol,
            "dividendCount": len(divs),
            "dividends": []
        }
        for date, amount in divs.items():
            result["dividends"].append({
                "date": date.strftime("%Y-%m-%d"),
                "amount": round(float(amount), 6)
            })

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Stock quote
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_stock_quote(symbol: str) -> str:
    """Get current stock quote and key stats.

    Returns current price, change, volume, market cap, PE, EPS,
    52-week high/low, dividend yield, and more.

    For multiple stocks, call this tool once per ticker.
    """
    info = ticker_info(symbol)
    if "error" in info:
        return json.dumps(info)

    quote = {
        "symbol": symbol,
        "name": info.get("longName", ""),
        "currency": info.get("currency", ""),
        "currentPrice": info.get("currentPrice"),
        "previousClose": info.get("previousClose"),
        "open": info.get("open"),
        "dayHigh": info.get("dayHigh"),
        "dayLow": info.get("dayLow"),
        "volume": info.get("volume"),
        "averageVolume": info.get("averageVolume"),
        "marketCap": info.get("marketCap"),
        "trailingPE": info.get("trailingPE"),
        "forwardPE": info.get("forwardPE"),
        "trailingEps": info.get("trailingEps"),
        "dividendYield": info.get("dividendYield"),
        "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh"),
        "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow"),
        "fiftyDayAverage": info.get("fiftyDayAverage"),
        "twoHundredDayAverage": info.get("twoHundredDayAverage"),
        "sharesOutstanding": info.get("sharesOutstanding"),
    }
    return json.dumps(quote, indent=2, default=str)


# ---------------------------------------------------------------------------
# Tool: Holders / ownership
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_holders(symbol: str) -> str:
    """Get major holders and institutional ownership data.

    Returns top institutional holders, top mutual fund holders,
    and insider/institutional ownership percentages.
    """
    try:
        t = yf.Ticker(symbol)
        result = {"symbol": symbol}

        # Major holders summary
        mh = t.major_holders
        if mh is not None and not mh.empty:
            result["majorHolders"] = {}
            for _, row in mh.iterrows():
                result["majorHolders"][str(row.iloc[1])] = str(row.iloc[0])

        # Top institutional holders
        ih = t.institutional_holders
        if ih is not None and not ih.empty:
            result["topInstitutionalHolders"] = ih.head(10).to_dict(orient="records")

        # Top mutual fund holders
        mfh = t.mutualfund_holders
        if mfh is not None and not mfh.empty:
            result["topMutualFundHolders"] = mfh.head(10).to_dict(orient="records")

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Analyst recommendations
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_analyst_recommendations(symbol: str) -> str:
    """Get analyst recommendations and price targets.

    Returns recent analyst ratings (buy/hold/sell),
    price target data, and recommendation trends.
    """
    try:
        t = yf.Ticker(symbol)
        result = {"symbol": symbol}

        # Recommendations
        recs = t.recommendations
        if recs is not None and not recs.empty:
            recent = recs.tail(20)
            result["recommendations"] = recent.to_dict(orient="records")

        # Info-based targets
        info = t.info
        if info:
            result["targetMeanPrice"] = info.get("targetMeanPrice")
            result["targetHighPrice"] = info.get("targetHighPrice")
            result["targetLowPrice"] = info.get("targetLowPrice")
            result["recommendationKey"] = info.get("recommendationKey")
            result["numberOfAnalystOpinions"] = info.get("numberOfAnalystOpinions")

        return json.dumps(result, indent=2, default=str)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Price history
# ---------------------------------------------------------------------------
@mcp.tool()
async def get_price_history(
    symbol: str, period: str = "1y", interval: str = "1mo"
) -> str:
    """Get historical price data.

    Args:
        symbol: Stock ticker
        period: '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'max'
        interval: '1d', '1wk', '1mo'

    Returns OHLCV data (open, high, low, close, volume) for each period.
    """
    try:
        t = yf.Ticker(symbol)
        hist = t.history(period=period, interval=interval)

        if hist is None or hist.empty:
            return json.dumps({"error": f"No price history for {symbol}"})

        result = {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "dataPoints": len(hist),
            "prices": []
        }
        for date, row in hist.iterrows():
            result["prices"].append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 4),
                "high": round(float(row["High"]), 4),
                "low": round(float(row["Low"]), 4),
                "close": round(float(row["Close"]), 4),
                "volume": int(row["Volume"]),
            })

        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool: Compare multiple stocks
# ---------------------------------------------------------------------------
@mcp.tool()
async def compare_stocks(symbols: str) -> str:
    """Compare key metrics across multiple stocks.

    Args:
        symbols: Comma-separated ticker symbols, e.g. '8766.T,4063.T,8001.T'

    Returns a side-by-side comparison of PE, dividend yield, ROE, margins,
    debt/equity, beta, market cap, and more for each stock.
    """
    tickers = [s.strip() for s in symbols.split(",")]
    results = []

    for sym in tickers[:10]:  # Max 10 stocks
        info = ticker_info(sym)
        if "error" in info:
            results.append({"symbol": sym, "error": info["error"]})
            continue

        results.append({
            "symbol": sym,
            "name": info.get("longName", ""),
            "currency": info.get("currency", ""),
            "currentPrice": info.get("currentPrice"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "priceToBook": info.get("priceToBook"),
            "enterpriseToEbitda": info.get("enterpriseToEbitda"),
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),
            "grossMargins": info.get("grossMargins"),
            "operatingMargins": info.get("operatingMargins"),
            "profitMargins": info.get("profitMargins"),
            "returnOnEquity": info.get("returnOnEquity"),
            "returnOnAssets": info.get("returnOnAssets"),
            "debtToEquity": info.get("debtToEquity"),
            "currentRatio": info.get("currentRatio"),
            "freeCashflow": info.get("freeCashflow"),
            "operatingCashflow": info.get("operatingCashflow"),
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),
            "beta": info.get("beta"),
            "sharesOutstanding": info.get("sharesOutstanding"),
        })

    return json.dumps(results, indent=2, default=str)


# ---------------------------------------------------------------------------
# Run the server
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
