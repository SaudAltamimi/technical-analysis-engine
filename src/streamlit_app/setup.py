#!/usr/bin/env python3
"""
Setup script for the Streamlit frontend app
This app is completely separate from the technical analysis engine
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def main():
    """Setup the Streamlit app environment"""
    print("🚀 Setting up Streamlit Frontend App")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("requirements.txt"):
        print("❌ Error: requirements.txt not found")
        print("Make sure you're running this from the src/streamlit_app directory")
        sys.exit(1)
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Streamlit dependencies"):
        print("\n❌ Setup failed")
        sys.exit(1)
    
    print("\n✅ Streamlit app setup complete!")
    print("\n🎯 Next steps:")
    print("1. Start the API server: cd ../.. && make api")
    print("2. Start this Streamlit app: streamlit run streamlit_app.py")
    print("   or from project root: make streamlit")
    
    print("\n📋 Architecture:")
    print("• This Streamlit app is a pure frontend")
    print("• It communicates with the FastAPI backend via HTTP")
    print("• No vectorbt or heavy analysis dependencies needed here")


if __name__ == "__main__":
    main() 