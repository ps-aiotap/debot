from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Document, ChatHistory
from auth.rbac_dependencies import require_org_member, require_roles, UserContext
from auth.rbac_models import Role
from auth.rbac_service import RBACService
from typing import List

router = APIRouter(prefix="/api/v1", tags=["rbac"])

@router.get("/documents")
async def get_documents(
    context: UserContext = Depends(require_roles([Role.ADMIN, Role.ANALYST, Role.VIEWER])),
    db: Session = Depends(get_db)
):
    """Get documents with tenant isolation - all roles can view"""
    documents = RBACService.filter_by_org(
        db.query(Document), context.org_id
    ).all()
    return documents

@router.post("/documents")
async def create_document(
    document_data: dict,
    context: UserContext = Depends(require_roles([Role.ADMIN, Role.ANALYST])),
    db: Session = Depends(get_db)
):
    """Create document - admin and analyst only"""
    document = Document(**document_data, org_id=context.org_id)
    db.add(document)
    db.commit()
    return document

@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: int,
    context: UserContext = Depends(require_roles([Role.ADMIN])),
    db: Session = Depends(get_db)
):
    """Delete document - admin only"""
    document = RBACService.filter_by_org(
        db.query(Document), context.org_id
    ).filter(Document.id == doc_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    return {"message": "Document deleted"}

@router.get("/chat-history")
async def get_chat_history(
    context: UserContext = Depends(require_roles([Role.ADMIN, Role.ANALYST, Role.VIEWER])),
    db: Session = Depends(get_db)
):
    """Get chat history with tenant isolation and ownership check (ABAC)"""
    query = RBACService.filter_by_org(db.query(ChatHistory), context.org_id)
    
    # ABAC: Viewers can only see their own chat history
    if context.role == Role.VIEWER:
        query = query.filter(ChatHistory.user_id == context.user.id)
    
    return query.all()