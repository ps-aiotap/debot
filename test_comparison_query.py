#!/usr/bin/env python3

import asyncio
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

async def test_comparison():
    persona_manager = PersonaManager()
    persona_manager.set_persona("real_estate")
    
    app = SimpleChatbotApp(persona_manager=persona_manager)
    
    print(f"Active persona: {app.get_current_persona()}")
    print(f"Active collections: {app.persona_manager.get_collections()}")
    
    # Test the exact failing query
    query = "Compare the development potential and zoning advantages between Kothrud, Pune and NCR region. Which offers better investment opportunities for residential projects?"
    print(f"\nTesting comparison query: {query}")
    
    try:
        response = await app.ask_question(query)
        print(f"Success: {response['answer'][:200]}...")
        print(f"Sources: {len(response.get('sources', []))}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_comparison())