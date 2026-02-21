import os
import json
from pathlib import Path
from typing import List, Dict
from dotenv import load_dotenv
from groq import Groq
from .vector_store import VectorStore

load_dotenv()

class RAGPipeline:
    def __init__(self):
        self.vector_store = VectorStore()
        
        chunks_file = Path('data/processed/chunks.json')
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            if self.vector_store.collection.count() == 0:
                self.vector_store.add_chunks(chunks)
        
        groq_key = None
        try:
            import streamlit as st
            groq_key = st.secrets.get("GROQ_API_KEY")
        except:
            pass
        
        if not groq_key:
            groq_key = os.getenv('GROQ_API_KEY')
        
        if not groq_key:
            raise ValueError("GROQ_API_KEY not found")
        
        self.client = Groq(api_key=groq_key)
        self.model = "llama-3.3-70b-versatile"
    
    def answer_question(self, query: str, n_results=5) -> Dict:
        relevant_chunks = self.vector_store.search(query, n_results=n_results)
        
        context = ""
        sources = []
        for i, chunk in enumerate(relevant_chunks, 1):
            context += f"\nწყარო {i}: {chunk['text']}\n"
            sources.append({'number': i, 'title': chunk['metadata']['title'], 'url': chunk['metadata']['source']})
        
        prompt = f"""შენ ხარ AI ასისტენტი საგადასახადო საკითხებში.
        
უპასუხე კითხვას კონტექსტის საფუძველზე ქართულად:

კონტექსტი:
{context}

კითხვა: {query}

პასუხი:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=800
            )
            return {'query': query, 'answer': response.choices[0].message.content, 'sources': sources}
        except Exception as e:
            return {'query': query, 'answer': f"შეცდომა: {str(e)}", 'sources': sources}