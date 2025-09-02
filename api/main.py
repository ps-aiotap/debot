from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.append('..')
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager

load_dotenv(override=True)

app = FastAPI(title="DeBot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot_app = None
persona_manager = PersonaManager()

class ChatRequest(BaseModel):
    message: str
    persona: Optional[str] = None
    explain: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    explanation: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    global chatbot_app
    chatbot_app = SimpleChatbotApp(persona_manager=persona_manager)
    await chatbot_app.initialize()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/personas")
async def get_personas():
    return {
        "available": persona_manager.get_available_personas(),
        "current": persona_manager.get_current_persona(),
        "collections": persona_manager.get_collections(),
        "prompt_style": persona_manager.get_prompt_style()
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not chatbot_app:
        raise HTTPException(status_code=500, detail="Chatbot not initialized")
    
    if request.persona and request.persona != persona_manager.get_current_persona():
        if not persona_manager.set_persona(request.persona):
            raise HTTPException(status_code=400, detail=f"Invalid persona: {request.persona}")
        await chatbot_app.initialize()
    
    try:
        response = await chatbot_app.ask_question(
            request.message, 
            use_cache=False, 
            explain=request.explain
        )
        
        return ChatResponse(
            answer=response.get("answer", "No answer generated."),
            sources=response.get("sources", []),
            explanation=response.get("explanation")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))