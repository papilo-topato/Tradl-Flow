# stocks.py
import yfinance as yf
import requests

# 1. COMMODITIES (Global Tickers)
COMMODITY_TICKERS = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Crude Oil": "CL=F",
    "Brent Oil": "BZ=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
    "Bitcoin": "BTC-USD"
}

# 2. SECTOR MAP
SECTOR_MAP = {
    "BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "BANKING": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS"],
    "AUTO": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS"],
    "FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS"],
    "METAL": ["TATASTEEL.NS", "HINDALCO.NS", "VEDL.NS", "JSWSTEEL.NS", "COALINDIA.NS"]
}

# 3. MANUAL OVERRIDES (Brand -> Stock Ticker)
BRAND_TO_STOCK = {
    "DOMINOS": "JUBLFOOD.NS", "DOMINO'S": "JUBLFOOD.NS", "JUBILANT FOODWORKS": "JUBLFOOD.NS",
    "DMART": "AVENUESUPER.NS", "AVENUE SUPERMARTS": "AVENUESUPER.NS",
    "GOOGLE": "GOOGL",
    "MAGGI": "NESTLEIND.NS", "JLR": "TATAMOTORS.NS",
    "ZOMATO": "ZOMATO.NS", "SWIGGY": "SWIGGY.NS",
    "SBI": "SBIN.NS", "SBI BANK": "SBIN.NS", "STATE BANK OF INDIA": "SBIN.NS",
    "HDFC": "HDFCBANK.NS", "HDFC BANK": "HDFCBANK.NS"
}

# 4. PARENT COMPANY NAMES (For Better News Search)
# When finding news, we want "Avenue Supermarts", not just "AVENUESUPER"
PARENT_NAMES = {
    "JUBLFOOD.NS": "Jubilant Foodworks",
    "AVENUESUPER.NS": "Avenue Supermarts",
    "SBIN.NS": "State Bank of India",
    "HDFCBANK.NS": "HDFC Bank"
}

# 5. GROUP MAP
GROUP_MAP = {
    "TATA": ["TCS.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TITAN.NS", "TATAPOWER.NS"],
    "RELIANCE": ["RELIANCE.NS", "JIOFIN.NS", "JUSTDIAL.NS"],
    "ADANI": ["ADANIENT.NS", "ADANIPORTS.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "AWL.NS"],
    "MAHINDRA": ["M&M.NS", "TECHM.NS", "M&MFIN.NS"]
}

def search_symbol_on_yahoo(query):
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=1&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=3)
        data = res.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            for quote in data['quotes']:
                symbol = quote['symbol']
                if symbol.endswith(".NS") or symbol.endswith(".BO"):
                    return symbol
            return data['quotes'][0]['symbol']
    except:
        pass
    return None

def resolve_query(query):
    q = " ".join(query.upper().split())

    # Commodity
    if "COMMODITY" in q or q in [k.upper() for k in COMMODITY_TICKERS.keys()]:
        return {"type": "commodity_market", "name": "Global Commodities", "search_terms": ["Commodity Market News"]}

    # Sector
    for sector, stocks in SECTOR_MAP.items():
        if sector in q:
            return {"type": "sector", "name": f"{sector.title()} Sector", "symbols": stocks, "search_terms": [f"{sector.title()} Sector News"]}

    # Group
    for group_name, stocks in GROUP_MAP.items():
        if group_name in q:
            return {"type": "group", "name": f"{group_name.title()} Group", "symbols": stocks, "search_terms": [f"{group_name} Group News"]}

    # Stock/Brand Logic
    sym = None
    search_terms = [query] # Default search term is user query

    if q in BRAND_TO_STOCK:
        sym = BRAND_TO_STOCK[q]
        # If it's a brand (e.g. DMART), add the Parent Company (Avenue Supermarts) to search terms
        if sym in PARENT_NAMES:
            search_terms.append(PARENT_NAMES[sym])
        else:
            search_terms.append(sym.replace(".NS",""))
    else:
        # Universal Search
        found = search_symbol_on_yahoo(query)
        if found:
            sym = found
            search_terms.append(sym)
        else:
            sym = query.upper() if (query.upper().endswith(".NS")) else f"{query.upper()}.NS"

    return {"type": "stock", "symbol": sym, "search_terms": search_terms}

def format_large_number(num):
    if num is None: return "N/A"
    if isinstance(num, str): return num
    if num >= 1_000_000_000_000: return f"₹{round(num/1_000_000_000_000, 2)}T"
    if num >= 1_000_000_000: return f"₹{round(num/1_000_000_000, 2)}B"
    if num >= 1_000_000: return f"₹{round(num/1_000_000, 2)}M"
    return f"₹{num}"

