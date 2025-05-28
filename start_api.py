#!/usr/bin/env python3
"""
Simple startup script for the Technical Analysis FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path
import uvicorn

def main():
    """Start the FastAPI server"""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Add the src directory to Python path
    src_path = project_root / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Set environment variables
    os.environ.setdefault("PYTHONPATH", str(src_path))
    
    # Server configuration
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8001))
    reload = os.getenv("API_RELOAD", "true").lower() == "true"
    workers = int(os.getenv("API_WORKERS", 1))
    
    print("🚀 Starting Technical Analysis FastAPI Server")
    print("=" * 50)
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"📖 ReDoc: http://{host}:{port}/redoc")
    print(f"🔄 Auto-reload: {reload}")
    print("=" * 50)
    
    try:
        # Start the server
        uvicorn.run(
            "src.app.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1
        )
        
    except ImportError:
        print("❌ Error: uvicorn not installed")
        print("💡 Install with: pip install uvicorn[standard]")
        print("💡 Or install all API dependencies: pip install -e '.[api]'")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 