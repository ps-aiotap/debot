#!/usr/bin/env python3
"""
Test runner for RBAC system validation
"""
import subprocess
import sys

def run_tests():
    """Run all RBAC tests with coverage"""
    
    print("🔒 Testing RBAC & Tenant Isolation System")
    print("=" * 50)
    
    # Test categories
    test_suites = [
        ("Simple RBAC", "tests/test_simple_rbac.py"),
        ("API Security", "tests/test_api_security.py::TestDataIsolationIntegration"),
    ]
    
    failed_tests = []
    
    for name, test_path in test_suites:
        print(f"\n🧪 Running {name} tests...")
        
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            test_path, "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED")
            print(result.stdout)
            print(result.stderr)
            failed_tests.append(name)
    
    # Summary
    print("\n" + "=" * 50)
    if failed_tests:
        print(f"❌ {len(failed_tests)} test suite(s) failed: {', '.join(failed_tests)}")
        return 1
    else:
        print("✅ All RBAC tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(run_tests())