#!/usr/bin/env python3
"""
API stability verification for ploTTY v0.9.0.

This script analyzes the public API structure and identifies what should be
considered stable public API vs internal implementation details.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List


def analyze_module_public_api(module_path: Path) -> Dict[str, List[str]]:
    """Analyze a Python module to identify public API elements."""
    public_api = {"classes": [], "functions": [], "constants": [], "imports": []}

    try:
        with open(module_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class is public (doesn't start with underscore)
                if not node.name.startswith("_"):
                    public_api["classes"].append(node.name)

            elif isinstance(node, ast.FunctionDef):
                # Check if function is public
                if not node.name.startswith("_"):
                    public_api["functions"].append(node.name)

            elif isinstance(node, ast.Assign):
                # Check for module-level constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        if isinstance(node.value, (ast.Constant, ast.Str, ast.Num)):
                            public_api["constants"].append(target.id)

            elif isinstance(node, ast.ImportFrom):
                if node.module and not node.module.startswith("_"):
                    for alias in node.names:
                        if not alias.name.startswith("_"):
                            public_api["imports"].append(f"{node.module}.{alias.name}")

    except Exception as e:
        print(f"Error analyzing {module_path}: {e}")

    return public_api


def analyze_cli_api() -> Dict[str, List[str]]:
    """Analyze CLI command structure."""
    cli_path = Path("src/plotty/cli")
    cli_api = {"commands": [], "subcommands": []}

    if not cli_path.exists():
        return cli_api

    # Find main command modules
    for item in cli_path.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            cli_api["commands"].append(item.name)

            # Check for subcommands
            for subitem in item.iterdir():
                if (
                    subitem.is_file()
                    and subitem.suffix == ".py"
                    and not subitem.name.startswith("_")
                ):
                    cli_api["subcommands"].append(f"{item.name}.{subitem.stem}")

    return cli_api


def analyze_config_api() -> Dict[str, List[str]]:
    """Analyze configuration API."""
    config_path = Path("src/plotty/config.py")

    if not config_path.exists():
        return {}

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)

        config_classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Cfg"):
                config_classes.append(node.name)

        return {"config_classes": config_classes}

    except Exception as e:
        print(f"Error analyzing config API: {e}")
        return {}


def generate_api_stability_report() -> str:
    """Generate comprehensive API stability report."""
    print("🔍 Analyzing ploTTY API structure...")

    # Analyze core modules
    core_modules = [
        "config.py",
        "models.py",
        "fsm.py",
        "db.py",
        "utils.py",
        "stats.py",
        "recovery.py",
        "hooks.py",
    ]

    api_analysis = {}

    for module in core_modules:
        module_path = Path(f"src/plotty/{module}")
        if module_path.exists():
            api_analysis[module] = analyze_module_public_api(module_path)

    # Analyze CLI API
    cli_api = analyze_cli_api()

    # Analyze Config API
    config_api = analyze_config_api()

    # Generate report
    report = """# ploTTY v0.9.0 API Stability Report

## Executive Summary

This report analyzes the current ploTTY API structure to identify stable public APIs
that should be maintained for v1.0.0 compatibility.

## Core Module APIs

"""

    for module_name, api in api_analysis.items():
        report += f"### {module_name}\n\n"

        if api["classes"]:
            report += "**Public Classes:**\n"
            for cls in api["classes"]:
                report += f"- `{cls}`\n"
            report += "\n"

        if api["functions"]:
            report += "**Public Functions:**\n"
            for func in api["functions"]:
                report += f"- `{func}()`\n"
            report += "\n"

        if api["constants"]:
            report += "**Public Constants:**\n"
            for const in api["constants"]:
                report += f"- `{const}`\n"
            report += "\n"

        if not any(api.values()):
            report += "*No public API elements identified*\n\n"

    # CLI API section
    report += "## CLI API\n\n"
    report += "### Main Commands\n\n"
    for cmd in cli_api["commands"]:
        report += f"- `plotty {cmd}`\n"

    report += "\n### Command Subcommands\n\n"
    for subcommand in cli_api["subcommands"]:
        report += f"- `{subcommand}`\n"

    # Config API section
    report += "\n## Configuration API\n\n"
    if config_api.get("config_classes"):
        report += "**Configuration Classes:**\n"
        for cls in config_api["config_classes"]:
            report += f"- `{cls}`\n"

    # API Stability Recommendations
    report += """

## API Stability Recommendations

### 🟢 STABLE APIs (Safe for v1.0.0)

**CLI Commands:**
- All top-level `plotty` commands and their basic options
- Core workflow commands: `add`, `list`, `info`, `check`, `remove`, `stats`

**Configuration:**
- All `*Cfg` classes in `config.py`
- YAML-based configuration structure
- Environment variable overrides

**Core Models:**
- Database models in `models.py` (Job, Layer, Pen, Paper, etc.)
- FSM states and transitions

### 🟡 STABILIZING APIs (Review needed)

**Internal Modules:**
- `utils.py` functions (review for utility vs internal use)
- `stats.py` service classes
- `recovery.py` system classes

**Advanced Features:**
- Hook system APIs
- Plugin system interfaces
- Advanced configuration options

### 🔴 INTERNAL APIs (Not for public use)

**Implementation Details:**
- Database session management
- Internal FSM implementation
- CLI argument parsing internals
- Logging system internals

## v1.0.0 API Stability Requirements

### Must Be Stable
1. **CLI Command Structure** - All current commands must remain compatible
2. **Configuration Format** - YAML structure must remain backward compatible
3. **Database Models** - Core models must maintain compatibility
4. **Basic Workflows** - Core job lifecycle operations

### Should Be Stable
1. **Utility Functions** - Common utilities in `utils.py`
2. **Statistics API** - Performance and job statistics
3. **Recovery System** - Job recovery and resumption

### Can Change
1. **Internal Implementation** - FSM internals, database sessions
2. **CLI Argument Parsing** - Internal argument handling
3. **Logging System** - Internal logging structure

## Recommendations for v0.9.0

1. **Document Public APIs** - Add proper docstrings to all public elements
2. **Version the APIs** - Consider API versioning for future changes
3. **Create API Tests** - Add compatibility tests for public APIs
4. **Deprecation Policy** - Establish clear deprecation policy for v1.0.0

## Next Steps

1. Review and approve this API stability analysis
2. Update documentation to reflect stable vs internal APIs
3. Add API compatibility tests to test suite
4. Prepare v1.0.0 API stability guarantee
"""

    return report


def main():
    """Main API stability analysis."""
    print("🔍 ploTTY v0.9.0 API Stability Analysis")
    print("=" * 50)

    report = generate_api_stability_report()

    # Save report
    with open("API_STABILITY_REPORT.md", "w") as f:
        f.write(report)

    print("📋 API stability report saved to: API_STABILITY_REPORT.md")
    print("🎯 Review the report to identify stable vs internal APIs")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  API analysis interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ API analysis failed: {e}")
        sys.exit(1)
