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

# Get frontend port from environment
frontend_port = os.getenv('FRONTEND_PORT', '5173')
api_port = os.getenv('API_PORT', '8000')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{frontend_port}", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define routes first
@app.get("/")
def root():
    return {"message": "DeBot API", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

chatbot_app = None
persona_config_path = os.path.join("..", "persona_config.json")
persona_manager = PersonaManager(config_path=persona_config_path)

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
    try:
        config_path = os.path.join("..", "config.yaml")
        chatbot_app = SimpleChatbotApp(config_path=config_path, persona_manager=persona_manager)
        await chatbot_app.initialize()
        print("✅ Chatbot initialized successfully")
    except Exception as e:
        print(f"⚠️ Chatbot initialization failed: {e}")
        chatbot_app = None



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
            use_cache=False
        )
        
        return ChatResponse(
            answer=response.get("answer", "No answer generated."),
            sources=response.get("sources", []),
            explanation=response.get("explanation")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))