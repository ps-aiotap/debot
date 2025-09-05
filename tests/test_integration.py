import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAuthIntegration:
    """Integration tests for auth endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client with mocked dependencies"""
        with patch('api.main.chatbot_app'), \
             patch('api.main.persona_manager'), \
             patch('database.get_db'):
            
            from api.main import app
            return TestClient(app)
    
    def test_health_endpoint_public(self, client):
        """Test that health endpoint is publicly accessible"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_chat_endpoint_requires_auth(self, client):
        """Test that chat endpoint requires authentication"""
        response = client.post("/chat", json={"message": "test"})
        assert response.status_code == 403  # No auth header
    
    def test_personas_endpoint_requires_auth(self, client):
        """Test that personas endpoint requires authentication"""
        response = client.get("/personas")
        assert response.status_code == 403  # No auth header
    
    @patch('auth.dependencies.jwt_handler')
    @patch('auth.dependencies.UserService')
    def test_chat_endpoint_with_valid_auth(self, mock_user_service, mock_jwt_handler, client):
        """Test chat endpoint with valid authentication"""
        # Mock JWT verification
        mock_jwt_handler.verify_token.return_value = {
            "sub": "clerk123",
            "email": "test@example.com"
        }
        
        # Mock user service
        mock_user = Mock()
        mock_user.clerk_user_id = "clerk123"
        mock_user.email = "test@example.com"
        mock_user_service.return_value.get_or_create_user.return_value = mock_user
        
        # Mock chatbot response
        with patch('api.main.chatbot_app') as mock_chatbot:
            mock_chatbot.ask_question.return_value = {
                "answer": "Test response",
                "sources": []
            }
            
            response = client.post(
                "/chat",
                json={"message": "test"},
                headers={"Authorization": "Bearer valid.jwt.token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["answer"] == "Test response"
            assert data["sources"] == []
    
    @patch('auth.dependencies.jwt_handler')
    def test_auth_me_endpoint(self, mock_jwt_handler, client):
        """Test /auth/me endpoint"""
        # Mock JWT verification
        mock_jwt_handler.verify_token.return_value = {
            "sub": "clerk123",
            "email": "test@example.com"
        }
        
        # Mock user
        with patch('auth.dependencies.UserService') as mock_user_service:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.clerk_user_id = "clerk123"
            mock_user.email = "test@example.com"
            mock_user.display_name = "Test User"
            mock_user.created_at.isoformat.return_value = "2024-01-01T00:00:00"
            mock_user_service.return_value.get_or_create_user.return_value = mock_user
            
            response = client.get(
                "/auth/me",
                headers={"Authorization": "Bearer valid.jwt.token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["clerk_user_id"] == "clerk123"
            assert data["email"] == "test@example.com"