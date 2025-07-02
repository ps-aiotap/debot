import os
import asyncio
from main import ChatbotApp

async def setup_chatbot():
    """Setup script to initialize the chatbot with data ingestion."""
    print("🤖 AI Domain Expert Chatbot Setup")
    print("=" * 40)
    
    # Check environment variables
    required_env_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        return False
    
    # Initialize chatbot
    app = ChatbotApp()
    
    print("🔄 Starting data ingestion and indexing...")
    success = await app.initialize(force_reindex=True)
    
    if success:
        print("✅ Setup completed successfully!")
        print("You can now run the Streamlit app with: streamlit run streamlit_app.py")
        return True
    else:
        print("❌ Setup failed. Please check your configuration and data sources.")
        return False

if __name__ == "__main__":
    asyncio.run(setup_chatbot())