import jwt
import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from functools import lru_cache
import os
from datetime import datetime, timezone

class ClerkJWTHandler:
    """Handles Clerk JWT verification using RS256"""
    
    def __init__(self, clerk_secret_key: str):
        self.clerk_secret_key = clerk_secret_key
        # Extract instance from secret key to build JWKS URL
        # Clerk secret keys have format: sk_test_<instance_id>...
        if clerk_secret_key and len(clerk_secret_key) > 8:
            # For development/test instances
            self.jwks_url = "https://clerk.dev/.well-known/jwks.json"
        else:
            raise ValueError("Invalid Clerk secret key format")
        
    @lru_cache(maxsize=1)
    def _get_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Clerk with caching"""
        try:
            # No authentication needed for public JWKS endpoint
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to fetch JWKS from {self.jwks_url}: {str(e)}. Check your Clerk configuration."
            )
    
    def _get_signing_key(self, kid: str) -> str:
        """Get signing key from JWKS"""
        jwks = self._get_jwks()
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Convert JWK to PEM format
                from jwt.algorithms import RSAAlgorithm
                return RSAAlgorithm.from_jwk(key)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: signing key not found"
        )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Clerk JWT token and return payload"""
        try:
            # First decode without verification to get issuer
            unverified_payload = jwt.decode(token, options={"verify_signature": False})
            issuer = unverified_payload.get("iss")
            
            # Update JWKS URL based on issuer
            if issuer:
                self.jwks_url = f"{issuer}/.well-known/jwks.json"
                # Clear cache when URL changes
                self._get_jwks.cache_clear()
            
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing kid"
                )
            
            # Get signing key
            signing_key = self._get_signing_key(kid)
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=["RS256"],
                options={"verify_exp": True, "verify_aud": False}
            )
            
            # Validate token is not expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            # Debug: log payload structure (remove in production)
            print(f"JWT payload: {payload}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token verification failed: {str(e)}"
            )

# Global instance
jwt_handler = ClerkJWTHandler(os.getenv("CLERK_SECRET_KEY", ""))