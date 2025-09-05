# Authentication Setup Guide

## Overview

This implementation provides production-grade authentication using Clerk with JWT verification for the DeBot application.

## Architecture

### Frontend (React + Clerk)
- **ClerkProvider**: Wraps the entire app for auth context
- **AuthWrapper**: Handles sign-in/sign-out redirects
- **Dashboard**: Protected component requiring authentication
- **UserButton**: Provides user menu and sign-out functionality

### Backend (FastAPI + JWT)
- **JWT Handler**: Verifies Clerk RS256 JWT tokens using JWKS
- **Auth Dependencies**: FastAPI dependencies for protected routes
- **User Service**: Database operations for user management
- **User Model**: SQLAlchemy model for user persistence

## Setup Instructions

### 1. Clerk Configuration

1. Create a Clerk account at https://clerk.com
2. Create a new application
3. Get your keys from the Clerk dashboard:
   - **Publishable Key** (`pk_test_...`): Public key used by frontend, safe to expose
   - **Secret Key** (`sk_test_...`): Private key used by backend, keep secure

### 2. Environment Variables

**Backend (.env):**
```bash
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key_here
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=debot_user
POSTGRES_PASSWORD=debot_password
POSTGRES_DB=debot_db
```

**Frontend (.env):**
```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key_here
VITE_API_URL=http://localhost:8000
```

### 3. Database Setup

The system automatically creates the users table on startup. Ensure PostgreSQL is running:

```bash
# Start PostgreSQL (example for Docker)
docker run --name postgres -e POSTGRES_PASSWORD=debot_password -p 5432:5432 -d postgres
```

### 4. Install Dependencies

**Backend:**
```bash
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**⚠️ Important**: After installing new dependencies, restart any running application instances.

### 5. Run the Application

```bash
# Start backend (from project root)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (in another terminal)
cd frontend
npm run dev
```

## Authentication Flow

### 1. User Access
1. User visits the application
2. `AuthWrapper` checks authentication status
3. If not authenticated, redirects to Clerk sign-in

### 2. Sign-In Process
1. User signs in through Clerk
2. Clerk issues JWT token
3. Frontend stores token in memory
4. User is redirected to dashboard

### 3. API Requests
1. Frontend includes JWT in Authorization header
2. Backend `get_current_user` dependency verifies token
3. JWT is validated using Clerk's JWKS endpoint
4. User info is extracted and user is created/updated in database
5. Request proceeds with authenticated user context

### 4. Token Verification (RS256)
1. Extract `kid` from JWT header
2. Fetch JWKS from Clerk's endpoint (cached)
3. Find matching signing key
4. Verify signature using RS256 algorithm
5. Validate expiration and claims

## Security Features

### JWT Security
- **RS256 Algorithm**: Asymmetric encryption prevents token forgery
- **JWKS Validation**: Keys fetched from Clerk's secure endpoint
- **Expiration Checking**: Tokens automatically expire
- **Signature Verification**: Ensures token integrity

### Database Security
- **User Isolation**: Each user has separate database records
- **No Password Storage**: Authentication handled by Clerk
- **Minimal Data**: Only essential user info stored locally

### API Security
- **Protected Endpoints**: All sensitive routes require authentication
- **CORS Configuration**: Restricts cross-origin requests
- **Input Validation**: Pydantic models validate request data

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=auth tests/

# Run specific test file
pytest tests/test_auth.py -v
```

## Troubleshooting

### Common Issues

1. **"Missing Clerk Publishable Key"**
   - Ensure `VITE_CLERK_PUBLISHABLE_KEY` is set in frontend/.env

2. **"Failed to fetch JWKS" or "401 Unauthorized"**
   - Check internet connection
   - Verify Clerk secret key is correct and complete
   - Ensure you're using the correct Clerk instance keys
   - Try clearing browser cache and re-authenticating

3. **"Invalid token: signing key not found"**
   - Token may be from different Clerk instance
   - Clear browser cache and re-authenticate

4. **Database connection errors**
   - Ensure PostgreSQL is running
   - Check database credentials in .env

5. **"config.yaml not found" or "persona_config.json not found"**
   - Ensure you're running from the project root directory
   - Run: `uvicorn api.main:app --reload` from the debot/ folder
   - Check that config.yaml and persona_config.json exist in project root

6. **"Invalid token: missing user information"**
   - Check backend logs for "Token payload keys" to see available fields
   - Ensure user has completed Clerk sign-up process
   - Try signing out and signing back in
   - Verify Clerk application settings allow required user data

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Production Considerations

### Security
- Use HTTPS in production
- Set secure CORS origins
- Enable rate limiting
- Monitor authentication failures

### Performance
- JWKS responses are cached
- Database connections pooled
- Consider Redis for session storage

### Monitoring
- Log authentication events
- Monitor token verification failures
- Track user creation/login patterns

## Migration & Scalability

### Multi-Tenant Ready
The architecture supports multi-tenancy:
- Add tenant_id to User model
- Filter queries by tenant
- Isolate data per organization

### Horizontal Scaling
- Stateless JWT verification
- Database connection pooling
- Redis for distributed caching
- Load balancer compatible

## API Endpoints

### Public Endpoints
- `GET /` - API info
- `GET /health` - Health check

### Protected Endpoints
- `GET /auth/me` - Current user info
- `POST /chat` - Chat with AI (requires auth)
- `GET /personas` - Available personas (requires auth)

### Authentication Headers
```bash
Authorization: Bearer <jwt_token>
```

## Code Structure

```
auth/
├── __init__.py
├── models.py          # SQLAlchemy User model
├── jwt_handler.py     # JWT verification logic
├── dependencies.py    # FastAPI auth dependencies
└── user_service.py    # Database operations

tests/
├── test_auth.py       # Unit tests
└── test_integration.py # Integration tests
```