# DeBot React Frontend Setup

## Quick Start

### 1. Install Dependencies

```bash
# Install Python API dependencies
pip install -r requirements-api.txt

# Install Node.js dependencies
cd frontend
npm install
```

### 2. Configure Clerk Authentication

1. Sign up at [Clerk.com](https://clerk.com)
2. Create a new application
3. Copy your publishable key
4. Create `frontend/.env`:

```bash
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_key_here
```

### 3. Start Development Environment

```bash
# From project root
python start-dev.py
```

This will start:
- FastAPI backend on http://localhost:8000
- React frontend on http://localhost:5173

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Features

✅ **User Authentication** - Clerk integration with sign-in/sign-out
✅ **Modern UI** - Clean, responsive design with Tailwind CSS
✅ **Real-time Chat** - Interactive chat interface
✅ **Persona Management** - Switch between different AI personas
✅ **Source Attribution** - View document sources for answers
✅ **Explainability** - Understand why documents were selected
✅ **Error Handling** - Graceful error display and recovery

## Architecture

```
frontend/
├── src/
│   ├── components/
│   │   └── ChatInterface.jsx    # Main chat component
│   ├── App.jsx                  # Main app with auth
│   ├── main.jsx                 # Entry point with Clerk
│   └── index.css                # Tailwind styles
├── package.json
└── vite.config.js

api/
└── main.py                      # FastAPI backend
```

## Manual Setup (Alternative)

### Backend
```bash
cd api
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```