from sqlalchemy.orm import Session
from sqlalchemy import and_
from auth.models import User
from auth.rbac_models import Organization, UserOrgMembership, Role
from typing import List, Optional

class RBACService:
    """Service for RBAC operations and tenant isolation"""
    
    @staticmethod
    def create_organization(db: Session, name: str, slug: str) -> Organization:
        org = Organization(name=name, slug=slug)
        db.add(org)
        db.commit()
        db.refresh(org)
        return org
    
    @staticmethod
    def add_user_to_org(db: Session, user_id: int, org_id: int, role: Role) -> UserOrgMembership:
        membership = UserOrgMembership(user_id=user_id, org_id=org_id, role=role)
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership
    
    @staticmethod
    def get_user_orgs(db: Session, user_id: int) -> List[Organization]:
        return db.query(Organization).join(UserOrgMembership).filter(
            UserOrgMembership.user_id == user_id
        ).all()
    
    @staticmethod
    def get_user_role_in_org(db: Session, user_id: int, org_id: int) -> Optional[Role]:
        membership = db.query(UserOrgMembership).filter(
            and_(UserOrgMembership.user_id == user_id, UserOrgMembership.org_id == org_id)
        ).first()
        return membership.role if membership else None
    
    @staticmethod
    def filter_by_org(query, org_id: int):
        """Apply tenant isolation filter to any query"""
        return query.filter_by(org_id=org_id)
    
    @staticmethod
    def has_permission(role: Role, required_roles: List[Role]) -> bool:
        """Check if role has required permissions"""
        return role in required_roles