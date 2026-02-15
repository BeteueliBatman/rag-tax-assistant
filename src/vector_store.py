from sentence_transformers import SentenceTransformer
import chromadb
import json
from pathlib import Path
from typing import List, Dict

class VectorStore:
    def __init__(self):
        print("🔧 Initializing Vector Store...")
        
        # ქართული ტექსტისთვის - პატარა და სწრაფი model
        print("📥 Loading embedding model (first time: ~100MB download)...")
        
        # პატარა, სწრაფი model
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✓ Model loaded!")
        
        # ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="data/chroma_db")
        
        # Collection
        try:
            self.chroma_client.delete_collection("tax_documents")
        except:
            pass
        
        self.collection = self.chroma_client.create_collection(
            name="tax_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✓ Vector store ready!\n")
    
    def embed_text(self, text: str) -> List[float]:
        """ტექსტის embedding-ად გარდაქმნა"""
        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding.tolist()
    
    def add_chunks(self, chunks: List[Dict]):
        """chunks-ის დამატება"""
        print(f"📦 Adding {len(chunks)} chunks to vector store...")
        
        batch_size = 32
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(chunks) + batch_size - 1) // batch_size
            
            print(f"  Batch {batch_num}/{total_batches}...", end=' ')
            
            texts = [chunk['text'] for chunk in batch]
            ids = [str(chunk['id']) for chunk in batch]
            metadatas = [{
                'source': chunk['source'],
                'title': chunk['title'],
                'chunk_index': chunk['chunk_index']
            } for chunk in batch]
            
            # Embeddings batch-ად (ეფექტურია)
            embeddings = self.embedding_model.encode(
                texts,
                normalize_embeddings=True,
                show_progress_bar=False
            ).tolist()
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas
            )
            
            print(f"✓")
        
        print(f"\n✅ Vector store built!")
        print(f"📊 Total: {self.collection.count()} documents")
    
    def search(self, query: str, n_results=5) -> List[Dict]:
        """ძებნა"""
        query_embedding = self.embed_text(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return formatted

def main():
    chunks_file = Path('data/processed/chunks.json')
    
    if not chunks_file.exists():
        print("❌ chunks.json not found!")
        print("   Run: python src/text_processor.py")
        return
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    vector_store = VectorStore()
    vector_store.add_chunks(chunks)
    
    # ტესტი
    print("\n" + "="*80)
    print("🧪 Testing search...\n")
    
    for query in ["რა არის დღგ?", "საბაჟო დეკლარაცია"]:
        print(f"\n🔍 {query}")
        results = vector_store.search(query, n_results=2)
        
        for i, r in enumerate(results):
            print(f"  [{i+1}] {r['metadata']['title'][:50]}")
            print(f"      Score: {1-r['distance']:.3f}")

if __name__ == "__main__":
    main()
