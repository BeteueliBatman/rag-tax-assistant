from sentence_transformers import SentenceTransformer
import chromadb
from typing import List, Dict

class VectorStore:
    def __init__(self):
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.chroma_client = chromadb.PersistentClient(path="data/chroma_db")
        
        try:
            self.collection = self.chroma_client.get_collection("tax_documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name="tax_documents",
                metadata={"hnsw:space": "cosine"}
            )
    
    def embed_text(self, text: str) -> List[float]:
        embedding = self.embedding_model.encode(text, normalize_embeddings=True, show_progress_bar=False)
        return embedding.tolist()
    
    def add_chunks(self, chunks: List[Dict]):
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            texts = [chunk['text'] for chunk in batch]
            ids = [str(chunk['id']) for chunk in batch]
            metadatas = [{'source': chunk['source'], 'title': chunk['title'], 'chunk_index': chunk['chunk_index']} for chunk in batch]
            embeddings = [self.embed_text(text) for text in texts]
            self.collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    
    def search(self, query: str, n_results=5) -> List[Dict]:
        query_embedding = self.embed_text(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=n_results)
        
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        return formatted