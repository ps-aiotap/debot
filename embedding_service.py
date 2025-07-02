import os
from typing import List, Dict
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
from cache_utils import cache_embedding, get_cached_embedding
import yaml
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class EmbeddingService:
    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Use local sentence-transformers for embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB HTTP client
        self.chroma_client = chromadb.HttpClient(
            host=os.getenv('CHROMA_HOST', 'localhost'),
            port=int(os.getenv('CHROMA_PORT', '8000'))
        )
        self.collection = self.chroma_client.get_or_create_collection("documents")
        
        # Configure LlamaIndex
        Settings.chunk_size = self.config['ingestion']['chunk_size']
        Settings.chunk_overlap = self.config['ingestion']['chunk_overlap']
    
    def get_embedding_with_cache(self, text: str) -> List[float]:
        """Get embedding with Redis caching."""
        # Check cache first
        cached_embedding = get_cached_embedding(text)
        if cached_embedding:
            return cached_embedding
        
        # Generate new embedding
        embedding = self.embedding_model.encode(text).tolist()
        
        # Cache the result
        cache_embedding(text, embedding)
        
        return embedding
    
    def create_index(self, documents: List[Dict[str, str]]) -> VectorStoreIndex:
        """Create vector index from documents."""
        # Convert to LlamaIndex documents
        llama_docs = []
        for doc in documents:
            llama_doc = Document(
                text=doc['content'],
                metadata={
                    'source': doc['source'],
                    'filename': doc['filename'],
                    'type': doc['type']
                }
            )
            llama_docs.append(llama_doc)
        
        # Create vector store
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        
        # Create index
        index = VectorStoreIndex.from_documents(
            llama_docs,
            vector_store=vector_store
        )
        
        return index
    
    def load_existing_index(self) -> VectorStoreIndex:
        """Load existing vector index."""
        vector_store = ChromaVectorStore(chroma_collection=self.collection)
        return VectorStoreIndex.from_vector_store(vector_store)