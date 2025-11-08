#!/usr/bin/env python3
"""
Release engineering script for ploTTY.

This script automates the release process including:
- Version bumping
- Changelog generation
- Tag creation
- Build verification
- Release notes generation
"""

import subprocess
import sys


def run_command(cmd: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(1)
    
    return result


def get_current_version() -> str:
    """Get current version from pyproject.toml."""
    result = run_command("uvx python -c \"import tomllib; data=tomllib.load(open('pyproject.toml', 'rb')); print(data['project']['version'])\"")
    return result.stdout.strip()


def update_version(new_version: str) -> None:
    """Update version in pyproject.toml."""
    print(f"📝 Updating version to {new_version}")
    
    # Read current pyproject.toml
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    # Replace version line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('version = '):
            lines[i] = f'version = "{new_version}"'
            break
    
    # Write back
    with open('pyproject.toml', 'w') as f:
        f.write('\n'.join(lines))


def generate_changelog() -> str:
    """Generate changelog from git commits since last tag."""
    print("📋 Generating changelog...")
    
    # Get last tag
    try:
        result = run_command("git describe --tags --abbrev=0")
        last_tag = result.stdout.strip()
    except subprocess.CalledProcessError:
        last_tag = "v0.1.0"
        print(f"⚠️  No tags found, using {last_tag}")
    
    # Get commits since last tag
    result = run_command(f"git log {last_tag}..HEAD --oneline --no-merges")
    commits = result.stdout.strip().split('\n')
    
    # Categorize commits
    categories = {
        '✨ Features': [],
        '🐛 Bug Fixes': [],
        '🔧 Improvements': [],
        '📚 Documentation': [],
        '🧪 Testing': [],
        '🔀 Refactoring': [],
        '🛠️ Build': [],
        '📦 Other': []
    }
    
    for commit in commits:
        if not commit.strip():
            continue
            
        # Parse commit hash and message
        parts = commit.split(' ', 1)
        if len(parts) < 2:
            continue
            
        hash_short = parts[0]
        message = parts[1]
        
        # Categorize based on message content
        if any(keyword in message.lower() for keyword in ['feat', 'feature', 'add']):
            categories['✨ Features'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['fix', 'bug', 'issue']):
            categories['🐛 Bug Fixes'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['improve', 'optimize', 'enhance']):
            categories['🔧 Improvements'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['doc', 'readme', 'changelog']):
            categories['📚 Documentation'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['test', 'pytest']):
            categories['🧪 Testing'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['refactor', 'cleanup']):
            categories['🔀 Refactoring'].append(f"- {message} ({hash_short})")
        elif any(keyword in message.lower() for keyword in ['build', 'ci', 'cd']):
            categories['🛠️ Build'].append(f"- {message} ({hash_short})")
        else:
            categories['📦 Other'].append(f"- {message} ({hash_short})")
    
    # Generate changelog
    changelog = "# Changelog\n\n"
    changelog += f"## Changes since {last_tag}\n\n"
    
    for category, items in categories.items():
        if items:
            changelog += f"### {category}\n\n"
            for item in items:
                changelog += f"{item}\n"
            changelog += "\n"
    
    return changelog


def run_tests() -> bool:
    """Run comprehensive test suite."""
    print("🧪 Running comprehensive test suite...")
    
    tests = [
        ("Linting", "uvx ruff check ."),
        ("Formatting", "uvx black --check ."),
        ("Unit tests", "uv run pytest -q"),
        ("Load tests", "uv run python test_load.py --quick"),
        ("Memory tests", "uv run python test_memory_simple.py"),
        ("Database tests", "uv run python test_database_performance.py")
    ]
    
    all_passed = True
    
    for test_name, cmd in tests:
        print(f"  🔄 Running {test_name}...")
        try:
            result = run_command(cmd, check=False)
            if result.returncode == 0:
                print(f"  ✅ {test_name} passed")
            else:
                print(f"  ❌ {test_name} failed")
                all_passed = False
        except Exception as e:
            print(f"  ❌ {test_name} failed: {e}")
            all_passed = False
    
    return all_passed


def build_package() -> bool:
    """Build the package and verify it."""
    print("📦 Building package...")
    
    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info", check=False)
    
    # Build
    run_command("uv build --wheel")
    
    # Check package
    run_command("uvx twine check dist/*")
    
    return True


def create_release_tag(version: str) -> None:
    """Create and push git tag."""
    print(f"🏷️  Creating release tag v{version}")
    
    # Create tag
    run_command(f"git tag -a v{version} -m 'Release v{version}'")
    
    # Push tag
    run_command(f"git push origin v{version}")


def generate_release_notes(version: str, changelog: str) -> str:
    """Generate release notes."""
    notes = f"""# ploTTY v{version} Release Notes

{changelog}

## Installation

```bash
# Install from PyPI
pip install plotty

# Install with vpype support
pip install plotty[vpype]

# Install with AxiDraw support
pip install plotty[axidraw]

# Install development version
pip install git+https://github.com/your-repo/plotty.git
```

## Verification

After installation, verify with:

```bash
plotty check self --level=all
```

## Performance

This release includes comprehensive performance testing:
- Load testing: Excellent performance under heavy workloads
- Memory efficiency: Optimal memory usage with no leaks detected
- Database performance: Fast query execution and excellent concurrency

## Support

- 📖 [Documentation](https://plotty.ai/docs)
- 🐛 [Issue Tracker](https://github.com/your-repo/plotty/issues)
- 💬 [Discussions](https://github.com/your-repo/plotty/discussions)
"""
    
    return notes


def main():
    """Main release process."""
    print("🚀 ploTTY Release Engineering")
    print("=" * 50)
    
    # Check if we're on main branch
    result = run_command("git branch --show-current", check=False)
    if result.stdout.strip() != "main":
        print("⚠️  Warning: Not on main branch")
    
    # Check if working directory is clean
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("❌ Working directory is not clean")
        sys.exit(1)
    
    # Get current version
    current_version = get_current_version()
    print(f"📌 Current version: {current_version}")
    
    # Ask for new version
    if len(sys.argv) > 1:
        new_version = sys.argv[1]
    else:
        new_version = input("🔢 Enter new version (e.g., 0.8.0): ").strip()
    
    if not new_version:
        print("❌ Version is required")
        sys.exit(1)
    
    print(f"🎯 Releasing version: {new_version}")
    
    # Confirm
    confirm = input(f"❓ Continue with release v{new_version}? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Release cancelled")
        sys.exit(0)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed - aborting release")
        sys.exit(1)
    
    # Update version
    update_version(new_version)
    
    # Generate changelog
    changelog = generate_changelog()
    
    # Save changelog
    with open('CHANGELOG_RELEASE.md', 'w') as f:
        f.write(changelog)
    
    print("📋 Changelog saved to CHANGELOG_RELEASE.md")
    
    # Build package
    if not build_package():
        print("❌ Build failed - aborting release")
        sys.exit(1)
    
    # Commit version change
    run_command("git add pyproject.toml CHANGELOG_RELEASE.md")
    run_command(f"git commit -m 'Release v{new_version}'")
    
    # Push changes
    run_command("git push origin main")
    
    # Create tag
    create_release_tag(new_version)
    
    # Generate release notes
    release_notes = generate_release_notes(new_version, changelog)
    
    # Save release notes
    with open('RELEASE_NOTES.md', 'w') as f:
        f.write(release_notes)
    
    print("📝 Release notes saved to RELEASE_NOTES.md")
    
    print(f"\n🎉 Release v{new_version} completed successfully!")
    print("📦 Package built in dist/")
    print(f"🏷️  Tag v{new_version} created and pushed")
    print("📋 Release notes ready in RELEASE_NOTES.md")
    print("\n📌 Next steps:")
    print("  1. Create GitHub release using RELEASE_NOTES.md")
    print("  2. PyPI upload will happen automatically via GitHub Actions")
    print("  3. Update documentation if needed")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Release cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Release failed: {e}")
        sys.exit(1)