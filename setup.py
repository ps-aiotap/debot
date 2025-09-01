import os
import asyncio
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

async def setup_chatbot():
    """Setup script to initialize the chatbot with data ingestion."""
    print("AI Domain Expert Chatbot Setup")
    print("=" * 40)
    
    # Check environment variables
    required_env_vars = ['OPENAI_API_KEY']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        return False
    
    # Initialize persona manager and chatbot
    persona_manager = PersonaManager()
    app = SimpleChatbotApp(persona_manager=persona_manager)
    
    print("Starting data ingestion and indexing...")
    os.environ["FORCE_REINDEX"] = "true"
    success = await app.initialize()
    
    if success:
        print("Setup completed successfully!")
        print("You can now run the Streamlit app with: streamlit run streamlit_app.py")
        return True
    else:
        print("Setup failed. Please check your configuration and data sources.")
        return False

if __name__ == "__main__":
    asyncio.run(setup_chatbot())