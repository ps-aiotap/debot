#!/usr/bin/env python3

import asyncio
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

async def test_real_estate():
    persona_manager = PersonaManager()
    app = SimpleChatbotApp(persona_manager=persona_manager)
    await app.initialize()
    
    # Set persona to real_estate
    app.set_persona("real_estate")
    print(f"Active persona: {app.get_current_persona()}")
    print(f"Active collections: {app.persona_manager.get_collections()}")
    
    # Initialize without data ingestion to test existing collections
    print("\nSkipping data ingestion, testing existing collections...")
    
    # Test the problematic query
    query = "What is the FSI potential for residential projects in Kothrud, Pune?"
    print(f"\nTesting query: {query}")
    
    try:
        response = await app.ask_question(query)
        print(f"Success: {response['answer'][:200]}...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_estate())