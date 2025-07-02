import os
from dotenv import load_dotenv
from ingest.load_docs import load_documents
from simple_embedding import SimpleEmbeddingService

load_dotenv()

print("Clearing ChromaDB and re-indexing documents...")

# Initialize embedding service
embedding_service = SimpleEmbeddingService()

# Delete existing collection and recreate
try:
    embedding_service.chroma_client.delete_collection("documents")
    print("✅ Cleared old data")
except:
    print("ℹ️ No existing collection to clear")

# Recreate collection
embedding_service.collection = embedding_service.chroma_client.get_or_create_collection("documents")

# Load only local documents
docs = load_documents(os.getenv('DOCS_DIR', './data/mds'))
print(f"Loading {len(docs)} documents...")

# Add documents
embedding_service.add_documents(docs)
print("✅ Documents indexed")

# Test search
results = embedding_service.search("Budget Authority", n_results=3)
print(f"\nSearch results for 'Budget Authority': {len(results)} found")

for i, result in enumerate(results):
    print(f"{i+1}. Distance: {result['distance']:.3f}")
    print(f"   Source: {result['metadata'].get('filename', 'Unknown')}")
    print(f"   Preview: {result['content'][:100]}...")
    print()