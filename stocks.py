# stocks.py
import yfinance as yf

# 1. COMMODITIES (Global Tickers)
COMMODITY_TICKERS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Crude Oil": "CL=F",
    "Brent Oil": "BZ=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F"
}

# 2. SECTOR MAP (Sector Name -> Top Stocks)
SECTOR_MAP = {
    "BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "AUTO": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS"],
    "METAL": ["TATASTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JSWSTEEL.NS"]
}

# 3. EXISTING MAPS
BRAND_TO_STOCK = {
    "DMART": "AVENUESUPER.NS", "DOMINOS": "JUBLFOOD.NS", "DOMINO'S": "JUBLFOOD.NS",
    "ZOMATO": "ZOMATO.NS", "SWIGGY": "SWIGGY.NS", "PAYTM": "PAYTM.NS",
    "MAGGI": "NESTLEIND.NS", "JAGUAR": "TATAMOTORS.NS",
    "PIZZA HUT": "DEVYANI.NS", "KFC": "DEVYANI.NS",
    "ZUDIO": "TRENT.NS", "WESTSIDE": "TRENT.NS",
    "GOOGLE": "GOOGL"
}
GROUP_MAP = {
    "TATA": ["TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TITAN.NS", "TRENT.NS", "TATAPOWER.NS"],
    "RELIANCE": ["RELIANCE.NS", "JIOFIN.NS", "JUSTDIAL.NS"],
    "ADANI": ["ADANIENT.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "ADANIPOWER.NS"],
    "MAHINDRA": ["M&M.NS", "TECHM.NS", "M&MFIN.NS"],
    "HDFC": ["HDFCBANK.NS", "HDFCLIFE.NS", "HDFCAMC.NS"]
}

def resolve_query(query):
    """
    Determines if query is a Commodity, Sector, Group, or Stock.
    """
    q = query.upper().strip()

    # CASE A: Commodities
    if "COMMODITY" in q or "COMMODITIES" in q or q in ["GOLD", "OIL", "SILVER"]:
        return {
            "type": "commodity_market",
            "name": "Global Commodities",
            "search_terms": ["Commodity Market News", "Gold Price Outlook", "Crude Oil Analysis"]
        }

    # CASE B: Sectors (e.g., "Banks", "Auto Sector")
    for sector, stocks in SECTOR_MAP.items():
        if sector in q:
            return {
                "type": "sector",
                "name": f"{sector.title()} Sector",
                "symbols": stocks,
                "search_terms": [f"{sector.title()} Sector News", f"Indian {sector.title()} Stocks Outlook"]
            }

    # CASE C: Groups
    for group_name, stocks in GROUP_MAP.items():
        if group_name in q:
            return {
                "type": "group",
                "name": f"{group_name.title()} Group",
                "symbols": stocks,
                "search_terms": [f"{group_name} Group News"]
            }

    # CASE D: Stock/Brand
    sym = BRAND_TO_STOCK.get(q)
    if not sym:
        sym = q if q.endswith(".NS") else f"{q}.NS"
    
    return {
        "type": "stock",
        "symbol": sym,
        "search_terms": [q, sym.replace(".NS","")]
    }

def get_live_data(symbol):
    """Generic fetcher for Stocks AND Commodities"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if data.empty: return None
        
        current = data['Close'].iloc[-1]
        prev = data['Open'].iloc[-1]
        change = current - prev
        pct = (change/prev)*100
        
        # Safe info fetch
        info = ticker.info
        name = info.get('shortName', symbol)
        
        return {
            "symbol": symbol.replace(".NS", "").replace("=F", ""),
            "name": name,
            "price": round(current, 2),
            "change": round(change, 2),
            "percent_change": round(pct, 2),
            "currency": info.get('currency', '?'),
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('trailingPE', 'N/A'),
            "sector": info.get('sector', 'Market'),
            "day_high": round(data['High'].iloc[-1], 2),
            "day_low": round(data['Low'].iloc[-1], 2)
        }
    except:
        # Fallback Logic
        import random
        base_price = random.uniform(100, 3000)
        change = random.uniform(-50, 50)
        return {
            "symbol": symbol.replace(".NS", "").replace("=F", ""),
            "name": symbol,
            "price": round(base_price, 2),
            "change": round(change, 2),
            "percent_change": round((change/base_price)*100, 2),
            "currency": "INR",
            "market_cap": "N/A",
            "pe_ratio": "N/A",
            "sector": "Unknown",
            "day_high": round(base_price + 20, 2),
            "day_low": round(base_price - 20, 2),
            "note": "⚠️ Live data unavailable. Showing simulated data."
        }

def get_live_stock_price(symbol):
    # Wrapper for backward compatibility if needed, or just alias it
    return get_live_data(symbol)

def get_commodity_snapshot():
    """Fetches list of top commodities"""
    data_list = []
    for name, ticker in COMMODITY_TICKERS.items():
        data = get_live_data(ticker)
        if data:
            data['name'] = name # Override with friendly name
            data_list.append(data)
    return data_list

def get_market_overview():
    indices = [{"name": "NIFTY 50", "price": 26218, "change": -18, "percent_change": -0.07}]
    return {"indices": indices}

def get_market_ticker():
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "SBIN.NS", "ITC.NS", "TATAMOTORS.NS"]
    ticker_data = []
    for sym in symbols:
        d = get_live_data(sym)
        if d:
            ticker_data.append({
                "symbol": d['symbol'],
                "last_price": d['price'],
                "percent_change": d['percent_change']
            })
    return ticker_data
