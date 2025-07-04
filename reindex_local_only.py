import os
from dotenv import load_dotenv
from simple_embedding import SimpleEmbeddingService
from ingest.load_docs import load_documents
from ingest.load_pdfs import load_pdfs

load_dotenv()

print("🔄 Re-indexing LOCAL documents only...")

# Initialize embedding service
embedding_service = SimpleEmbeddingService()

# Clear existing collection
try:
    embedding_service.chroma_client.delete_collection("documents")
    print("✅ Cleared old index")
except:
    print("ℹ️ No existing collection to clear")

# Recreate collection
embedding_service.collection = embedding_service.chroma_client.get_or_create_collection("documents")

# Load only local documents
all_documents = []

# Load from DOCS_DIR
if os.getenv('DOCS_DIR'):
    docs = load_documents(os.getenv('DOCS_DIR'))
    all_documents.extend(docs)
    print(f"📄 Loaded {len(docs)} documents from DOCS_DIR")

# Load from MDS_DIR  
if os.getenv('MDS_DIR'):
    mds_docs = load_documents(os.getenv('MDS_DIR'))
    all_documents.extend(mds_docs)
    print(f"📝 Loaded {len(mds_docs)} documents from MDS_DIR")

# Load from PDF_DIR
if os.getenv('PDF_DIR'):
    pdf_docs = load_pdfs(os.getenv('PDF_DIR'))
    all_documents.extend(pdf_docs)
    print(f"📋 Loaded {len(pdf_docs)} PDFs from PDF_DIR")

print(f"\n📊 Total local documents: {len(all_documents)}")

# Index documents
if all_documents:
    embedding_service.add_documents(all_documents)
    print("✅ Local documents indexed successfully!")
    
    # Test search
    results = embedding_service.search("dashboard acquisition", n_results=3)
    print(f"\n🔍 Test search results: {len(results)} found")
    
    for i, result in enumerate(results):
        source_type = "LOCAL" if any(path in result['metadata'].get('source', '') for path in ['data/mds', 'data/docs', 'data/pdfs']) else "WEB"
        print(f"{i+1}. [{source_type}] {result['metadata'].get('filename', 'Unknown')}")
        print(f"   Distance: {result['distance']:.3f}")
        print(f"   Preview: {result['content'][:100]}...")
        print()
else:
    print("❌ No local documents found!")

print("\n🚀 Run 'python simple_main.py' to use the chatbot with local documents only.")