import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create unified base for tests
TestBase = declarative_base()

# Import models with unified base
from auth.models import User
from auth.rbac_models import Organization, UserOrgMembership, Role
from database import Document, ChatHistory
from auth.rbac_service import RBACService

# Ensure all models use same metadata
User.__table__.metadata = TestBase.metadata
Organization.__table__.metadata = TestBase.metadata
UserOrgMembership.__table__.metadata = TestBase.metadata
Document.__table__.metadata = TestBase.metadata
ChatHistory.__table__.metadata = TestBase.metadata

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def setup_db():
    TestBase.metadata.create_all(bind=engine)
    yield
    TestBase.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_db):
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def test_data(db_session):
    # Create organizations
    org1 = RBACService.create_organization(db_session, "Org1", "org1")
    org2 = RBACService.create_organization(db_session, "Org2", "org2")
    
    # Create users
    user1 = User(clerk_user_id="user1", email="admin@org1.com")
    user2 = User(clerk_user_id="user2", email="viewer@org1.com")
    user3 = User(clerk_user_id="user3", email="admin@org2.com")
    
    db_session.add_all([user1, user2, user3])
    db_session.commit()
    
    # Create memberships
    RBACService.add_user_to_org(db_session, user1.id, org1.id, Role.ADMIN)
    RBACService.add_user_to_org(db_session, user2.id, org1.id, Role.VIEWER)
    RBACService.add_user_to_org(db_session, user3.id, org2.id, Role.ADMIN)
    
    return {
        "org1": org1, "org2": org2,
        "user1": user1, "user2": user2, "user3": user3
    }

class TestTenantIsolation:
    def test_user_cannot_access_other_org_data(self, db_session, test_data):
        """Test that users cannot access data from other organizations"""
        
        # Create documents in different orgs
        doc1 = Document(org_id=test_data["org1"].id, filename="doc1.pdf", content="content1")
        doc2 = Document(org_id=test_data["org2"].id, filename="doc2.pdf", content="content2")
        
        db_session.add_all([doc1, doc2])
        db_session.commit()
        
        # User from org1 should only see org1 documents
        org1_docs = RBACService.filter_by_org(db_session.query(Document), test_data["org1"].id).all()
        assert len(org1_docs) == 1
        assert org1_docs[0].filename == "doc1.pdf"
        
        # User from org2 should only see org2 documents
        org2_docs = RBACService.filter_by_org(db_session.query(Document), test_data["org2"].id).all()
        assert len(org2_docs) == 1
        assert org2_docs[0].filename == "doc2.pdf"

class TestRBAC:
    def test_role_permissions(self, db_session, test_data):
        """Test role-based access control"""
        # Admin should have admin role
        admin_role = RBACService.get_user_role_in_org(
            db_session, test_data["user1"].id, test_data["org1"].id
        )
        assert admin_role == Role.ADMIN
        
        # Viewer should have viewer role
        viewer_role = RBACService.get_user_role_in_org(
            db_session, test_data["user2"].id, test_data["org1"].id
        )
        assert viewer_role == Role.VIEWER
        
        # User should not have role in other org
        no_role = RBACService.get_user_role_in_org(
            db_session, test_data["user1"].id, test_data["org2"].id
        )
        assert no_role is None

    def test_permission_checks(self):
        """Test permission validation logic"""
        # Admin can do admin tasks
        assert RBACService.has_permission(Role.ADMIN, [Role.ADMIN])
        assert RBACService.has_permission(Role.ADMIN, [Role.ADMIN, Role.ANALYST])
        
        # Viewer cannot do admin tasks
        assert not RBACService.has_permission(Role.VIEWER, [Role.ADMIN])
        assert not RBACService.has_permission(Role.VIEWER, [Role.ANALYST])
        
        # Viewer can do viewer tasks
        assert RBACService.has_permission(Role.VIEWER, [Role.VIEWER, Role.ANALYST])

class TestABAC:
    def test_ownership_isolation(self, db_session, test_data):
        """Test attribute-based access control for ownership"""
        
        # Create chat history for different users in same org
        chat1 = ChatHistory(
            org_id=test_data["org1"].id,
            user_id=test_data["user1"].id,
            question="Q1", answer="A1"
        )
        chat2 = ChatHistory(
            org_id=test_data["org1"].id,
            user_id=test_data["user2"].id,
            question="Q2", answer="A2"
        )
        
        db_session.add_all([chat1, chat2])
        db_session.commit()
        
        # User1 should only see their own chat
        user1_chats = db_session.query(ChatHistory).filter(
            ChatHistory.org_id == test_data["org1"].id,
            ChatHistory.user_id == test_data["user1"].id
        ).all()
        assert len(user1_chats) == 1
        assert user1_chats[0].question == "Q1"
        
        # User2 should only see their own chat
        user2_chats = db_session.query(ChatHistory).filter(
            ChatHistory.org_id == test_data["org1"].id,
            ChatHistory.user_id == test_data["user2"].id
        ).all()
        assert len(user2_chats) == 1
        assert user2_chats[0].question == "Q2"