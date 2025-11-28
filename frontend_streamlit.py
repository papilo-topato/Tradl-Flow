import streamlit as st
import requests
import time

# UPDATED: Pointing to the correct backend port
API_URL = "http://localhost:8002"

# --- THEME MANAGEMENT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'

def toggle_theme():
    st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'

# --- PAGE CONFIGURATION & MENU ITEMS ---
st.set_page_config(
    page_title="Tradl Flow | Financial Intelligence", 
    layout="wide", 
    page_icon="🌊",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/papilo-topato',
        'Report a bug': "https://x.com/papilo_topato",
        'About': """
        ### Tradl Flow v3.0
        **Built by Raghuram K S**
        
        An AI-Powered Financial Intelligence System built for the Tradl Hackathon.
        Integrates Real-time News, Stock Data, and Context-Aware AI Agents.
        """
    }
)

# --- DYNAMIC CSS INJECTION ---
if st.session_state.theme == 'dark':
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#1e1e1e"
    metric_label = "#b0b0b0"
    shadow = "rgba(0,0,0,0.5)"
else:
    bg_color = "#ffffff"       # Pure White Background
    text_color = "#000000"     # Pitch Black Text
    card_bg = "#f0f2f6"        # Light Gray Card to differentiate from BG
    metric_label = "#31333F"   # Dark Gray for labels
    shadow = "rgba(0,0,0,0.1)"

st.markdown(f"""
    <style>
    /* Force Global Background and Text */
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    
    /* Force ALL headings and text to adopt the theme color */
    h1, h2, h3, h4, h5, h6, p, div, span, li {{ 
        color: {text_color} !important; 
    }}
    
    /* Exceptions for specific badges/buttons that must remain white */
    .positive {{ color: #009900 !important; font-weight: bold; }} /* Darker Green for visibility on light mode */
    .negative {{ color: #cc0000 !important; font-weight: bold; }} /* Darker Red for visibility */
    
    /* Card Styling */
    .market-card {{
        background-color: {card_bg};
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 5px {shadow};
    }}
    
    /* Fix for Metrics inside HTML cards */
    .market-card h1 {{ color: {text_color} !important; margin: 0; }}
    .market-card div {{ color: {text_color}; }}
    
    .news-card {{
        background-color: {card_bg};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border: 1px solid #ddd; /* Softer border for light mode */
    }}
    
    .news-card div {{ color: {text_color}; }}
    
    /* Profile Link Styling */
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
    
    /* Footer */
    .footer {{
        color: {metric_label} !important;
    }}
    
    /* Input Field Styling (Search Box) */
    .stTextInput > div > div > input {{
        color: {text_color};
        background-color: {card_bg};
    }}

    /* Safari Support Fix & General Reset */
    * {{
        -webkit-user-select: auto !important;
        user-select: auto !important;
    }}
    div {{
        -webkit-user-select: auto !important;
    }}
    </style>
    
    <script>
    // Robust JS Injection using MutationObserver to catch Streamlit's dynamic rendering
    const observer = new MutationObserver((mutations) => {{
        mutations.forEach((mutation) => {{
            // 1. Fix Autocomplete on Search Input
            const inputs = document.querySelectorAll('input');
            inputs.forEach(input => {{
                if (!input.hasAttribute('autocomplete')) {{
                    input.setAttribute('autocomplete', 'off');
                }}
            }});
            
            // 2. Fix ARIA on Buttons
            const buttons = document.querySelectorAll('button');
            buttons.forEach(btn => {{
                if (!btn.getAttribute('aria-label')) {{
                    btn.setAttribute('aria-label', 'Button');
                }}
            }});
            
            // 3. Fix ARIA on Main Menu (Specific Target)
            const menu = document.querySelector('[data-testid="stMainMenu"]');
            if (menu && menu.getAttribute('aria-expanded') === 'false') {{
                menu.setAttribute('aria-expanded', 'true'); // Hack to satisfy validator
            }}
        }});
    }});
    
    // Start observing the document body
    observer.observe(document.body, {{ childList: true, subtree: true }});
    </script>
""", unsafe_allow_html=True)

# --- LOADING LOGIC ---
def fetch_data_with_progress(query):
    progress_bar = st.progress(0, text="Initializing Tradl Flow Engine...")
    
    # Step 1: Resolve Query
    progress_bar.progress(20, text="🤖 Agents resolving Entity & Mapping Parent Companies...")
    try:
        res = requests.post(f"{API_URL}/resolve_and_fetch", json={"query": query})
        data = res.json()
    except:
        progress_bar.empty()
        return None, None
        
    if data.get("type") == "error":
        progress_bar.empty()
        return None, None

    # Step 2: Fetch News
    term_display = data.get('search_terms', [query])[0]
    progress_bar.progress(60, text=f"🌍 Scanning Global Media for '{term_display}'...")
    
    terms_str = ",".join(data.get('search_terms', [query]))
    news_res = requests.post(f"{API_URL}/ingest_news", json={"query": terms_str})
    news_data = news_res.json().get('articles', [])
    
    progress_bar.progress(100, text="✨ Rendering Intelligence Dashboard...")
    time.sleep(0.5)
    progress_bar.empty()
    
    return data, news_data

