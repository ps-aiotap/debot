from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import os
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simple_main import SimpleChatbotApp
from persona_manager import PersonaManager
from auth.dependencies import get_current_user, get_optional_user
from auth.models import User
from database import get_db
from datetime import datetime
from sqlalchemy.orm import Session

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
# Get project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
persona_config_path = os.path.join(project_root, "persona_config.json")
persona_manager = PersonaManager(config_path=persona_config_path)

class ChatRequest(BaseModel):
    message: str
    persona: Optional[str] = None
    explain: bool = False

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    explanation: Optional[Dict[str, Any]] = None

class UserResponse(BaseModel):
    id: int
    clerk_user_id: str
    email: str
    display_name: Optional[str]
    created_at: str

@app.on_event("startup")
async def startup_event():
    global chatbot_app
    try:
        config_path = os.path.join(project_root, "config.yaml")
        chatbot_app = SimpleChatbotApp(config_path=config_path, persona_manager=persona_manager)
        await chatbot_app.initialize()
        print("✅ Chatbot initialized successfully")
    except Exception as e:
        print(f"⚠️ Chatbot initialization failed: {e}")
        chatbot_app = None



@app.get("/personas")
async def get_personas(
    current_user = Depends(get_current_user)
):
    """Get available personas for authenticated user"""
    return {
        "available": persona_manager.get_available_personas(),
        "current": persona_manager.get_current_persona(),
        "collections": persona_manager.get_collections(),
        "prompt_style": persona_manager.get_prompt_style()
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    if db:
        from auth.user_service import UserService
        user_service = UserService(db)
        db_user = user_service.get_or_create_user(
            clerk_user_id=current_user.clerk_user_id,
            email=current_user.email,
            display_name=current_user.display_name
        )
        return UserResponse(
            id=db_user.id,
            clerk_user_id=db_user.clerk_user_id,
            email=db_user.email,
            display_name=db_user.display_name,
            created_at=db_user.created_at.isoformat()
        )
    else:
        # Fallback when DB not available
        return UserResponse(
            id=0,
            clerk_user_id=current_user.clerk_user_id,
            email=current_user.email,
            display_name=current_user.display_name,
            created_at=datetime.now().isoformat()
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Protected chat endpoint requiring authentication"""
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)