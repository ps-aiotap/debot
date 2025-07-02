import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import chromadb
from cache_utils import cache_embedding, get_cached_embedding
from dotenv import load_dotenv

load_dotenv()

class SimpleEmbeddingService:
    def __init__(self):
        # Use local sentence-transformers for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB HTTP client
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv('CHROMA_HOST', 'localhost'),
            port=int(os.getenv('CHROMA_PORT', '8000'))
        )
        self.collection = self.chroma_client.get_or_create_collection("documents")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding with Redis caching."""
        cached_embedding = get_cached_embedding(text)
        if cached_embedding:
            return cached_embedding
        
        embedding = self.embedding_model.encode(text).tolist()
        cache_embedding(text, embedding)
        return embedding
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to ChromaDB."""
        for i, doc in enumerate(documents):
            embedding = self.get_embedding(doc['content'])
            self.collection.add(
                embeddings=[embedding],
                documents=[doc['content']],
                metadatas=[{
                    'source': doc['source'],
                    'filename': doc['filename'],
                    'type': doc['type']
                }],
                ids=[f"doc_{i}"]
            )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Search for similar documents."""
        query_embedding = self.get_embedding(query)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        documents = []
        for i in range(len(results['documents'][0])):
            documents.append({
                'content': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })
        
        return documents