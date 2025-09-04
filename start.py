import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()

def start_services():
    """Start Docker services and the application."""
    print("🚀 Starting AI Domain Expert Chatbot")
    print("=" * 40)
    
    # Start Docker services
    print("📦 Starting Docker services...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Check if services are running
    result = subprocess.run(["docker-compose", "ps"], capture_output=True, text=True)
    print("Docker services status:")
    print(result.stdout)
    
    # Get service URLs from environment
    chroma_port = os.getenv('CHROMA_PORT', '8000')
    redis_port = os.getenv('REDIS_PORT', '6379')
    
    print("✅ Services started successfully!")
    print(f"🌐 ChromaDB: http://localhost:{chroma_port}")
    print(f"🔴 Redis: localhost:{redis_port}")
    print("\nNext steps:")
    print("  • Modern UI: python start-dev.py")
    print("  • Legacy UI: streamlit run streamlit_app.py")
    print("  • CLI: python main.py")

if __name__ == "__main__":
    start_services()