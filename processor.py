from GoogleNews import GoogleNews
import re
import datetime

def calculate_priority(date_str, text):
    """
    Assigns a score: Higher is newer/more relevant.
    """
    score = 0
    date_str = date_str.lower()
    
    # 1. Recency Score
    if "min" in date_str or "just now" in date_str:
        score += 100
    elif "hour" in date_str:
        try:
            # "2 hours ago" -> prioritize lower hours
            hours = int(re.search(r'\d+', date_str).group())
            score += (50 - hours) # 1 hour > 5 hours
        except:
            score += 40
    elif "day" in date_str:
        score += 10
        
    # 2. Relevance Score (Keywords)
    keywords = ["surge", "crash", "high", "low", "record", "quarter", "profit", "loss"]
    if any(k in text.lower() for k in keywords):
        score += 20
        
    return score

def search_topic_news(query_list):
    googlenews = GoogleNews(lang='en', region='IN')
    if isinstance(query_list, str): query_list = [query_list]
    
    all_articles = []
    seen_titles = set()
    
    print(f"Searching: {query_list}")
    
    for topic in query_list:
        googlenews.search(topic)
        results = googlenews.result()
        
        for item in results[:6]:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                
                date_str = item.get('date', 'Unknown')
                text = f"{item['title']}. {item['desc']}"
                
                # Calculate Rank
                rank = calculate_priority(date_str, text)
                
                all_articles.append({
                    "text": item['title'], # Cleaner display
                    "desc": item['desc'],
                    "source": item['media'],
                    "link": item['link'],
                    "date": date_str,
                    "rank": rank
                })
        googlenews.clear()
    
    # SORT: Highest rank first
    all_articles.sort(key=lambda x: x['rank'], reverse=True)
    return all_articles
