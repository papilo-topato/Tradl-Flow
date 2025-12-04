# graph.py
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
from database import global_db
import json

# --- SETUP ---
llm = ChatOllama(model="llama3.2", temperature=0)

# --- STATE ---
class AgentState(TypedDict):
    article_text: str
    is_duplicate: bool
    entities: dict

# --- NODES ---

def deduplication_node(state: AgentState):
    """
    Agent 1: Checks if story exists.
    """
    print("--- Step 1: Deduplication Check ---")
    text = state['article_text']
    results = global_db.similarity_search(text, k=1)
    
    is_dup = False
    if results:
        score = results[0][1]
        # Adjust threshold based on your previous test results
        if score < 1.1: 
            is_dup = True
            print(f" -> Duplicate detected (Score: {score:.2f})")
    
    return {"is_duplicate": is_dup}

def entity_extraction_node(state: AgentState):
    """
    Agent 2: Extracts metadata (Companies, Sectors).
    """
    print("--- Step 2: Entity Extraction ---")
    text = state['article_text']
    
    prompt = f"""
    You are a Senior Financial Analyst. Analyze this news.
    1. Identify Companies (e.g., 'Zomato', 'HDFC Bank').
    2. Identify the SPECIFIC Sector (e.g., 'Consumer Tech', 'Banking', 'Energy', 'Commodities').
    3. Identify Sentiment (Positive/Negative).

    CRITICAL: Do not guess. If it's about food delivery, the sector is 'Consumer Tech', NOT 'Commodities'.

    Return JSON ONLY:
    {{
        "companies": ["Name"],
        "sectors": ["Specific Sector"],
        "sentiment": "string"
    }}
    
    News: {text}
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()
    
    # Clean up the LLM response to ensure valid JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
        
    try:
        data = json.loads(content)
        print(f" -> Extracted: {data}")
    except:
        print(" -> JSON Parse Error, using empty entities.")
        data = {"companies": [], "sectors": []}
        
    return {"entities": data}

def storage_node(state: AgentState):
    """
    Agent 3: Saves the article WITH the extracted metadata.
    """
    print("--- Step 3: Storage ---")
    text = state['article_text']
    entities = state['entities']
    
    # Flatten metadata for storing (Vector DBs like flat strings/lists)
    # We join lists into strings: ['HDFC', 'ICICI'] -> "HDFC, ICICI"
    meta = {
        "companies": ", ".join(entities.get("companies", [])),
        "sectors": ", ".join(entities.get("sectors", []))
    }
    
    global_db.add_texts([text], [meta])
    print(" -> Saved to DB with Metadata.")
    return {}

# --- WORKFLOW ---
workflow = StateGraph(AgentState)

workflow.add_node("deduplicator", deduplication_node)
workflow.add_node("analyst", entity_extraction_node)
workflow.add_node("storage", storage_node)

workflow.set_entry_point("deduplicator")

def route_step(state):
    if state['is_duplicate']:
        return END
    return "analyst"

workflow.add_conditional_edges(
    "deduplicator",
    route_step,
    {END: END, "analyst": "analyst"}
)

workflow.add_edge("analyst", "storage")
workflow.add_edge("storage", END)

app = workflow.compile()
