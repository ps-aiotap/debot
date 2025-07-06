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
        host = os.getenv('CHROMA_HOST', 'localhost')
        port = int(os.getenv('CHROMA_PORT', '8000'))
        print(f"DEBUG: Connecting to ChromaDB at {host}:{port}")
        
        try:
            # Try different client initialization for 0.4.15 compatibility
            import requests
            response = requests.get(f"http://{host}:{port}/api/v1/heartbeat")
            print(f"DEBUG: Direct HTTP test: {response.status_code}")
            
            self.chroma_client = chromadb.Client(
                chromadb.config.Settings(
                    chroma_api_impl="chromadb.api.fastapi.FastAPI",
                    chroma_server_host=host,
                    chroma_server_http_port=str(port)
                )
            )
            print("DEBUG: ChromaDB client created with Settings")
            self.collection = self.chroma_client.get_or_create_collection("documents")
            print("DEBUG: ChromaDB collection created/retrieved")
        except Exception as e:
            print(f"DEBUG: ChromaDB connection failed: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            # Fallback to HttpClient
            try:
                self.chroma_client = chromadb.HttpClient(host=host, port=port)
                self.collection = self.chroma_client.get_or_create_collection("documents")
                print("DEBUG: Fallback HttpClient worked")
            except Exception as e2:
                print(f"DEBUG: Fallback also failed: {e2}")
                raise e2
    
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
        # Check if documents already exist
        try:
            existing_count = self.collection.count()
            print(f"DEBUG: Found {existing_count} existing documents in ChromaDB")
            if existing_count > 0:
                print("DEBUG: Documents already exist, skipping re-indexing")
                return
        except:
            print("DEBUG: Could not check existing documents, proceeding with indexing")
        
        print(f"DEBUG: Adding {len(documents)} new documents to ChromaDB")
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
        print(f"DEBUG: Finished adding {len(documents)} documents")
    
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