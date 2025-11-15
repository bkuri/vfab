"""
SQLite database driver for vfab.

This module provides SQLite-specific database initialization and configuration.
"""

from __future__ import annotations
from pathlib import Path
from typing import Tuple

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def create_sqlite_engine(db_path: Path, echo: bool = False) -> Tuple[any, sessionmaker]:
    """Create SQLite database engine and session factory.

    Args:
        db_path: Path to SQLite database file
        echo: Whether to enable SQLAlchemy echo logging

    Returns:
        Tuple of (engine, session_factory)
    """
    # Ensure parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # SQLite-specific connection string
    database_url = f"sqlite:///{db_path}"

    # Create engine with SQLite-specific optimizations
    engine = create_engine(
        database_url,
        future=True,
        echo=echo,
        # SQLite-specific settings
        connect_args={
            "check_same_thread": False,  # Allow multi-threaded access
            "timeout": 20,  # Connection timeout
        },
    )

    session_factory = sessionmaker(bind=engine, future=True)

    return engine, session_factory


def get_sqlite_url(db_path: Path) -> str:
    """Get SQLite connection URL for given database path.

    Args:
        db_path: Path to SQLite database file

    Returns:
        SQLite connection URL string
    """
    return f"sqlite:///{db_path}"


def is_sqlite_url(database_url: str) -> bool:
    """Check if database URL is for SQLite.

    Args:
        database_url: Database connection URL

    Returns:
        True if URL is SQLite format
    """
    return database_url.startswith("sqlite:///")


def optimize_sqlite_connection(engine: any) -> None:
    """Apply SQLite-specific performance optimizations.

    Args:
        engine: SQLAlchemy engine instance
    """
    # Enable WAL mode for better concurrent access
    with engine.connect() as conn:
        from sqlalchemy import text

        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))
        conn.execute(text("PRAGMA cache_size=10000"))
        conn.execute(text("PRAGMA temp_store=MEMORY"))
        conn.commit()


class SQLiteSessionContext:
    """SQLite-specific session context manager with optimizations."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self) -> Session:
        self.session = self.session_factory()

        # Apply SQLite optimizations
        optimize_sqlite_connection(self.session.bind)

        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.session:
            try:
                if exc_type is not None:
                    self.session.rollback()
                else:
                    self.session.commit()
            finally:
                self.session.close()
