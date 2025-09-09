import pytest
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base
from auth.rbac_models import Organization, UserOrgMembership, Role
from auth.models import User

class TestPerformance:
    
    @pytest.fixture
    def perf_db(self):
        """Setup performance test database with indexes"""
        engine = create_engine("sqlite:///./perf_test.db")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(bind=engine)
        
        # Create test data
        db = SessionLocal()
        
        # Create 100 orgs, 1000 users, 10000 documents
        orgs = [Organization(name=f"Org{i}", slug=f"org{i}") for i in range(100)]
        db.add_all(orgs)
        db.commit()
        
        users = [User(clerk_user_id=f"user{i}", email=f"user{i}@test.com") for i in range(1000)]
        db.add_all(users)
        db.commit()
        
        # Add memberships
        memberships = []
        for i, user in enumerate(users):
            org_id = (i % 100) + 1  # Distribute users across orgs
            role = [Role.ADMIN, Role.ANALYST, Role.VIEWER][i % 3]
            memberships.append(UserOrgMembership(user_id=user.id, org_id=org_id, role=role))
        
        db.add_all(memberships)
        db.commit()
        
        yield db
        db.close()
    
    def test_tenant_filter_performance(self, perf_db):
        """Test that org_id filtering is fast with proper indexes"""
        from database import Document
        
        # Add test documents
        docs = [Document(org_id=(i % 100) + 1, filename=f"doc{i}.pdf", content=f"content{i}") 
                for i in range(10000)]
        perf_db.add_all(docs)
        perf_db.commit()
        
        # Time tenant-filtered query
        start_time = time.time()
        
        # Query should use index on org_id
        result = perf_db.query(Document).filter(Document.org_id == 1).limit(100).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert len(result) > 0
        assert query_time < 0.1  # Should be fast with proper indexing
    
    def test_role_check_performance(self, perf_db):
        """Test that role lookups are efficient"""
        start_time = time.time()
        
        # Simulate 100 role checks
        for i in range(100):
            user_id = (i % 1000) + 1
            org_id = (i % 100) + 1
            
            membership = perf_db.query(UserOrgMembership).filter(
                UserOrgMembership.user_id == user_id,
                UserOrgMembership.org_id == org_id
            ).first()
            
            assert membership is not None
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 100 role checks should complete quickly
        assert total_time < 0.5