#!/usr/bin/env python3

import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to ChromaDB
chroma_host = os.getenv('CHROMA_HOST', 'localhost')
chroma_port = int(os.getenv('CHROMA_PORT', 8000))

client = chromadb.HttpClient(host=chroma_host, port=chroma_port)

print("=== ChromaDB Collections Status ===")
collections = client.list_collections()
print(f"Total collections: {len(collections)}")

for collection in collections:
    print(f"\nCollection: {collection.name}")
    print(f"Count: {collection.count()}")
    
    # Sample a few documents to see what's indexed
    if collection.count() > 0:
        results = collection.peek(limit=3)
        print(f"Sample docs: {len(results['documents'])} documents")
        for i, doc in enumerate(results['documents'][:2]):
            print(f"  Doc {i+1}: {doc[:100]}...")
    else:
        print("  ⚠️  EMPTY COLLECTION")

print("\n=== Expected Collections ===")
expected = ['real_estate_docs', 'digital_marketing_docs', 'zoning_docs', 'fsi_docs']
for exp in expected:
    found = any(c.name == exp for c in collections)
    print(f"{exp}: {'✅ Found' if found else '❌ Missing'}")