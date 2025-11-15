"""
PostgreSQL database driver for vfab.

This module provides PostgreSQL-specific database initialization and configuration.
"""

from __future__ import annotations
from typing import Tuple
from urllib.parse import urlparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


def create_postgresql_engine(
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    echo: bool = False,
    **kwargs,
) -> Tuple[any, sessionmaker]:
    """Create PostgreSQL database engine and session factory.

    Args:
        host: PostgreSQL server host
        port: PostgreSQL server port
        database: Database name
        username: Database username
        password: Database password
        echo: Whether to enable SQLAlchemy echo logging
        **kwargs: Additional SQLAlchemy engine options

    Returns:
        Tuple of (engine, session_factory)
    """
    # Build PostgreSQL connection string
    database_url = get_postgresql_url(
        host, port, database, username, password, **kwargs
    )

    # Create engine with PostgreSQL-specific settings
    engine = create_engine(
        database_url,
        future=True,
        echo=echo,
        # PostgreSQL-specific settings
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,  # Recycle connections every hour
    )

    session_factory = sessionmaker(bind=engine, future=True)

    return engine, session_factory


def get_postgresql_url(
    host: str, port: int, database: str, username: str, password: str, **kwargs
) -> str:
    """Get PostgreSQL connection URL.

    Args:
        host: PostgreSQL server host
        port: PostgreSQL server port
        database: Database name
        username: Database username
        password: Database password
        **kwargs: Additional connection parameters

    Returns:
        PostgreSQL connection URL string
    """
    # Build connection parameters
    params = []

    # Add optional parameters
    if "sslmode" in kwargs:
        params.append(f"sslmode={kwargs['sslmode']}")
    if "connect_timeout" in kwargs:
        params.append(f"connect_timeout={kwargs['connect_timeout']}")
    if "application_name" in kwargs:
        params.append(f"application_name={kwargs['application_name']}")

    # Construct URL
    param_string = "?" + "&".join(params) if params else ""
    return f"postgresql://{username}:{password}@{host}:{port}/{database}{param_string}"


def is_postgresql_url(database_url: str) -> bool:
    """Check if database URL is for PostgreSQL.

    Args:
        database_url: Database connection URL

    Returns:
        True if URL is PostgreSQL format
    """
    return database_url.startswith(("postgresql://", "postgres://"))


def parse_postgresql_url(database_url: str) -> dict:
    """Parse PostgreSQL connection URL into components.

    Args:
        database_url: PostgreSQL connection URL

    Returns:
        Dictionary with connection components
    """
    parsed = urlparse(database_url)

    return {
        "host": parsed.hostname,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/"),
        "username": parsed.username,
        "password": parsed.password,
    }


def optimize_postgresql_connection(engine: any) -> None:
    """Apply PostgreSQL-specific performance optimizations.

    Args:
        engine: SQLAlchemy engine instance
    """
    # PostgreSQL-specific optimizations can be applied here
    # For example, setting connection parameters, etc.
    pass


class PostgreSQLSessionContext:
    """PostgreSQL-specific session context manager with optimizations."""

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self) -> Session:
        self.session = self.session_factory()

        # Apply PostgreSQL optimizations
        optimize_postgresql_connection(self.session.bind)

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


def test_postgresql_connection(
    host: str, port: int, database: str, username: str, password: str
) -> bool:
    """Test PostgreSQL database connection.

    Args:
        host: PostgreSQL server host
        port: PostgreSQL server port
        database: Database name
        username: Database username
        password: Database password

    Returns:
        True if connection successful
    """
    try:
        engine, _ = create_postgresql_engine(host, port, database, username, password)

        # Test connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")

        return True
    except Exception:
        return False
