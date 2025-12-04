# database.py
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import os

# 1. Setup Local Embeddings (Free, runs on CPU)
# We use a specific model optimized for sentence similarity
print("Loading Embedding Model (this happens only once)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

class VectorDB:
    def __init__(self):
        # We use ChromaDB because it's great for local development
        self.db_path = "./chroma_db"
        self.db = Chroma(
            persist_directory=self.db_path, 
            embedding_function=embeddings,
            collection_name="financial_news"
        )

    def add_texts(self, texts, metadatas):
        """
        Adds text to the vector database.
        """
        # Chroma automatically handles deduplication of exact IDs, 
        # but we will handle semantic deduplication in the Agent.
        self.db.add_texts(texts=texts, metadatas=metadatas)
        # Chroma persists automatically in newer versions, but just in case:
        # self.db.persist() 
            
    def similarity_search(self, query, k=1):
        """
        Finds the top k most similar items.
        Returns: List of (Document, score)
        """
        # score < 0.5 usually means very similar (duplicate)
        return self.db.similarity_search_with_score(query, k=k)

    def advanced_search(self, query_text, k=5): # Increased k to 5 to cast a wider net
        """
        Performs a search. 
        In a real production system, we would use an LLM to expand 
        'Banking' -> 'Finance', 'Lending', etc.
        For now, vector search handles the semantic matching well.
        """
        if self.db is None:
            return []
            
        print(f"Searching DB for: {query_text}")
        results = self.db.similarity_search_with_score(query_text, k=k)
        
        cleaned_results = []
        for doc, score in results:
            # --- THE QUALITY FILTER ---
            # If score is > 1.4, it's garbage. Don't show it.
            if score < 1.4: 
                cleaned_results.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
            else:
                print(f"Filtered out low relevance result: {score}")
            
        return cleaned_results

# Global instance
global_db = VectorDB()
