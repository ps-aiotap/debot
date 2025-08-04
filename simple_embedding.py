import os
import yaml
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from cache_utils import cache_embedding, get_cached_embedding
from dotenv import load_dotenv
from persona_manager import PersonaManager

load_dotenv()


class SimpleEmbeddingService:
    def __init__(self, config_path: str = "config.yaml", persona_manager: Optional[PersonaManager] = None):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Use configurable embedding model
        embedding_model_name = self.config.get('embedding', {}).get('model', 'all-MiniLM-L6-v2')
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print(f"DEBUG: Using embedding model: {embedding_model_name}")

        # Initialize ChromaDB HTTP client
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        print(f"DEBUG: Connecting to ChromaDB at {host}:{port}")
        
        # Initialize persona manager
        self.persona_manager = persona_manager or PersonaManager()
        self.collections = {}

        try:
            # Try different client initialization for 0.4.15 compatibility
            import requests

            response = requests.get(f"http://{host}:{port}/api/v2/heartbeat")
            print(f"DEBUG: Direct HTTP test: {response.status_code}")

            self.chroma_client = chromadb.Client(
                chromadb.config.Settings(
                    chroma_api_impl="chromadb.api.fastapi.FastAPI",
                    chroma_server_host=host,
                    chroma_server_http_port=str(port),
                )
            )
            print("DEBUG: ChromaDB client created with Settings")
            # Initialize collections for current persona
            self._initialize_collections()
            print("DEBUG: ChromaDB collections initialized")
        except Exception as e:
            print(f"DEBUG: ChromaDB connection failed: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            # Fallback to HttpClient
            try:
                self.chroma_client = chromadb.HttpClient(host=host, port=port)
                # Initialize collections for current persona
                self._initialize_collections()
                print("DEBUG: Fallback HttpClient worked")
            except Exception as e2:
                print(f"DEBUG: Fallback also failed: {e2}")
                raise e2

    def _initialize_collections(self):
        """Initialize collections for current persona."""
        collection_names = self.persona_manager.get_collections()
        for name in collection_names:
            try:
                self.collections[name] = self.chroma_client.get_or_create_collection(name)
                print(f"DEBUG: Collection '{name}' initialized")
            except Exception as e:
                print(f"ERROR: Failed to initialize collection '{name}': {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding with Redis caching."""
        cached_embedding = get_cached_embedding(text)
        if cached_embedding:
            return cached_embedding

        embedding = self.embedding_model.encode(text).tolist()
        cache_embedding(text, embedding)
        return embedding

    def add_documents(self, documents: List[Dict[str, str]], collection_name: str = None):
        """Add documents to specified collection or all persona collections."""
        import hashlib
        import json

        # Create hash of all document content
        doc_content = json.dumps(
            [{"filename": d["filename"], "content": d["content"]} for d in documents],
            sort_keys=True,
        )
        current_hash = hashlib.md5(doc_content.encode()).hexdigest()
        
        # Determine which collections to use
        if collection_name:
            collections_to_use = [collection_name]
        else:
            collections_to_use = self.persona_manager.get_collections()
        
        for coll_name in collections_to_use:
            # Ensure collection exists
            if coll_name not in self.collections:
                try:
                    self.collections[coll_name] = self.chroma_client.get_or_create_collection(coll_name)
                    print(f"DEBUG: Created collection '{coll_name}'")
                except Exception as e:
                    print(f"ERROR: Failed to create collection '{coll_name}': {e}")
                    continue
            
            collection = self.collections[coll_name]
            
            # Check for force reindex flag
            if os.getenv("FORCE_REINDEX", "").lower() == "true":
                print(f"DEBUG: FORCE_REINDEX=true, clearing and re-indexing collection '{coll_name}'")
                try:
                    # Delete and recreate collection instead of trying to delete all documents
                    self.chroma_client.delete_collection(coll_name)
                    self.collections[coll_name] = self.chroma_client.get_or_create_collection(coll_name)
                    collection = self.collections[coll_name]
                except Exception as e:
                    print(f"ERROR: Failed to reset collection '{coll_name}': {e}")
                    continue
            else:
                # Check if hash matches stored hash
                try:
                    existing_docs = collection.get(ids=["content_hash"])
                    if (
                        existing_docs["documents"]
                        and existing_docs["documents"][0] == current_hash
                    ):
                        print(
                            f"DEBUG: Content hash matches for '{coll_name}', skipping re-indexing ({len(documents)} docs)"
                        )
                        continue
                    else:
                        print(f"DEBUG: Content changed for '{coll_name}', clearing old documents")
                    # Clear existing documents
                    try:
                        # Delete and recreate collection instead of trying to delete all documents
                        self.chroma_client.delete_collection(coll_name)
                        self.collections[coll_name] = self.chroma_client.get_or_create_collection(coll_name)
                        collection = self.collections[coll_name]
                    except Exception as e:
                        print(f"ERROR: Failed to reset collection '{coll_name}': {e}")
                        continue
                except:
                    print(f"DEBUG: No existing hash found for '{coll_name}', proceeding with indexing")

            print(f"DEBUG: Adding {len(documents)} new documents to collection '{coll_name}'")
            for i, doc in enumerate(documents):
                if i % 10 == 0:  # Progress every 10 docs
                    print(
                        f"DEBUG: Processing document {i+1}/{len(documents)} - {doc['filename']}"
                    )
                embedding = self.get_embedding(doc["content"])
                collection.add(
                    embeddings=[embedding],
                    documents=[doc["content"]],
                    metadatas=[
                        {
                            "source": doc["source"],
                            "filename": doc["filename"],
                            "type": doc["type"],
                        }
                    ],
                    ids=[f"doc_{i}"],
                )
            # Store content hash
            collection.add(
                documents=[current_hash],
                ids=["content_hash"],
                metadatas=[{"type": "hash", "doc_count": len(documents)}],
            )
            print(
                f"DEBUG: Finished adding {len(documents)} documents to '{coll_name}' with hash {current_hash[:8]}..."
            )

    def search(self, query: str, n_results: int = 5, collection_name: str = None) -> List[Dict]:
        """Search across all collections for the current persona or a specific collection."""
        query_embedding = self.get_embedding(query)
        all_results = []
        
        # Determine which collections to search
        if collection_name:
            collections_to_search = [collection_name]
        else:
            collections_to_search = self.persona_manager.get_collections()
        
        for coll_name in collections_to_search:
            if coll_name not in self.collections:
                print(f"WARNING: Collection '{coll_name}' not initialized, skipping search")
                continue
                
            collection = self.collections[coll_name]
            try:
                results = collection.query(
                    query_embeddings=[query_embedding], n_results=n_results
                )
                
                # Process results from this collection
                if results["documents"] and results["documents"][0]:
                    for i in range(len(results["documents"][0])):
                        all_results.append(
                            {
                                "content": results["documents"][0][i],
                                "metadata": results["metadatas"][0][i],
                                "distance": results["distances"][0][i],
                                "collection": coll_name
                            }
                        )
            except Exception as e:
                print(f"ERROR: Failed to search collection '{coll_name}': {e}")
        
        # Sort by relevance (distance)
        all_results.sort(key=lambda x: x["distance"])
        
        # Return top N results across all collections
        return all_results[:n_results]
