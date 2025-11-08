"""
Main entry point for CLI package.
"""

# Performance: Lazy loading for faster CLI startup
def lazy_import(module_name: str):
    """Lazy import for better CLI startup performance."""
    import importlib
    return importlib.import_module(module_name)

from . import app

if __name__ == "__main__":
    app()
