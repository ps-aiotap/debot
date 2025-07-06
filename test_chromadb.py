import chromadb
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('CHROMA_HOST', 'localhost')
port = int(os.getenv('CHROMA_PORT', '8000'))

print(f"Testing ChromaDB connection to {host}:{port}")

try:
    client = chromadb.HttpClient(host=host, port=port)
    print("✅ ChromaDB client created")
    
    # Test heartbeat
    heartbeat = client.heartbeat()
    print(f"✅ Heartbeat: {heartbeat}")
    
    # Test collection creation
    collection = client.get_or_create_collection("test")
    print("✅ Collection created/retrieved")
    
    print("🎉 ChromaDB is working!")
    
except Exception as e:
    print(f"❌ ChromaDB test failed: {e}")
    print(f"Error type: {type(e)}")