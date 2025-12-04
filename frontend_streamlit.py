import streamlit as st
import requests
import time

API_URL = "http://localhost:8002"  # CORRECTED: Backend runs on 8002

# --- THEME MANAGEMENT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Tradl Flow | Financial Intelligence",
    layout="wide",
    page_icon="🌊",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/papilo-topato',
        'About': "Tradl Flow v3.0 - Built by Raghuram K S"
    }
)

# --- DYNAMIC CSS ---
if st.session_state.theme == 'dark':
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#1e1e1e"
    viz_bg = "#2b2b2b"
    viz_border = "#444"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    card_bg = "#f0f2f6"
    viz_bg = "#e0e0e0"
    viz_border = "#ccc"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    p, h1, h2, h3, div, li, span {{ color: {text_color}; }}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {card_bg};
    }}
    [data-testid="stSidebar"] * {{
        color: {text_color} !important;
    }}

    /* Card Styling */
    .market-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .news-card {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }}

    /* VISUALIZATION PIPELINE CSS */
    .viz-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: {viz_bg};
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 25px;
        border: 1px solid {viz_border};
    }}
    .viz-node {{
        background-color: {card_bg};
        border: 2px solid #555;
        padding: 10px 15px;
        border-radius: 8px;
        text-align: center;
        width: 18%;
        font-size: 14px;
        font-weight: bold;
        transition: all 0.3s ease;
        opacity: 0.4;
        color: {text_color};
    }}
    .viz-arrow {{
        font-size: 20px;
        color: #555;
        font-weight: bold;
    }}

    /* ACTIVE STATES */
    .viz-active {{
        border-color: #4CAF50;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.6);
        transform: scale(1.05);
        opacity: 1;
        color: #4CAF50 !important;
    }}
    .viz-completed {{
        border-color: #4CAF50;
        background-color: rgba(76, 175, 80, 0.1);
        opacity: 1;
    }}

    /* Profile Links */
    .profile-link {{
        text-decoration: none;
        color: {text_color} !important;
        background-color: {card_bg};
        padding: 10px 15px;
        border-radius: 5px;
        margin-right: 10px;
        border: 1px solid #ccc;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 10px;
    }}
    .profile-link:hover {{ border-color: #4CAF50; color: #4CAF50 !important; }}

    .footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: {card_bg}; text-align: center;
        padding: 10px; font-size: 12px; border-top: 1px solid #333; opacity:0.8;
        color: {text_color};
    }}
    </style>
""", unsafe_allow_html=True)

# --- PIPELINE VISUALIZER COMPONENT ---
def render_pipeline_viz(step=0):
    """
    Renders a live HTML Flowchart.
    Step 0: Idle
    Step 1: User -> Resolver
    Step 2: Resolver -> API
    Step 3: API -> Ranker
    Step 4: Done
    """

    # Define Classes based on step
    s1 = "viz-active" if step == 1 else ("viz-completed" if step > 1 else "")
    s2 = "viz-active" if step == 2 else ("viz-completed" if step > 2 else "")
    s3 = "viz-active" if step == 3 else ("viz-completed" if step > 3 else "")
    s4 = "viz-active" if step == 4 else ("viz-completed" if step > 4 else "")

    html_code = f"""
    <div class="viz-container">
        <div class="viz-node {s1}">
            👤 User Intent<br>
            <span style="font-size:10px">NLP Analysis</span>
        </div>
        <div class="viz-arrow">→</div>
        <div class="viz-node {s2}">
            🧠 Smart Resolver<br>
            <span style="font-size:10px">Entity Mapping</span>
        </div>
        <div class="viz-arrow">→</div>
        <div class="viz-node {s3}">
            🌐 Data Swarm<br>
            <span style="font-size:10px">Live APIs & Scrapers</span>
        </div>
        <div class="viz-arrow">→</div>
        <div class="viz-node {s4}">
            🤖 AI Ranker<br>
            <span style="font-size:10px">Context Scoring</span>
        </div>
    </div>
    """
    return html_code

# --- DATA FETCHING WITH VISUALS ---
def fetch_data_with_visuals(query):
    # Create a placeholder for the visualizer
    viz_placeholder = st.empty()

    # STEP 1: RESOLVING
    viz_placeholder.markdown(render_pipeline_viz(step=1), unsafe_allow_html=True)
    time.sleep(0.3)  # Tiny visual delay for effect

    viz_placeholder.markdown(render_pipeline_viz(step=2), unsafe_allow_html=True)
    try:
        # Actual Backend Call
        res = requests.post(f"{API_URL}/resolve_and_fetch", json={"query": query})
        data = res.json()
    except:
        viz_placeholder.empty()
        return None, None

    if data.get("type") == "error":
        viz_placeholder.empty()
        return None, None

    # STEP 2: FETCHING & RANKING
    viz_placeholder.markdown(render_pipeline_viz(step=3), unsafe_allow_html=True)

    term_display = data.get('search_terms', [query])[0]
    terms_str = ",".join(data.get('search_terms', [query]))

    # Actual Backend Call
    news_res = requests.post(f"{API_URL}/ingest_news", json={"query": terms_str})
    news_data = news_res.json().get('articles', [])

    # STEP 3: DONE
    viz_placeholder.markdown(render_pipeline_viz(step=4), unsafe_allow_html=True)
    time.sleep(0.8)  # Let user see the "Complete" state
    viz_placeholder.empty()  # Remove it to show results clean

    return data, news_data

# --- RENDER FUNCTIONS (Stocks, Grid, News) ---
def render_stock(data):
    info = data['data']
    color = "positive" if info['change'] >= 0 else "negative"
    if "note" in data: st.info(f"ℹ️ {data['note']}")

    st.markdown(f"""
    <div class="market-card">
        <div style="display:flex; justify-content:space-between;">
            <div><h1>{info['symbol']}</h1><span style="color:#888;">{info['sector']}</span></div>
            <div style="text-align:right;"><h1>₹{info['price']}</h1><span class="{color}">{info['change']} ({info['percent_change']}%)</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Market Cap", f"₹{info['market_cap']}")
    c2.metric("P/E Ratio", f"{info['pe_ratio']}")
    c3.metric("Day Range", f"{info['day_low']} - {info['day_high']}")

