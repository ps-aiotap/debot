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
    
    print("✅ Services started successfully!")
    print("🌐 ChromaDB: http://localhost:8008")
    print("🔴 Redis: localhost:6379")
    print("\nRun 'streamlit run streamlit_app.py' to start the web interface")

if __name__ == "__main__":
    start_services()