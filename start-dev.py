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
    root_dir = Path(__file__).parent
    api_dir = root_dir / "api"
    frontend_dir = root_dir / "frontend"
    
    processes = []
    
    try:
        # Start FastAPI backend
        print("Starting FastAPI backend...")
        api_process = run_command(
            "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000",
            cwd=api_dir
        )
        processes.append(api_process)
        
        # Wait a bit for backend to start
        time.sleep(3)
        
        # Start React frontend
        print("Starting React frontend...")
        frontend_process = run_command("npm run dev", cwd=frontend_dir)
        processes.append(frontend_process)
        
        print("\n" + "="*50)
        print("🚀 DeBot Development Environment Started!")
        print("="*50)
        print("📡 Backend API: http://localhost:8000")
        print("🌐 Frontend: http://localhost:5173")
        print("📚 API Docs: http://localhost:8000/docs")
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