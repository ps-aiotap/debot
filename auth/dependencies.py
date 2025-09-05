from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from .jwt_handler import jwt_handler
from .models import User
from .user_service import UserService

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """FastAPI dependency to get current authenticated user"""
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    # Verify JWT token
    payload = jwt_handler.verify_token(credentials.credentials)
    
    # Extract user info from token
    clerk_user_id = payload.get("sub")
    # Try multiple possible email fields
    email = (
        payload.get("email") or 
        payload.get("email_address") or
        payload.get("primary_email_address_id")
    )
    
    # Debug: log available fields (remove in production)
    print(f"Token payload keys: {list(payload.keys())}")
    
    if not clerk_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: missing user ID. Available fields: {list(payload.keys())}"
        )
    
    # Email might not be available in all token types
    if not email:
        email = f"user_{clerk_user_id}@clerk.local"  # Fallback email
    
    # Return minimal user object (DB integration handled in API layer)
    class AuthenticatedUser:
        def __init__(self, clerk_user_id: str, email: str, display_name: str = None):
            self.clerk_user_id = clerk_user_id
            self.email = email
            self.display_name = display_name
    
    return AuthenticatedUser(
        clerk_user_id=clerk_user_id,
        email=email,
        display_name=payload.get("name") or payload.get("given_name")
    )

def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Optional authentication - returns None if no valid token"""
    try:
        if credentials:
            return get_current_user(credentials)
    except HTTPException:
        pass
    return None