#!/usr/bin/env python3
"""
Script to run the Streamlit app for Custom Strategy Builder & Tester
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app"""
    
    # Change to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    print("🚀 Starting Custom Strategy Builder & Tester...")
    print("📍 Make sure your FastAPI server is running on http://localhost:8000")
    print("🔗 Streamlit app will be available at http://localhost:8501")
    print("-" * 50)
    
    # Run streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--theme.base=light"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Streamlit app...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 