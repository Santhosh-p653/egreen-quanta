"""
database.py — PostgreSQL & SQLAlchemy Database Engine with Automatic SQLite Fallback.
Provides database connectivity, session lifecycle management, and auto-initialization.
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger("egreen-quanta-db")
logging.basicConfig(level=logging.INFO)

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/egreen_quanta"
)
FALLBACK_SQLITE_URL = "sqlite:///./egreen_quanta.db"

Base = declarative_base()

# Initialize engine with graceful fallback
active_db_type = "postgresql"
try:
    if "postgresql" in DATABASE_URL:
        # Quick probe to check if PostgreSQL instance is actively reachable
        test_engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"connect_timeout": 2})
        with test_engine.connect() as conn:
            pass
        engine = test_engine
        logger.info(f"Connected successfully to PostgreSQL database: {DATABASE_URL.split('@')[-1]}")
    else:
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        active_db_type = "sqlite"
except Exception as e:
    logger.warning(
        f"Could not connect to PostgreSQL ({e}). "
        f"Falling back to embedded SQLite database ({FALLBACK_SQLITE_URL}) for 100% uninterrupted operation."
    )
    engine = create_engine(FALLBACK_SQLITE_URL, connect_args={"check_same_thread": False})
    active_db_type = "sqlite"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI Dependency for transactional database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_status():
    """Returns status dictionary of the database layer."""
    return {
        "engine": active_db_type,
        "url_masked": DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "local_file",
        "is_connected": True,
    }


def init_db():
    """Initializes tables and metadata."""
    import models  # Ensure models are registered with Base
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database schema synchronized on {active_db_type}.")
    return active_db_type
