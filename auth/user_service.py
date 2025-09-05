from sqlalchemy.orm import Session
from .models import User
from typing import Optional

class UserService:
    """Service for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[User]:
        """Get user by Clerk user ID"""
        return self.db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
    
    def create_user(self, clerk_user_id: str, email: str, display_name: Optional[str] = None) -> User:
        """Create new user"""
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            display_name=display_name
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_or_create_user(self, clerk_user_id: str, email: str, display_name: Optional[str] = None) -> User:
        """Get existing user or create new one"""
        user = self.get_user_by_clerk_id(clerk_user_id)
        if not user:
            user = self.create_user(clerk_user_id, email, display_name)
        return user