from __future__ import annotations
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


# Global session factory
_session_factory = None


def init_database(database_url: str, echo: bool = False) -> None:
    """Initialize the database with all tables."""
    global _session_factory

    engine, session_factory = make_engine(database_url, echo)
    _session_factory = session_factory

    # Create all tables
    Base.metadata.create_all(engine)


def make_engine(url: str, echo: bool = False):
    """Create database engine and session factory."""
    eng = create_engine(url, future=True, echo=echo)
    return eng, sessionmaker(bind=eng, future=True)


class SessionContext:
    """Context manager for database sessions."""

    def __init__(self):
        if _session_factory is None:
            # Initialize with default SQLite database
            init_database("sqlite:///./workspace/plotty.db")
        self.session = _session_factory()

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
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
    """Get the database file path for a workspace."""
    return workspace / "plotty.db"
