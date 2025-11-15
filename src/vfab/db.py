"""
Database driver manager for vfab.

This module provides database-agnostic session management and driver selection.
Supports SQLite and PostgreSQL with extensible architecture for additional databases.
"""

from __future__ import annotations
from pathlib import Path

from .models import Base

# Import database drivers
from .drivers.sqlite import create_sqlite_engine, is_sqlite_url, SQLiteSessionContext
from .drivers.postgresql import (
    create_postgresql_engine,
    is_postgresql_url,
    parse_postgresql_url,
    PostgreSQLSessionContext,
)


# Global session factory
_session_factory = None
_database_type = None


def init_database(database_url: str, echo: bool = False) -> None:
    """Initialize database with all tables using appropriate driver.

    Args:
        database_url: Database connection URL
        echo: Whether to enable SQLAlchemy echo logging
    """
    global _session_factory, _database_type

    engine, session_factory = _create_engine_and_factory(database_url, echo)
    _session_factory = session_factory
    _database_type = _detect_database_type(database_url)

    # Create all tables
    Base.metadata.create_all(engine)


def _create_engine_and_factory(database_url: str, echo: bool):
    """Create appropriate engine and session factory based on database URL.

    Args:
        database_url: Database connection URL
        echo: Whether to enable SQLAlchemy echo logging

    Returns:
        Tuple of (engine, session_factory)
    """
    if is_sqlite_url(database_url):
        # Extract path from SQLite URL
        db_path = Path(database_url.replace("sqlite:///", ""))
        return create_sqlite_engine(db_path, echo)

    elif is_postgresql_url(database_url):
        # Parse PostgreSQL URL
        parsed = parse_postgresql_url(database_url)
        return create_postgresql_engine(
            host=parsed["host"],
            port=parsed["port"],
            database=parsed["database"],
            username=parsed["username"],
            password=parsed["password"],
            echo=echo,
        )

    else:
        raise ValueError(f"Unsupported database URL: {database_url}")


def _detect_database_type(database_url: str) -> str:
    """Detect database type from URL.

    Args:
        database_url: Database connection URL

    Returns:
        Database type string ('sqlite' or 'postgresql')
    """
    if is_sqlite_url(database_url):
        return "sqlite"
    elif is_postgresql_url(database_url):
        return "postgresql"
    else:
        return "unknown"


class SessionContext:
    """Database-agnostic session context manager."""

    def __init__(self):
        global _session_factory, _database_type

        if _session_factory is None:
            # Initialize with default SQLite database
            init_database("sqlite:///./workspace/vfab.db")
            _database_type = "sqlite"

        self.session_factory = _session_factory
        self.database_type = _database_type
        self.session = None

    def __enter__(self):
        # Create appropriate session context based on database type
        if self.database_type == "sqlite":
            sqlite_context = SQLiteSessionContext(self.session_factory)
            self.session = sqlite_context.__enter__()
            return self.session
        elif self.database_type == "postgresql":
            postgresql_context = PostgreSQLSessionContext(self.session_factory)
            self.session = postgresql_context.__enter__()
            return self.session
        else:
            # Fallback to basic session
            self.session = self.session_factory()
            return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type is not None:
                    self.session.rollback()
                else:
                    self.session.commit()
            finally:
                self.session.close()


def get_session() -> SessionContext:
    """Get a database session context manager."""
    return SessionContext()


def get_database_path(workspace: Path) -> Path:
    """Get database file path for a workspace (SQLite only).

    Args:
        workspace: Path to workspace directory

    Returns:
        Path to SQLite database file
    """
    return workspace / "vfab.db"


def get_database_info() -> dict:
    """Get information about current database configuration.

    Returns:
        Dictionary with database type and connection info
    """
    return {
        "database_type": _database_type or "not_initialized",
        "session_factory_initialized": _session_factory is not None,
    }


def make_engine(url: str, echo: bool = False):
    """Legacy function for backward compatibility.

    Args:
        url: Database connection URL
        echo: Whether to enable SQLAlchemy echo logging

    Returns:
        Tuple of (engine, session_factory)
    """
    return _create_engine_and_factory(url, echo)


def is_valid_database_url(database_url: str) -> bool:
    """Check if database URL is supported.

    Args:
        database_url: Database connection URL

    Returns:
        True if URL format is supported
    """
    return is_sqlite_url(database_url) or is_postgresql_url(database_url)


def get_default_database_url(workspace: Path) -> str:
    """Get default database URL for workspace.

    Args:
        workspace: Path to workspace directory

    Returns:
        Default SQLite database URL
    """
    db_path = get_database_path(workspace)
    return f"sqlite:///{db_path}"
