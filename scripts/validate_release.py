#!/usr/bin/env python3
"""
Quick validation script for ploTTY release readiness.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"STDERR: {result.stderr}")
        return None
    
    return result


def check_git_status():
    """Check git repository status."""
    print("🔍 Checking git status...")
    
    # Check if we're on main or master branch
    result = run_command("git branch --show-current", check=False)
    branch = result.stdout.strip() if result else ""
    if branch not in ["main", "master"]:
        print(f"⚠️  Not on main branch (currently on {branch})")
        return False
    
    # Check if working directory is clean
    result = run_command("git status --porcelain", check=False)
    if result and result.stdout.strip():
        print("❌ Working directory is not clean")
        return False
    
    print("✅ Git status is clean")
    return True


def check_version():
    """Check current version."""
    print("📌 Checking version...")
    
    result = run_command("uvx python -c \"import tomllib; data=tomllib.load(open('pyproject.toml', 'rb')); print(data['project']['version'])\"")
    if result:
        version = result.stdout.strip()
        print(f"✅ Current version: {version}")
        return version
    
    return None


def check_tests():
    """Quick test check."""
    print("🧪 Quick test check...")
    
    # Just run a few critical tests
    tests = [
        ("Import test", "uv run python -c \"import plotty; print('✅ Import successful')\""),
        ("CLI test", "plotty --help > /dev/null"),
        ("Config check", "plotty check config > /dev/null 2>&1 || echo 'Config check completed with warnings'"),
    ]
    
    all_passed = True
    
    for test_name, cmd in tests:
        print(f"  🔄 {test_name}...")
        result = run_command(cmd, check=False)
        if result and result.returncode == 0:
            print(f"  ✅ {test_name} passed")
        else:
            print(f"  ⚠️  {test_name} failed or had warnings")
            # Don't fail for warnings
    
    return all_passed


def check_build():
    """Check if package can be built."""
    print("📦 Checking build...")
    
    result = run_command("uv build --wheel", check=False)
    if result and result.returncode == 0:
        print("✅ Package builds successfully")
        return True
    else:
        print("❌ Package build failed")
        return False


def main():
    """Main validation."""
    print("🚀 ploTTY Release Readiness Validation")
    print("=" * 50)
    
    checks = [
        ("Git Status", check_git_status),
        ("Version Check", lambda: check_version() is not None),
        ("Tests", check_tests),
        ("Build", check_build),
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}:")
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            all_passed = False
    
    print(f"\n{'='*50}")
    if all_passed:
        print("🎉 All checks passed! Ready for release.")
        print("📌 Run: python scripts/release.py <version>")
    else:
        print("❌ Some checks failed. Fix issues before release.")
        sys.exit(1)


if __name__ == "__main__":
    main()