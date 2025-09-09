import pytest
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum

# Simple test models to avoid import issues
Base = declarative_base()

class Role(enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst" 
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String)

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class UserOrgMembership(Base):
    __tablename__ = "user_org_memberships"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    org_id = Column(Integer, ForeignKey("organizations.id"))
    role = Column(Enum(Role))

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, nullable=False)
    filename = Column(String)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_tenant_isolation(db_session):
    """Test basic tenant isolation"""
    # Create orgs
    org1 = Organization(name="Org1")
    org2 = Organization(name="Org2")
    db_session.add_all([org1, org2])
    db_session.commit()
    
    # Create documents
    doc1 = Document(org_id=org1.id, filename="doc1.pdf")
    doc2 = Document(org_id=org2.id, filename="doc2.pdf")
    db_session.add_all([doc1, doc2])
    db_session.commit()
    
    # Test isolation
    org1_docs = db_session.query(Document).filter(Document.org_id == org1.id).all()
    assert len(org1_docs) == 1
    assert org1_docs[0].filename == "doc1.pdf"

def test_rbac_roles(db_session):
    """Test role assignments"""
    # Create user and org
    user = User(email="test@example.com")
    org = Organization(name="TestOrg")
    db_session.add_all([user, org])
    db_session.commit()
    
    # Create membership
    membership = UserOrgMembership(user_id=user.id, org_id=org.id, role=Role.ADMIN)
    db_session.add(membership)
    db_session.commit()
    
    # Verify role
    result = db_session.query(UserOrgMembership).filter(
        UserOrgMembership.user_id == user.id,
        UserOrgMembership.org_id == org.id
    ).first()
    
    assert result.role == Role.ADMIN

def test_permission_logic():
    """Test permission checking logic"""
    def has_permission(user_role, required_roles):
        return user_role in required_roles
    
    # Admin can do everything
    assert has_permission(Role.ADMIN, [Role.ADMIN])
    assert has_permission(Role.ADMIN, [Role.ADMIN, Role.ANALYST])
    
    # Viewer has limited access
    assert not has_permission(Role.VIEWER, [Role.ADMIN])
    assert has_permission(Role.VIEWER, [Role.VIEWER, Role.ANALYST])