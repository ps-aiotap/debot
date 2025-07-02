import os
from dotenv import load_dotenv
from ingest.load_docs import load_documents

load_dotenv()

# Test document loading
print("Testing document loading...")
docs = load_documents(os.getenv('DOCS_DIR', './data/mds'))
print(f"Found {len(docs)} documents:")

for doc in docs:
    print(f"- {doc['filename']}: {len(doc['content'])} characters")
    if "Budget Authority" in doc['content']:
        print(f"  ✅ Contains 'Budget Authority'")
    else:
        print(f"  ❌ Does NOT contain 'Budget Authority'")

# Test embedding service
print("\nTesting embedding service...")
try:
    from simple_embedding import SimpleEmbeddingService
    embedding_service = SimpleEmbeddingService()
    
    if docs:
        print("Adding documents to ChromaDB...")
        embedding_service.add_documents(docs)
        
        print("Testing search...")
        results = embedding_service.search("Budget Authority", n_results=3)
        print(f"Search returned {len(results)} results")
        
        for i, result in enumerate(results):
            print(f"{i+1}. Distance: {result['distance']:.3f}")
            print(f"   Content preview: {result['content'][:100]}...")
    
except Exception as e:
    print(f"Error: {e}")