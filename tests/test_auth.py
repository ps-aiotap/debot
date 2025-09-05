import pytest
import jwt
from unittest.mock import Mock, patch
from fastapi import HTTPException
from auth.jwt_handler import ClerkJWTHandler
from auth.dependencies import get_current_user
from auth.user_service import UserService
from auth.models import User
from datetime import datetime, timezone, timedelta

class TestClerkJWTHandler:
    """Test JWT verification logic"""
    
    def setup_method(self):
        self.handler = ClerkJWTHandler("test_secret")
    
    @patch('auth.jwt_handler.requests.get')
    def test_get_jwks_success(self, mock_get):
        """Test successful JWKS retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {"keys": [{"kid": "test", "kty": "RSA"}]}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Clear cache
        self.handler._get_jwks.cache_clear()
        
        result = self.handler._get_jwks()
        assert result == {"keys": [{"kid": "test", "kty": "RSA"}]}
    
    @patch('auth.jwt_handler.requests.get')
    def test_get_jwks_failure(self, mock_get):
        """Test JWKS retrieval failure"""
        mock_get.side_effect = Exception("Network error")
        
        # Clear cache
        self.handler._get_jwks.cache_clear()
        
        with pytest.raises(HTTPException) as exc_info:
            self.handler._get_jwks()
        
        assert exc_info.value.status_code == 503
        assert "Failed to fetch JWKS" in str(exc_info.value.detail)
    
    def test_verify_token_missing_kid(self):
        """Test token verification with missing kid"""
        # Create token without kid in header
        token = jwt.encode({"sub": "user123"}, "secret", algorithm="HS256")
        
        with pytest.raises(HTTPException) as exc_info:
            self.handler.verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "missing kid" in str(exc_info.value.detail)
    
    def test_verify_token_expired(self):
        """Test expired token verification"""
        # Create expired token
        payload = {
            "sub": "user123",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1)
        }
        token = jwt.encode(payload, "secret", algorithm="HS256", headers={"kid": "test"})
        
        with pytest.raises(HTTPException) as exc_info:
            self.handler.verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in str(exc_info.value.detail).lower()
    
    def test_verify_token_invalid(self):
        """Test invalid token verification"""
        with pytest.raises(HTTPException) as exc_info:
            self.handler.verify_token("invalid.token.here")
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

class TestUserService:
    """Test user service operations"""
    
    def setup_method(self):
        self.mock_db = Mock()
        self.service = UserService(self.mock_db)
    
    def test_get_user_by_clerk_id(self):
        """Test getting user by Clerk ID"""
        mock_user = User(clerk_user_id="clerk123", email="test@example.com")
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.service.get_user_by_clerk_id("clerk123")
        
        assert result == mock_user
        self.mock_db.query.assert_called_once_with(User)
    
    def test_create_user(self):
        """Test user creation"""
        self.service.create_user("clerk123", "test@example.com", "Test User")
        
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once()
    
    def test_get_or_create_user_existing(self):
        """Test get_or_create with existing user"""
        mock_user = User(clerk_user_id="clerk123", email="test@example.com")
        self.mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        result = self.service.get_or_create_user("clerk123", "test@example.com")
        
        assert result == mock_user
        # Should not create new user
        self.mock_db.add.assert_not_called()
    
    def test_get_or_create_user_new(self):
        """Test get_or_create with new user"""
        # No existing user
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        result = self.service.get_or_create_user("clerk123", "test@example.com")
        
        # Should create new user
        self.mock_db.add.assert_called_once()
        self.mock_db.commit.assert_called_once()

class TestAuthDependencies:
    """Test FastAPI auth dependencies"""
    
    @patch('auth.dependencies.jwt_handler')
    def test_get_current_user_success(self, mock_jwt_handler):
        """Test successful user authentication"""
        # Mock JWT verification
        mock_jwt_handler.verify_token.return_value = {
            "sub": "clerk123",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        # Mock credentials
        mock_credentials = Mock()
        mock_credentials.credentials = "valid.jwt.token"
        
        # Mock database and user service
        mock_db = Mock()
        mock_user = User(clerk_user_id="clerk123", email="test@example.com")
        
        with patch('auth.dependencies.UserService') as mock_user_service:
            mock_user_service.return_value.get_or_create_user.return_value = mock_user
            
            result = get_current_user(mock_credentials, mock_db)
            
            assert result == mock_user
            mock_jwt_handler.verify_token.assert_called_once_with("valid.jwt.token")
    
    def test_get_current_user_no_credentials(self):
        """Test authentication without credentials"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None, None)
        
        assert exc_info.value.status_code == 401
        assert "Missing authorization header" in str(exc_info.value.detail)
    
    @patch('auth.dependencies.jwt_handler')
    def test_get_current_user_invalid_token_payload(self, mock_jwt_handler):
        """Test authentication with invalid token payload"""
        # Mock JWT verification with missing required fields
        mock_jwt_handler.verify_token.return_value = {"invalid": "payload"}
        
        mock_credentials = Mock()
        mock_credentials.credentials = "invalid.payload.token"
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials, None)
        
        assert exc_info.value.status_code == 401
        assert "missing user information" in str(exc_info.value.detail)

# Integration test fixtures
@pytest.fixture
def mock_db_session():
    """Mock database session for testing"""
    return Mock()

@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return User(
        id=1,
        clerk_user_id="clerk_test_123",
        email="test@example.com",
        display_name="Test User",
        created_at=datetime.utcnow()
    )