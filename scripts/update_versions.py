#!/usr/bin/env python3
"""Comprehensive version synchronization across all files."""

import hashlib
import urllib.request
import re
import sys
import subprocess


def get_source_version():
    """Get version from central source."""
    with open("src/plotty/__init__.py") as f:
        content = f.read()
        match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
        return match.group(1) if match else None


def update_pyproject_toml(version):
    """Update pyproject.toml version."""
    with open("pyproject.toml", "r") as f:
        content = f.read()

    # Check if version needs updating
    current_match = re.search(r'version = ["\']([^"\']+)["\']', content)
    if current_match and current_match.group(1) == version:
        print(f"✅ pyproject.toml already at v{version}")
        return True

    content = re.sub(r'version = ["\'][^"\']+["\']', f'version = "{version}"', content)

    with open("pyproject.toml", "w") as f:
        f.write(content)


def update_cli_fallback(version):
    """Update CLI fallback version."""
    with open("src/plotty/cli/__init__.py", "r") as f:
        content = f.read()

    # Check if fallback version needs updating
    current_match = re.search(
        r'except metadata\.PackageNotFoundError:\s*\n\s*__version__ = ["\']([^"\']+)["\']',
        content,
    )
    if current_match and current_match.group(1) == version:
        print(f"✅ CLI fallback already at v{version}")
        return True

    content = re.sub(
        r'(__version__ = )["\'][^"\']+["\'](?=\s*$)',
        f'\\1"{version}"',
        content,
        flags=re.MULTILINE,
    )

    with open("src/plotty/cli/__init__.py", "w") as f:
        f.write(content)


def update_pkgbuild(version):
    """Update PKGBUILD version and hash."""
    print(f"📦 Updating PKGBUILD to v{version}")

    # Update version first
    with open("packaging/PKGBUILD", "r") as f:
        content = f.read()

    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line.startswith("pkgver="):
            lines[i] = f"pkgver={version}"
            break

    with open("packaging/PKGBUILD", "w") as f:
        f.write("\n".join(lines))

    # Try updpkgsums first (preferred method)
    try:
        subprocess.run(
            ["updpkgsums", "packaging/PKGBUILD"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✅ PKGBUILD updated with updpkgsums")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  updpkgsums failed: {e}")
        return update_pkgbuild_manual(version)
    except FileNotFoundError:
        print("⚠️  updpkgsums not available, using manual hash calculation")
        return update_pkgbuild_manual(version)


def update_pkgbuild_manual(version):
    """Manual hash calculation as fallback."""
    try:
        url = f"https://github.com/bkuri/plotty/archive/refs/tags/v{version}.tar.gz"
        response = urllib.request.urlopen(url)
        data = response.read()
        sha256_hash = hashlib.sha256(data).hexdigest()

        with open("packaging/PKGBUILD", "r") as f:
            content = f.read()

        content = re.sub(
            r'sha256sums=\([\'"][^\'"]+[\'"]\)',
            f"sha256sums=('{sha256_hash}')",
            content,
        )

        with open("packaging/PKGBUILD", "w") as f:
            f.write(content)

        print("✅ PKGBUILD hash updated manually")
        return True
    except Exception:
        print("⚠️  Tag v{version} not found yet - updating version only")
        print("   Hash will be updated when tag is created")
        return True  # Still successful, just no hash update


def update_websocket_version(version):
    """Update WebSocket server version."""
    with open("src/plotty/websocket/server.py", "r") as f:
        content = f.read()

    # Check if version needs updating
    current_match = re.search(r'version=["\']([^"\']+)["\']', content)
    if current_match and current_match.group(1) == version:
        print(f"✅ WebSocket server already at v{version}")
        return True

    content = re.sub(r'version=["\'][^"\']+["\']', f'version="{version}"', content)

    with open("src/plotty/websocket/server.py", "w") as f:
        f.write(content)


def update_backup_version(version):
    """Update backup format version."""
    with open("src/plotty/backup.py", "r") as f:
        content = f.read()

    # Check if version needs updating
    current_match = re.search(r'version: str = ["\']([^"\']+)["\']', content)
    if current_match and current_match.group(1) == version:
        print(f"✅ Backup format already at v{version}")
        return True

    content = re.sub(
        r'version: str = ["\'][^"\']+["\']', f'version: str = "{version}"', content
    )

    with open("src/plotty/backup.py", "w") as f:
        f.write(content)


def update_all_versions():
    """Update all version locations."""
    version = get_source_version()
    if not version:
        print("❌ Could not determine source version")
        return False

    print(f"🔄 Synchronizing all versions to {version}")

    updates = [
        ("pyproject.toml", update_pyproject_toml),
        ("CLI fallback", update_cli_fallback),
        ("PKGBUILD", update_pkgbuild),
        ("WebSocket server", update_websocket_version),
        ("Backup format", update_backup_version),
    ]

    success_count = 0
    for name, updater in updates:
        try:
            if updater(version):
                success_count += 1
            else:
                print(f"❌ Failed to update {name}")
        except Exception as e:
            print(f"❌ Failed to update {name}: {e}")

    print(f"📊 Updated {success_count}/{len(updates)} version locations")
    return success_count == len(updates)


if __name__ == "__main__":
    if not update_all_versions():
        sys.exit(1)
