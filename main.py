from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from graph import app as pipeline_app
from database import global_db
from stocks import resolve_query, get_live_data, get_commodity_snapshot, get_market_overview, get_market_ticker # <--- UPDATE IMPORTS
from processor import search_topic_news, extract_text_from_pdf, extract_text_from_url, analyze_document_content, llm_analyst
from langchain_core.messages import HumanMessage

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Financial News AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsRequest(BaseModel):
    text: str

class QueryRequest(BaseModel):
    query: str

class CompareRequest(BaseModel):
    stock1: str
    stock2: str

@app.get("/")
def home():
    return {"status": "System Online", "backend": "Local / Ollama"}

@app.get("/market_summary")
def market_summary():
    """Returns Indices and Top Movers"""
    return get_market_overview()

@app.post("/resolve_and_fetch")
def resolve_and_fetch(req: QueryRequest):
    res = resolve_query(req.query)
    
    # 1. COMMODITY MARKET
    if res['type'] == 'commodity_market':
        data = get_commodity_snapshot()
        return {
            "type": "commodity",
            "title": "Global Commodities",
            "stocks": data,
            "search_terms": res['search_terms']
        }

    # 2. SECTOR or GROUP (Logic is same: List of stocks)
    elif res['type'] in ['sector', 'group']:
        stocks_data = []
        for sym in res['symbols']:
            d = get_live_data(sym)
            if d: stocks_data.append(d)
        
        return {
            "type": "grid_view", # Reusing grid layout for both
            "title": res['name'],
            "stocks": stocks_data,
            "search_terms": res['search_terms']
        }
    
    # 3. SINGLE STOCK
    else:
        d = get_live_data(res['symbol'])
        if d:
            if "note" in res:
                d["note"] = res["note"]
            return {"type": "stock", "data": d, "search_terms": res['search_terms']}
            
    return {"type": "error", "message": "Data not found"}

@app.post("/ingest_news")
def ingest_news(req: QueryRequest):
    # This now expects a comma-separated string or handles it internally
    # For simplicity, we assume the frontend sends the primary search term
    # But better: The frontend passes the list from 'resolve_and_fetch'
    # Let's adapt to handle the string input by splitting if needed
    terms = req.query.split(",") 
    articles = search_topic_news(terms)
    return {"articles": articles}

@app.post("/ingest")
def ingest_article(request: NewsRequest):
    """
    Feed a new article into the AI pipeline.
    """
    try:
        # Run the LangGraph pipeline
        result = pipeline_app.invoke({"article_text": request.text})
        
        if result['is_duplicate']:
            return {"status": "ignored", "reason": "Duplicate"}
        else:
            return {
                "status": "processed", 
                "entities": result['entities']
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
def search_news(request: QueryRequest):
    """
    Context-aware search.
    """
    results = global_db.advanced_search(request.query)
    return {"results": results}

@app.post("/analyze_doc")
async def analyze_doc(
    file: UploadFile = File(None), 
    url: str = Form(None)
):
    """
    Analyzes an uploaded file OR a URL.
    """
    raw_text = ""
    
    # 1. Get Text
    if file:
        content = await file.read()
        raw_text = extract_text_from_pdf(content)
    elif url:
        raw_text = extract_text_from_url(url)
    else:
        return {"status": "error", "message": "No input provided"}
    
    # 2. Analyze
    result = analyze_document_content(raw_text)
    
    return {"status": "success", "data": result}

@app.post("/compare_stocks")
def compare_stocks(req: CompareRequest):
    # 1. Resolve and Fetch Stock 1
    res1 = resolve_query(req.stock1)
    data1 = get_live_data(res1['symbol']) if res1.get('symbol') else None
    
    # 2. Resolve and Fetch Stock 2
    res2 = resolve_query(req.stock2)
    data2 = get_live_data(res2['symbol']) if res2.get('symbol') else None

    if not data1 or not data2:
        return {"status": "error", "message": "Could not find data for one or both stocks."}

    # 3. Fetch News for Context (Top 3 articles each)
    news1 = search_topic_news([data1['symbol']])[:3]
    news2 = search_topic_news([data2['symbol']])[:3]

    # 4. Generate AI Verdict
    prompt = f"""
    Compare these two stocks based on the provided data and news headlines.
    
    Stock A: {data1['symbol']} | Price: {data1['price']} | PE: {data1.get('pe_ratio', 'N/A')} | Change: {data1['percent_change']}%
    News A: {[n['text'] for n in news1]}
    
    Stock B: {data2['symbol']} | Price: {data2['price']} | PE: {data2.get('pe_ratio', 'N/A')} | Change: {data2['percent_change']}%
    News B: {[n['text'] for n in news2]}
    
    Task: Provide a 3-sentence comparison verdict. Which one looks stronger in the short term?
    """
    
    ai_verdict = "AI analysis unavailable."
    try:
        response = llm_analyst.invoke([HumanMessage(content=prompt)])
        ai_verdict = response.content
    except:
        pass

    return {
        "status": "success",
        "stock1": data1,
        "stock2": data2,
        "verdict": ai_verdict
    }

# --- RUNNER ---
if __name__ == "__main__":
    import uvicorn
    # Runs the server on port 8002
    uvicorn.run(app, host="0.0.0.0", port=8002)