# --- RENDER FUNCTIONS ---
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
            <div class="market-card" style="padding:15px; position:relative;">
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
            
        st.markdown(f"""
        <div class="news-card">
            <div style="font-size:11px; color:#888;">{badge} 📅 {item['date']} | {item['source']}</div>
            <div style="font-weight:600; font-size:16px; margin: 5px 0;">{item['text']}</div>
            <a href="{item['link']}" target="_blank" style="color:#4CAF50; text-decoration:none; font-size:12px;">Read Full Story ↗</a>
        </div>
        """, unsafe_allow_html=True)

# --- NAVIGATION SIDEBAR ---
with st.sidebar:
    st.title("🌊 Tradl Flow")
    st.caption("AI-Powered Market Intelligence")
    
    page = st.radio("Navigation", ["🚀 Terminal", "👤 About the Architect"])
    
    st.divider()
    
    # Theme Toggle
    btn_label = "☀️ Light Mode" if st.session_state.theme == 'dark' else "🌙 Dark Mode"
    st.button(btn_label, on_click=toggle_theme)
    
    st.markdown("---")
    st.caption("© 2025 Tradl Flow")
    st.caption("Built by **Raghuram K S**")

# --- PAGE ROUTING ---

if page == "🚀 Terminal":
    # === TERMINAL VIEW ===
    st.title("🌊 Tradl Flow")
    st.markdown("#### The Intelligent Market Workspace")
    
    query = st.text_input("Search (e.g., 'Domino\\'s', 'Tata', 'Gold', 'Banks')...", placeholder="Type a company, sector, or brand...")

    if query:
        if query.lower() == "market":
            st.info("Market Overview Mode")
        else:
            data, news = fetch_data_with_progress(query)
            if data:
                if data['type'] == 'stock': render_stock(data)
                elif data['type'] in ['commodity', 'grid_view']: render_grid_view(data)
                render_news(news)
            else:
                st.error("❌ Data not found. Try a different term.")
    else:
        # Default Landing
        st.info("👋 Welcome to Tradl Flow. Start by searching for a stock (e.g., 'Zomato'), a sector ('Banks'), or a group ('Adani').")
        
        # Quick access chips
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("🏦 Banks"): fetch_data_with_progress("Banks")
        if c2.button("🚗 Auto"): fetch_data_with_progress("Auto")
        if c3.button("🛢️ Oil"): fetch_data_with_progress("Oil")
        if c4.button("🪙 Gold"): fetch_data_with_progress("Gold")

elif page == "👤 About the Architect":
    # === PROFILE VIEW ===
    st.title("Raghuram K S")
    st.markdown("#### 🚀 Engineer | Product Thinker | AI & No-Code Builder")
    
    # Social Links Row
    st.markdown(f"""
    <div>
        <a href="https://www.linkedin.com/in/papilo-topato" class="profile-link" target="_blank">🔗 LinkedIn</a>
        <a href="https://github.com/papilo-topato" class="profile-link" target="_blank">💻 GitHub</a>
        <a href="https://x.com/papilo_topato" class="profile-link" target="_blank">🐦 X (Twitter)</a>
        <a href="https://www.youtube.com/@papilo-topato" class="profile-link" target="_blank">🎥 YouTube</a>
        <a href="https://instagram.com/papilo_topato?igshid=ZDc4ODBmNjlmNQ==" class="profile-link" target="_blank">📸 Instagram</a>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### About Me
        Exploring the fast-moving intersection of **AI, no-code development, and electronics**—and currently open to opportunities where these worlds collide.

        Previously, I worked as a **Management Trainee** in the central think tank at **Electronic Payment and Services (EPS)**, where I operated at the crossroads of business strategy, product thinking, and hands-on tech execution. From shaping growth strategies to building AI capabilities from scratch, I learned to turn complexity into clarity—and ideas into impact.

        With a background in **Electronics & Communication Engineering** and experience as a **Smart India Hackathon 2022 Hardware Edition finalist**, I’m deeply curious about how intelligence can be embedded into systems—whether that’s smarter software, automated workflows, or hardware-AI hybrids that blur the line between physical and digital.
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
    
    st.info("🤝 If you're working on something interesting in AI, automation, product, or no-code, or if you’re exploring how hardware and intelligence merge—let’s connect.")

# --- FOOTER ---
st.markdown("""
    <div style="position:fixed; bottom:0; left:0; width:100%; text-align:center; background-color:rgba(0,0,0,0); pointer-events:none; font-size:12px; opacity:0.7;">
        Developed and built by <b>Raghuram K S</b>
    </div>
""", unsafe_allow_html=True)