def get_live_data(symbol):
    """
    Fetches stock data with DEMO INTERCEPTORS for Key Stocks.
    """
    
    # ==========================================
    # 🛑 DEMO MODE: HARDCODED FINANCIALS
    # ==========================================

    # 1. SBI BANK (Hardcoded)
    if symbol == "SBIN.NS":
        return {
            "symbol": "SBIN",
            "name": "State Bank of India",
            "price": 948.10,
            "change": 14.50,
            "percent_change": 1.55,
            "market_cap": "₹8,78,201Cr",
            "pe_ratio": 10.47,
            "day_high": 955.20,
            "day_low": 938.00,
            "currency": "INR",
            "sector": "Financial Services",
            "note": "Demo Mode: Financials hardcoded for presentation"
        }

    # 2. HDFC BANK (Hardcoded)
    if symbol == "HDFCBANK.NS":
        return {
            "symbol": "HDFCBANK",
            "name": "HDFC Bank Limited",
            "price": 997.20,
            "change": 8.40,
            "percent_change": 0.85,
            "market_cap": "₹15,38,943Cr",
            "pe_ratio": 20.50,
            "day_high": 1005.00,
            "day_low": 988.50,
            "currency": "INR",
            "sector": "Financial Services",
            "note": "Demo Mode: Financials hardcoded for presentation"
        }

    # 3. JUBLIANT FOODWORKS / DOMINO'S (Hardcoded)
    if symbol == "JUBLFOOD.NS":
        return {
            "symbol": "JUBLFOOD",
            "name": "Jubilant Foodworks (Domino's)",
            "price": 590.90,
            "change": 4.10, # Synthetic
            "percent_change": 0.70,
            "market_cap": "₹38,888Cr",
            "pe_ratio": 101.96,
            "day_high": 595.00,
            "day_low": 585.50,
            "currency": "INR",
            "sector": "Consumer Cyclical",
            "note": "Demo Mode: Financials hardcoded for presentation"
        }

    # 4. AVENUE SUPERMARTS / DMART (Hardcoded)
    if symbol == "AVENUESUPER.NS":
        return {
            "symbol": "DMART", # Displaying popular name
            "name": "Avenue Supermarts",
            "price": 3913.30,
            "change": 22.50, # Synthetic
            "percent_change": 0.58,
            "market_cap": "₹2,54,297Cr",
            "pe_ratio": 93.09,
            "day_high": 3940.00,
            "day_low": 3890.00,
            "currency": "INR",
            "sector": "Consumer Defensive",
            "note": "Demo Mode: Financials hardcoded for presentation"
        }

    # ==========================================
    # 🟢 LIVE FETCH FOR OTHERS
    # ==========================================
    try:
        ticker = yf.Ticker(symbol)
        
        # Use fast_info for reliability
        current_price = ticker.fast_info.get('last_price')
        prev_close = ticker.fast_info.get('previous_close')
        
        if current_price is None or prev_close is None:
            data = ticker.history(period="1d")
            if data.empty: return None
            current_price = data['Close'].iloc[-1]
            prev_close = data['Open'].iloc[-1]
            
        change = current_price - prev_close
        pct_change = (change / prev_close) * 100
        
        info = ticker.info
        name = info.get('shortName') or info.get('longName') or symbol
        pe_ratio = info.get('trailingPE')
        market_cap = info.get('marketCap')
        sector = info.get('sector', 'N/A')
        day_high = ticker.fast_info.get('day_high')
        day_low = ticker.fast_info.get('day_low')
        
        return {
            "symbol": symbol.replace(".NS", "").replace("=F", ""),
            "name": name,
            "price": round(current_price, 2),
            "change": round(change, 2),
            "percent_change": round(pct_change, 2),
            "market_cap": format_large_number(market_cap),
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else "N/A",
            "day_high": round(day_high, 2) if day_high else "N/A",
            "day_low": round(day_low, 2) if day_low else "N/A",
            "currency": info.get('currency', '?'),
            "sector": sector
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def get_commodity_snapshot():
    data_list = []
    for name, ticker in COMMODITY_TICKERS.items():
        data = get_live_data(ticker)
        if data:
            data['symbol'] = name 
            data_list.append(data)
    return data_list

def get_market_overview():
    # Indices
    indices = ["^NSEI", "^BSESN", "^NSEBANK"]
    results = []
    for sym in indices:
        d = get_live_data(sym)
        if d:
            if sym == "^NSEI": d['name'] = "NIFTY 50"
            elif sym == "^BSESN": d['name'] = "SENSEX"
            elif sym == "^NSEBANK": d['name'] = "BANK NIFTY"
            results.append(d)
    return results

def get_market_ticker():
    return get_market_overview()
