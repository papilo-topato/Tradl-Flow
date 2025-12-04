# processor.py
import pypdf
import io
import requests
from bs4 import BeautifulSoup
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from GoogleNews import GoogleNews
import re
from textblob import TextBlob

# Initialize Llama 3.2
llm_analyst = ChatOllama(model="llama3.2", temperature=0)

# --- NEWS SCORING LOGIC ---
def analyze_sentiment(text):
    """Simple sentiment for list view"""
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0.1: return "🟢 Bullish"
    elif analysis.sentiment.polarity < -0.1: return "🔴 Bearish"
    return "⚪ Neutral"

def calculate_priority(date_str, text):
    score = 0
    date_str = date_str.lower()
    if "min" in date_str or "just now" in date_str: score += 100
    elif "hour" in date_str: score += 50
    elif "day" in date_str: score += 10
    
    keywords = ["surge", "crash", "high", "record", "profit", "quarter", "results"]
    if any(k in text.lower() for k in keywords): score += 20
    return score

def search_topic_news(query_list):
    googlenews = GoogleNews(lang='en', region='IN')
    if isinstance(query_list, str): query_list = [query_list]
    
    all_articles = []
    seen_titles = set()
    
    for topic in query_list:
        googlenews.search(topic)
        results = googlenews.result()
        for item in results[:6]:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                text = f"{item['title']}. {item['desc']}"
                all_articles.append({
                    "text": item['title'],
                    "desc": item['desc'],
                    "source": item['media'],
                    "link": item['link'],
                    "date": item.get('date', 'Today'),
                    "rank": calculate_priority(item.get('date', ''), text),
                    "sentiment": analyze_sentiment(text)
                })
        googlenews.clear()
    
    all_articles.sort(key=lambda x: x['rank'], reverse=True)
    return all_articles

# --- DOCUMENT ANALYST LOGIC ---

def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text[:15000]
    except Exception as e:
        print(f"PDF Error: {e}")
        return None

def extract_text_from_url(url):
    try:
        # Robust Headers to look like a Real User
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.google.com/'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Aggressively strip non-content tags
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "ads"]):
            tag.extract()
            
        # Get text with spacing to prevent words merging
        text = soup.get_text(separator=' ')
        
        # Clean up whitespace (Collapse multiple spaces into one)
        text = ' '.join(text.split())
        
        return text[:15000]
    except Exception as e:
        print(f"Scrape Error: {e}")
        return None

def analyze_document_content(text):
    if not text or len(text) < 100:
        return {"is_relevant": False, "message": "Could not extract enough text from the link. Website might be protected."}

    # BALANCED PROMPT
    prompt = f"""
    You are a Financial Analyst. Analyze the text below.

    STEP 1: IDENTIFY TOPIC
    - If the text is about Movies (Plots, Cast), Sports (Match scores), Recipes, or Celebrity Gossip -> Output "NON_FINANCIAL".
    - If the text mentions Stocks, Companies (e.g., Tata, Reliance), Prices (Rs, $), Markets, Business, or Economy -> Proceed to Step 2.
    
    STEP 2: ANALYSIS (Only if Financial)
    Provide a valid JSON-style response with:
    - Summary (3 bullet points)
    - Sentiment (Bullish/Bearish/Neutral)
    - Impact (What stock/sector is affected?)

    Text to Analyze:
    {text[:5000]}
    """
    
    try:
        response = llm_analyst.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()
        
        # Check for the kill switch
        if "NON_FINANCIAL" in content:
            return {
                "is_relevant": False,
                "message": "☕ Not my cup of tea. This appears to be general content (Entertainment/Sports), not Financial Intelligence."
            }
        
        return {
            "is_relevant": True,
            "analysis": content.replace("NON_FINANCIAL", "") # Cleanup
        }
    except Exception as e:
        return {"is_relevant": False, "message": f"AI Error: {e}"}
