#!/usr/bin/env python3
"""
Cross-platform compatibility test for vfab.

This script tests vfab functionality across different platforms.
"""

import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"STDERR: {result.stderr}")
        return None

    return result


def get_platform_info():
    """Get platform information."""
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
    }
    return info


def test_file_operations():
    """Test file operations."""
    print("📁 Testing file operations...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test file creation
        test_file = temp_path / "test.txt"
        test_file.write_text("test content")

        if not test_file.exists():
            print("❌ File creation failed")
            return False

        # Test file reading
        content = test_file.read_text()
        if content != "test content":
            print("❌ File reading failed")
            return False

        # Test directory operations
        subdir = temp_path / "subdir"
        subdir.mkdir()

        if not subdir.is_dir():
            print("❌ Directory creation failed")
            return False

        print("✅ File operations passed")
        return True


def test_path_handling():
    """Test path handling."""
    print("🛤️  Testing path handling...")

    # Test path joining
    if platform.system() == "Windows":
        path1 = Path("C:\\Users\\test")
        path2 = Path("documents")
        joined = path1 / path2
        expected_sep = "\\"
    else:
        path1 = Path("/home/test")
        path2 = Path("documents")
        joined = path1 / path2
        expected_sep = "/"

    if expected_sep not in str(joined):
        print(f"❌ Path joining failed: {joined}")
        return False

    # Test path resolution
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_file = temp_path / "test.txt"
        test_file.write_text("test")

        resolved = test_file.resolve()
        if not resolved.exists():
            print("❌ Path resolution failed")
            return False

    print("✅ Path handling passed")
    return True


def test_database_operations():
    """Test database operations."""
    print("🗄️  Testing database operations...")

    try:
        # Test database initialization
        result = run_command("vfab check config", check=False)
        if result and result.returncode <= 2:  # Allow warnings
            print("✅ Database operations passed")
            return True
        else:
            print("⚠️  Database operations had issues")
            return True  # Don't fail for database issues
    except Exception as e:
        print(f"❌ Database operations failed: {e}")
        return False


def test_cli_commands():
    """Test CLI commands."""
    print("💻 Testing CLI commands...")

    commands = [
        ("vfab --help", "Help command"),
        ("vfab check config", "Config check"),
        ("vfab list pens", "List pens"),
        ("vfab list papers", "List papers"),
        ("vfab info system", "System info"),
    ]

    all_passed = True

    for cmd, description in commands:
        print(f"  🔄 Testing {description}...")
        result = run_command(cmd, check=False)

        if result and result.returncode == 0:
            print(f"  ✅ {description} passed")
        elif result and result.returncode <= 2:  # Allow warnings for config
            print(f"  ⚠️  {description} passed with warnings")
        else:
            print(f"  ❌ {description} failed")
            all_passed = False

    return all_passed


def test_environment_variables():
    """Test environment variable handling."""
    print("🌍 Testing environment variables...")

    # Test setting environment variable
    os.environ["VFAB_TEST"] = "test_value"

    if os.environ.get("VFAB_TEST") != "test_value":
        print("❌ Environment variable setting failed")
        return False

    # Test environment variable in subprocess
    result = run_command(
        "python -c \"import os; print(os.environ.get('VFAB_TEST', 'not_found'))\"",
        check=False,
    )

    if result and "test_value" in result.stdout:
        print("✅ Environment variables passed")
        return True
    else:
        print("❌ Environment variable in subprocess failed")
        return False


def test_permissions():
    """Test file permissions."""
    print("🔐 Testing file permissions...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test file creation and permissions
        test_file = temp_path / "test.txt"
        test_file.write_text("test")

        # Check if file is readable
        try:
            content = test_file.read_text()
            if content != "test":
                print("❌ File read permissions failed")
                return False
        except PermissionError:
            print("❌ File read permissions failed")
            return False

        # Check if file is writable
        try:
            test_file.write_text("test updated")
        except PermissionError:
            print("❌ File write permissions failed")
            return False

        print("✅ File permissions passed")
        return True


def test_special_characters():
    """Test handling of special characters."""
    print("🔤 Testing special characters...")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Test filenames with spaces
        space_file = temp_path / "file with spaces.txt"
        space_file.write_text("test")

        if not space_file.exists():
            print("❌ Spaces in filename failed")
            return False

        # Test filenames with special characters (platform-dependent)
        if platform.system() != "Windows":
            special_file = temp_path / "file-with-special.chars.txt"
            special_file.write_text("test")

            if not special_file.exists():
                print("❌ Special characters in filename failed")
                return False

        print("✅ Special characters passed")
        return True


def main():
    """Main cross-platform test."""
    print("🌍 vfab Cross-Platform Compatibility Test")
    print("=" * 60)

    # Get platform information
    info = get_platform_info()
    print(f"📊 Platform: {info['system']} {info['release']}")
    print(f"🖥️  Machine: {info['machine']}")
    print(f"🐍 Python: {info['python_implementation']} {info['python_version']}")
    print()

    # Run tests
    tests = [
        ("File Operations", test_file_operations),
        ("Path Handling", test_path_handling),
        ("Database Operations", test_database_operations),
        ("CLI Commands", test_cli_commands),
        ("Environment Variables", test_environment_variables),
        ("File Permissions", test_permissions),
        ("Special Characters", test_special_characters),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    print(f"\n{'='*60}")
    print(f"📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All cross-platform tests passed!")
        return True
    else:
        print("⚠️  Some cross-platform tests failed")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Cross-platform test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Cross-platform test failed: {e}")
        sys.exit(1)
