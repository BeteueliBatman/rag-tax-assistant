import os
from typing import List, Dict
from pathlib import Path
import json
from dotenv import load_dotenv
from groq import Groq
from .vector_store import VectorStore

# Load environment variables
load_dotenv()

class RAGPipeline:
    def __init__(self):
        print("🚀 Initializing RAG Pipeline...")
        
        # Vector Store
        print("📚 Loading vector store...")
        self.vector_store = VectorStore()
        
        # Load chunks
        chunks_file = Path('data/processed/chunks.json')
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
            
            if self.vector_store.collection.count() == 0:
                print("📦 Building vector store...")
                self.vector_store.add_chunks(chunks)
        
        # Groq API setup - Streamlit Secrets support
        print("🤖 Connecting to Groq...")
        
        # Try Streamlit secrets first, then environment variable
        groq_key = None
        try:
            import streamlit as st
            groq_key = st.secrets.get("GROQ_API_KEY")
        except:
            pass
        
        if not groq_key:
            groq_key = os.getenv('GROQ_API_KEY')
        
        if not groq_key:
            raise ValueError("❌ GROQ_API_KEY not found in secrets or .env!")
        
        self.client = Groq(api_key=groq_key)
        self.model = "llama-3.3-70b-versatile"
        
        print("✅ RAG Pipeline ready!\n")
    
    def create_prompt(self, query: str, context_chunks: List[Dict]) -> tuple:
        """Prompt-ის შექმნა კონტექსტით"""
        
        context_text = ""
        sources = []
        
        for i, chunk in enumerate(context_chunks, 1):
            context_text += f"\n--- წყარო {i} ---\n"
            context_text += f"დოკუმენტი: {chunk['metadata']['title']}\n"
            context_text += f"URL: {chunk['metadata']['source']}\n"
            context_text += f"შინაარსი: {chunk['text']}\n"
            
            sources.append({
                'number': i,
                'title': chunk['metadata']['title'],
                'url': chunk['metadata']['source']
            })
        
        prompt = f"""შენ ხარ AI ასისტენტი, რომელიც ეხმარება მომხმარებლებს საგადასახადო და საბაჟო საკითხებში.

შენი დავალებაა უპასუხო მომხმარებლის კითხვას მოცემული კონტექსტის საფუძველზე.

**მნიშვნელოვანი წესები:**
1. უპასუხე ᲛᲮᲝᲚᲝᲓ კონტექსტში არსებული ინფორმაციის საფუძველზე
2. თუ კონტექსტში არ არის პასუხი, ამბობ: "ბოდიში, ამ კითხვაზე პასუხი არ მოიძებნა მოწოდებულ დოკუმენტებში."
3. ᲧᲝᲕᲔᲚᲗᲕᲘᲡ მიუთითე რომელი წყაროდან მოდის ინფორმაცია (წყარო 1, წყარო 2, და ა.შ.)
4. იყავი ზუსტი და კონკრეტული
5. გამოიყენე მარტივი, გასაგები ქართული ენა

**კონტექსტი (დოკუმენტებიდან):**
{context_text}

**მომხმარებლის კითხვა:** {query}

**შენი პასუხი:**"""
        
        return prompt, sources
    
    def answer_question(self, query: str, n_results=5) -> Dict:
        """კითხვაზე პასუხის გენერირება"""
        
        print(f"🔍 Searching relevant documents for: {query}")
        
        # 1. Vector Search
        relevant_chunks = self.vector_store.search(query, n_results=n_results)
        
        print(f"✓ Found {len(relevant_chunks)} relevant chunks")
        
        # 2. Prompt-ის შექმნა
        prompt, sources = self.create_prompt(query, relevant_chunks)
        
        # 3. Groq-ის გამოძახება
        print("🤖 Generating answer...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "შენ ხარ დამხმარე AI ასისტენტი საგადასახადო საკითხებში."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            print("✓ Answer generated!\n")
            
            return {
                'query': query,
                'answer': answer,
                'sources': sources,
                'relevant_chunks': relevant_chunks
            }
        
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            return {
                'query': query,
                'answer': f"ბოდიში, პასუხის გენერირებისას მოხდა შეცდომა: {str(e)}",
                'sources': sources,
                'relevant_chunks': relevant_chunks
            }

def main():
    rag = RAGPipeline()
    
    print("\n" + "="*80)
    print("🧪 Testing RAG Pipeline")
    print("="*80 + "\n")
    
    test_questions = [
        "რა არის დღგ?",
        "როგორ უნდა მოვახდინო საბაჟო დეკლარირება?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*80}")
        print(f"ტესტი {i}/{len(test_questions)}")
        print(f"{'='*80}\n")
        
        result = rag.answer_question(question)
        
        print(f"❓ კითხვა: {result['query']}")
        print(f"\n💬 პასუხი:\n{result['answer']}")
        
        print(f"\n📚 წყაროები:")
        for source in result['sources']:
            print(f"  • {source['title']}")
            print(f"    {source['url']}")
        
        print()

if __name__ == "__main__":
    main()