#!/usr/bin/env python3
"""
Test runner for Technical Analysis Engine
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run the test suite"""
    print("🧪 Technical Analysis Engine Test Suite")
    print("=" * 50)
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    
    try:
        # Run unit tests first
        print("\n📊 Running Unit Tests...")
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/unit/", 
            "-v", "--tb=short"
        ], cwd=project_root)
        
        if result.returncode != 0:
            print("❌ Unit tests failed!")
            return False
        
        print("✅ Unit tests passed!")
        
        # Check if API server is running for integration tests
        import requests
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("\n🔗 Running Integration Tests...")
                result = subprocess.run([
                    sys.executable, "-m", "pytest",
                    "tests/integration/",
                    "-v", "--tb=short", "-m", "integration"
                ], cwd=project_root)
                
                if result.returncode == 0:
                    print("✅ Integration tests passed!")
                else:
                    print("❌ Integration tests failed!")
                    return False
            else:
                print("\n⚠️  Skipping integration tests (API server not responding)")
        except (requests.exceptions.RequestException, ImportError):
            print("\n⚠️  Skipping integration tests (API server not running)")
            print("   Start API server with: make api")
        
        print("\n🎉 All available tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 