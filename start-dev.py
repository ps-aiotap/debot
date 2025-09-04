#!/usr/bin/env python3
"""Development startup script for DeBot with React frontend."""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Run a command and return the process."""
    print(f"Running: {cmd}")
    return subprocess.Popen(cmd, shell=shell, cwd=cwd)

def main():
    """Start both backend and frontend in development mode."""
    from dotenv import load_dotenv
    load_dotenv()
    
    root_dir = Path(__file__).parent
    api_dir = root_dir / "api"
    frontend_dir = root_dir / "frontend"
    
    # Load frontend .env as well
    frontend_env_path = frontend_dir / ".env"
    if frontend_env_path.exists():
        load_dotenv(frontend_env_path)
    
    # Get ports from environment
    api_port = os.getenv('API_PORT', '8000')
    frontend_port = os.getenv('FRONTEND_PORT', '5173')
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("🚀 Starting FastAPI backend...")
        api_process = run_command(
            f"python -m uvicorn main:app --reload --host 0.0.0.0 --port {api_port}",
            cwd=api_dir
        )
        processes.append(api_process)
        
        # Wait and show progress
        print("⏳ Waiting for backend to initialize...")
        for i in range(3):
            time.sleep(1)
            print(f"   {'.' * (i + 1)}")
        
        # Start React frontend with strict port
        print("🌐 Starting React frontend...")
        frontend_env = os.environ.copy()
        frontend_env['FRONTEND_PORT'] = frontend_port
        try:
            frontend_process = subprocess.Popen(
                "npm run dev", 
                shell=True, 
                cwd=frontend_dir,
                env=frontend_env,
                stderr=subprocess.PIPE
            )
            processes.append(frontend_process)
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            print(f"💡 Port {frontend_port} might be in use. Try: netstat -ano | findstr :{frontend_port}")
            raise
        
        print("⏳ Initializing frontend...")
        time.sleep(2)
        
        print("\n" + "="*50)
        print("🚀 DeBot Development Environment Started!")
        print("="*50)
        print(f"📡 Backend API: http://localhost:{api_port}")
        print(f"🌐 Frontend: http://localhost:{frontend_port}")
        print(f"📚 API Docs: http://localhost:{api_port}/docs")
        print("\nPress Ctrl+C to stop all services")
        print("="*50)
        
        # Wait for processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n\nShutting down services...")
        for process in processes:
            process.terminate()
        
        # Wait for graceful shutdown
        time.sleep(2)
        
        # Force kill if needed
        for process in processes:
            if process.poll() is None:
                process.kill()
        
        print("All services stopped.")

if __name__ == "__main__":
    main()