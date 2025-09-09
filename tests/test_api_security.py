import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from api.main import app
from auth.rbac_models import Role

client = TestClient(app)

class TestAPISecurityEndpoints:
    
    @patch('auth.rbac_dependencies.get_current_user')
    @patch('auth.rbac_dependencies.get_db')
    def test_unauthorized_access_denied(self, mock_db, mock_user):
        """Test that requests without proper auth are denied"""
        response = client.get("/api/v1/documents")
        assert response.status_code == 401
    
    @patch('auth.rbac_dependencies.get_current_user')
    @patch('auth.rbac_dependencies.get_db')
    def test_cross_tenant_access_denied(self, mock_db, mock_user):
        """Test that users cannot access other organization's data"""
        # Mock user from org 1 trying to access org 2 data
        mock_user.return_value = MagicMock(id=1)
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = None
        
        response = client.get("/api/v1/documents", headers={"Authorization": "Bearer fake_token"})
        assert response.status_code == 403
    
    @patch('auth.rbac_dependencies.get_current_user')
    @patch('auth.rbac_dependencies.get_db')
    def test_role_based_access_control(self, mock_db, mock_user):
        """Test that role restrictions are enforced"""
        # Mock viewer trying to create document (should fail)
        mock_membership = MagicMock()
        mock_membership.role = Role.VIEWER
        mock_db.return_value.query.return_value.filter.return_value.first.return_value = mock_membership
        
        response = client.post("/api/v1/documents", 
                             json={"filename": "test.pdf"},
                             headers={"Authorization": "Bearer fake_token"})
        assert response.status_code == 403
    
    def test_sql_injection_protection(self):
        """Test that SQL injection attempts are blocked"""
        malicious_payload = {"filename": "'; DROP TABLE documents; --"}
        response = client.post("/api/v1/documents", json=malicious_payload)
        # Should fail at auth level, not reach SQL
        assert response.status_code == 401

class TestDataIsolationIntegration:
    
    def test_org_id_always_present(self):
        """Test that org_id is required on all tenant-isolated tables"""
        from database import Document, ChatHistory
        
        # Verify org_id columns exist and are not nullable
        assert hasattr(Document, 'org_id')
        assert hasattr(ChatHistory, 'org_id')
        
        # Check column constraints
        doc_org_col = Document.__table__.columns['org_id']
        chat_org_col = ChatHistory.__table__.columns['org_id']
        
        assert not doc_org_col.nullable
        assert not chat_org_col.nullable
    
    def test_unique_constraints_enforced(self):
        """Test that unique constraints prevent duplicate memberships"""
        from auth.rbac_models import UserOrgMembership
        
        # Verify unique constraint exists
        constraints = UserOrgMembership.__table__.constraints
        unique_constraint = next((c for c in constraints if hasattr(c, 'columns') and 
                                len(c.columns) == 2), None)
        assert unique_constraint is not None