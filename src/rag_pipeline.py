import os
from typing import List, Dict
from pathlib import Path
import json
from dotenv import load_dotenv
from groq import Groq
from vector_store import VectorStore

load_dotenv()

class RAGPipeline:
    def __init__(self):
        print("🚀 Initializing RAG Pipeline...")
        
        self.vector_store = VectorStore()
        
        chunks_file = Path('data/processed/chunks.json')
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            if self.vector_store.collection.count() == 0:
                self.vector_store.add_chunks(chunks)
        
        # Groq (უფასო და სწრაფი!)
        groq_key = os.getenv('GROQ_API_KEY')
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY not in .env!")
        
        self.client = Groq(api_key=groq_key)
        self.model = "llama-3.3-70b-versatile"  # ქართულს კარგად იცნობს
        
        print("✅ RAG ready!\n")
    
    def create_prompt(self, query: str, context_chunks: List[Dict]) -> tuple:
        context_text = ""
        sources = []
        
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\nწყარო {i}: {chunk['text']}\n"
            sources.append({
                'number': i,
                'title': chunk['metadata']['title'],
                'url': chunk['metadata']['source']
            })
        
        prompt = f"""შენ ხარ AI ასისტენტი საგადასახადო საკითხებში.

უპასუხე კითხვას კონტექსტის საფუძველზე:

{context_text}

კითხვა: {query}

პასუხი (ქართულად, მოკლედ):"""
        
        return prompt, sources
    
    def answer_question(self, query: str, n_results=5) -> Dict:
        print(f"🔍 {query}")
        
        relevant_chunks = self.vector_store.search(query, n_results)
        print(f"✓ Found {len(relevant_chunks)} chunks")
        
        prompt, sources = self.create_prompt(query, relevant_chunks)
        
        print("🤖 Generating...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            print("✓ Done!\n")
            
            return {
                'query': query,
                'answer': answer,
                'sources': sources
            }
        except Exception as e:
            return {
                'query': query,
                'answer': f"შეცდომა: {e}",
                'sources': sources
            }

def main():
    rag = RAGPipeline()
    
    for q in ["რა არის დღგ?"]:
        result = rag.answer_question(q)
        print(f"❓ {result['query']}")
        print(f"💬 {result['answer']}\n")
        for s in result['sources']:
            print(f"  • {s['title']}")

if __name__ == "__main__":
    main()