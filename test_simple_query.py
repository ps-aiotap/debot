#!/usr/bin/env python3

import asyncio
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

async def test_simple():
    persona_manager = PersonaManager()
    persona_manager.set_persona("real_estate")
    
    app = SimpleChatbotApp(persona_manager=persona_manager)
    
    # Skip data ingestion, use existing collections
    print(f"Active persona: {app.get_current_persona()}")
    print(f"Active collections: {app.persona_manager.get_collections()}")
    
    # Test simple query
    query = "What is FSI?"
    print(f"\nTesting simple query: {query}")
    
    try:
        response = await app.ask_question(query)
        print(f"Success: {response['answer'][:100]}...")
        print(f"Sources: {len(response.get('sources', []))}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple())