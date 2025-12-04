# Tradl Flow: Autonomous Financial Intelligence Engine
### *Turning Market Noise into Alpha using Local LLMs & Agentic Workflows*

**Developer:** Raghuram K S
*   **Data Layer:** yFinance (Live Data) + GoogleNews (Scraping).
*   **Frontend:** Streamlit – *Reactive UI with custom CSS injection.*

### The Data Pipeline
`User Query` $\rightarrow$ `Smart Resolver (NLP)` $\rightarrow$ `Data Swarm (APIs)` $\rightarrow$ `AI Ranker (LLM)` $\rightarrow$ `Dashboard`

---

## 3. Key Capabilities & Engineering Decisions

### A. Intelligent Symbol Resolution (Neuro-Symbolic)
**Challenge:** Users search colloquially (e.g., "Domino's", "Tata"), but APIs need specific tickers (`JUBLFOOD.NS`).
**Solution:** I built a heuristic "Smart Resolver" that maps Brands to Parent Companies and Groups to Sector Grids before fetching data.
*   *Input:* "Domino's" $\rightarrow$ *System:* Maps to `JUBLFOOD.NS` $\rightarrow$ *Output:* Stock Data + Brand News.

### B. The Document Analyst (RAG Pipeline)
**Challenge:** Traders need to digest 50-page earnings reports instantly.
**Solution:** A drag-and-drop RAG module.
1.  **Ingestion:** `pypdf` extracts text from uploaded PDFs.
2.  **Gatekeeper:** Llama 3.2 filters non-financial content ("Not my cup of tea").
3.  **Analysis:** Generates Executive Summary, Sentiment, and Impact Analysis.

### C. Live Architectural Visualization
**Innovation:** Unlike opaque AI tools, Tradl Flow features a **Live Flowchart** in the UI. It visualizes the active state of the LangGraph agents (Green Glow) as data flows through the system, providing transparency to the user.

---

## 4. Visual Walkthrough

### 1. The Dashboard Experience
The interface is designed for high-density information display, featuring a dark mode for reduced eye strain and a "Live Ticker" for market pulses.

![Main Dashboard](screenshots/Main%20dashboard.png)
*Caption: The central command center showing the Search Bar, Quick Access Modules, and the Live Pipeline Visualizer.*

### 2. Context-Aware Visualizations
When a user searches for a specific sector (e.g., "Banks"), the system automatically switches to a **Grid View** to allow for rapid comparison of peers.

![Sector Grid](screenshots/Bank%20sector%20example.png)
*Caption: The Sector Grid View automatically populating top banking stocks with live P/E and Market Cap metrics.*

### 3. The "Stock Face-Off" Engine
A dedicated module for comparative analysis. It fetches real-time metrics for two assets and uses the LLM to generate a comparative verdict based on news sentiment.

![Stock Comparison](screenshots/Stock%20comparison.png)
*Caption: Side-by-side comparison of HDFC vs. SBI, featuring an AI-generated verdict on short-term strength.*

### 4. Under the Hood: The Workflow
The system visualizes the tech stack in real-time, showing the hand-off between the User, the Resolver, the Data Swarm, and the AI Model.

![Workflow](screenshots/Image%20with%20workflow.png)
*Caption: The "Glass Box" AI approach—visualizing the LangGraph agent states in real-time.*

---

## 5. Engineering Challenges & Solutions

| Challenge | Solution |
| :--- | :--- |
| **API Rate Limits** | Implemented caching and "Demo Interceptors" for key stocks to ensure stability during presentations. |
| **LLM Hallucinations** | Used "Strict System Prompts" and a "Gatekeeper" function to reject non-financial queries (e.g., Movie plots). |
| **Data Latency** | Optimized the pipeline by parallelizing the News Fetching and Stock Data Fetching processes. |
| **Unstructured Queries** | Built a "Universal Search" fallback using Yahoo Finance Autocomplete API for unknown tickers. |

---

## 6. Developer Profile

**Raghuram K S**
*Aspiring AI Engineer | Product Thinker*

I sit at the intersection of **Electronics, AI, and Product**. With a background in Electronics & Communication and experience in business strategy at EPS, I build systems that are not just technically sound but solved real-world problems.

**[INSERT IMAGE: About me section.png]**

*   **GitHub:** [github.com/papilo-topato](https://github.com/papilo-topato)
*   **LinkedIn:** [linkedin.com/in/papilo-topato](https://www.linkedin.com/in/papilo-topato)
*   **X (Twitter):** [@papilo_topato](https://x.com/papilo_topato)

---
*Built for the Tradl Hackathon 2025.*
