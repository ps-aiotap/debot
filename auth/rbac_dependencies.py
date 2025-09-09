from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from auth.models import User
from auth.rbac_models import UserOrgMembership, Role, Organization
import jwt
import os

class UserContext:
    def __init__(self, user: User, org_id: int, role: Role):
        self.user = user
        self.org_id = org_id
        self.role = role

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extract user from Clerk JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        # Decode Clerk JWT (simplified - in production use proper Clerk verification)
        payload = jwt.decode(token, os.getenv("CLERK_SECRET_KEY"), algorithms=["HS256"])
        clerk_user_id = payload.get("sub")
        
        user = db.query(User).filter(User.clerk_user_id == clerk_user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_org_member(org_id: int = None):
    """Dependency to ensure user is member of organization"""
    async def _require_org_member(
        user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> UserContext:
        membership = db.query(UserOrgMembership).filter(
            UserOrgMembership.user_id == user.id,
            UserOrgMembership.org_id == org_id
        ).first()
        
        if not membership:
            raise HTTPException(status_code=403, detail="Access denied: not a member of this organization")
        
        return UserContext(user=user, org_id=org_id, role=membership.role)
    
    return _require_org_member

def require_roles(allowed_roles: List[Role]):
    """Dependency to enforce role-based access control"""
    def _require_roles(context: UserContext = Depends(require_org_member())):
        if context.role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Access denied: requires one of {[r.value for r in allowed_roles]}"
            )
        return context
    
    return _require_roles

def require_resource_access(resource_org_id: int):
    """ABAC: Check if user can access resource based on ownership/org membership"""
    def _require_resource_access(context: UserContext = Depends(require_org_member())):
        if context.org_id != resource_org_id:
            raise HTTPException(status_code=403, detail="Access denied: resource belongs to different organization")
        return context
    
    return _require_resource_access