def render_grid_view(data):
    st.subheader(f"📊 {data['title']}")
    cols = st.columns(3)
    for idx, stock in enumerate(data['stocks']):
        color = "positive" if stock['change'] >= 0 else "negative"
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="market-card" style="padding:15px;">
                <div style="font-size:12px; color:#888;">{stock['symbol']}</div>
                <div style="font-size:20px; font-weight:bold;">{stock.get('currency','')} {stock['price']}</div>
                <div class="{color}">{stock['change']} ({stock['percent_change']}%)</div>
            </div>
            """, unsafe_allow_html=True)

def render_news(articles):
    st.subheader("📰 Intelligent News Feed")
    if not articles: st.write("No major headlines found."); return
    for idx, item in enumerate(articles):
        badge = ""
        if idx == 0 or item.get('rank', 0) > 80:
            badge = '<span style="background:#ff4444; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:5px;">🔥 BREAKING</span>'
        elif "hour" in item['date']:
            badge = '<span style="background:#4CAF50; color:white; padding:2px 6px; border-radius:4px; font-size:10px; margin-right:5px;">LIVE</span>'

        # SENTIMENT BADGE
        sent = item.get('sentiment', '⚪ Neutral')
        sent_badge = f'<span style="border:1px solid #555; padding:2px 6px; border-radius:4px; font-size:10px; margin-left:5px;">{sent}</span>'

        st.markdown(f"""
        <div class="news-card">
            <div style="font-size:11px; color:#888;">{badge} {sent_badge} 📅 {item['date']} | {item['source']}</div>
            <div style="font-weight:600; font-size:16px; margin: 5px 0;">{item['text']}</div>
            <a href="{item['link']}" target="_blank" style="color:#4CAF50; text-decoration:none; font-size:12px;">Read Full Story ↗</a>
        </div>
        """, unsafe_allow_html=True)

# --- HELPER: GENERATE REPORT ---
def generate_report_text(query, data, news):
    """Generates a text-based market intelligence report"""
    report = f"""
=====================================
TRADL FLOW INTELLIGENCE REPORT
=====================================
Topic: {query}
Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}

"""

    # Add Market Data Section
    if data and data.get('type') == 'stock':
        info = data['data']
        report += f"""
STOCK ANALYSIS
--------------
Symbol: {info['symbol']}
Sector: {info['sector']}
Current Price: ₹{info['price']}
Change: {info['change']} ({info['percent_change']}%)
Market Cap: ₹{info['market_cap']}
P/E Ratio: {info['pe_ratio']}
Day Range: {info['day_low']} - {info['day_high']}

"""
    elif data and data.get('type') in ['commodity', 'grid_view']:
        report += f"""
{data['title']}
{'=' * len(data['title'])}

"""
        for stock in data.get('stocks', []):
            report += f"{stock['symbol']}: {stock.get('currency', '')} {stock['price']} ({stock['change']}, {stock['percent_change']}%)\n"
        report += "\n"

    # Add News Section
    report += """
TOP HEADLINES & SENTIMENT ANALYSIS
-----------------------------------
"""

    for idx, n in enumerate(news[:10], 1):
        sentiment = n.get('sentiment', 'N/A')
        report += f"{idx}. {n['text']}\n"
        report += f"   Sentiment: {sentiment} | Source: {n['source']} | {n['date']}\n"
        report += f"   Link: {n['link']}\n\n"

    report += """
