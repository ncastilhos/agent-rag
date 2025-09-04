#!/usr/bin/env python3
"""
Test runner script for AgentRAGServer tests
Usage: python run_tests.py
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with verbose output"""
    print("Running AgentRAGServer tests...")
    print("=" * 50)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_agent_rag_server.py", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], check=True, capture_output=False)
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("❌ Some tests failed!")
        print(f"Exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