=====================================
Report generated by Tradl Flow v3.0
AI-Powered Financial Intelligence
Built by Raghuram K S
=====================================
"""

    return report

# --- HELPER: PERFORM SEARCH ---
def perform_search(query_text):
    """Executes the search and renders results"""
    if query_text.lower() == "market":
        st.info("Market Overview Mode")
    else:
        data, news = fetch_data_with_visuals(query_text)
        if data:
            # Render results
            if data['type'] == 'stock': render_stock(data)
            elif data['type'] in ['commodity', 'grid_view']: render_grid_view(data)
            render_news(news)

            # Add Download Report Button
            st.markdown("---")
            report_content = generate_report_text(query_text, data, news)
            st.download_button(
                label="📥 Download Market Brief",
                data=report_content,
                file_name=f"Tradl_Report_{query_text.replace(' ', '_')}.txt",
                mime="text/plain",
                help="Download a comprehensive market intelligence report"
            )
        else:
            st.error(f"❌ Data not found for '{query_text}'. Try a different term.")

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("🌊 Tradl Flow")
    st.caption("AI-Powered Market Intelligence")
    page = st.radio("Navigation", ["🚀 Terminal", "👤 About the Architect"])
    st.divider()
    btn_label = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    st.button(btn_label, on_click=toggle_theme)
    st.markdown("---")
    st.caption("Built by **Raghuram K S**")

# --- MAIN ROUTING ---
if page == "🚀 Terminal":
    st.title("🌊 Tradl Flow")
    st.markdown("#### The Intelligent Market Workspace")

    query = st.text_input("Search (e.g., 'Domino\\'s', 'Tata', 'Gold', 'Banks')...", placeholder="Type a company, sector, or brand...")

    if query:
        perform_search(query)
    else:
        st.info("👋 Welcome to Tradl Flow. Start by searching for a stock, sector, or brand.")

        st.write("OR Select a Quick Access Module:")
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🏦 Banks"): perform_search("Banks")
        if c2.button("🚗 Auto"): perform_search("Auto")
        if c3.button("🛢️ Oil"): perform_search("Oil")
        if c4.button("🪙 Gold"): perform_search("Gold")

elif page == "👤 About the Architect":
    st.title("Raghuram K S")
    st.markdown("#### 🚀 Engineer | Product Thinker | AI & No-Code Builder")
    st.markdown("""
    <a href="https://www.linkedin.com/in/papilo-topato" class="profile-link" target="_blank">🔗 LinkedIn</a>
    <a href="https://github.com/papilo-topato" class="profile-link" target="_blank">💻 GitHub</a>
    <a href="https://x.com/papilo_topato" class="profile-link" target="_blank">🐦 X (Twitter)</a>
    <a href="https://www.youtube.com/@papilo-topato" class="profile-link" target="_blank">🎥 YouTube</a>
    <a href="https://instagram.com/papilo_topato?igshid=ZDc4ODBmNjlmNQ==" class="profile-link" target="_blank">📸 Instagram</a>
    """, unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### About Me
        Exploring the fast-moving intersection of **AI, no-code development, and electronics**—and currently open to opportunities where these worlds collide.

        Previously, I worked as a **Management Trainee** in the central think tank at **Electronic Payment and Services (EPS)**, where I operated at the crossroads of business strategy, product thinking, and hands-on tech execution. From shaping growth strategies to building AI capabilities from scratch, I learned to turn complexity into clarity—and ideas into impact.

        With a background in **Electronics & Communication Engineering** and experience as a **Smart India Hackathon 2022 Hardware Edition finalist**, I'm deeply curious about how intelligence can be embedded into systems—whether that's smarter software, automated workflows, or hardware-AI hybrids that blur the line between physical and digital.
        """)

        st.markdown("""
        ### 💡 My Philosophy
        **"In the world of endless paths, identity is the compass."**

        I am a great believer that **imagination is greater than knowledge**. In the age of AI, you only need imagination to see and articulate what you want. I love the "nutcracker" jobs—building dreams with limited tools.

        I am an **Engineer by heart, Child by soul**.
        *   **Engineer:** Practical, bottling down ideas to make them work.
        *   **Child:** Fast learner, imagining endlessly beyond boundaries.
        These two forces work together like two eyes giving depth to vision.
        """)

    with col2:
        st.markdown("""
        ### 🎯 Focus Areas

        **🤖 AI & Automation**
        Building practical AI/ML solutions, experimenting with LLMs, and using no-code/low-code tools to rapidly prototype intelligent workflows.

        **⚡ No-Code Development**
        Creating products with the speed of no-code tools (Bubble, Make, n8n) and bridging them with custom logic.

        **🔌 Electronics Meets AI**
        Exploring edge AI, tinyML, IoT intelligence, and adaptive hardware.

        **💡 Product & Innovation**
        Crafting solutions that work by asking the right "what if?" questions.
        """)

    st.info("🤝 If you're working on something interesting in AI, automation, product, or no-code, or if you're exploring how hardware and intelligence merge—let's connect.")

# --- FOOTER ---
st.markdown("""
    <div class="footer">
        Developed and built by <b>Raghuram K S</b>
    </div>
""", unsafe_allow_html=True)
