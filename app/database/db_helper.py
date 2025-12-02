from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import Session
from app.database.base import SessionLocal

# Global variable to hold the test session (set by tests)
_test_session: Optional[Session] = None


def set_test_session(session: Optional[Session]):
    """
    Set the session to use during tests.
    
    Args:
        session: The test session to use, or None to clear it
    """
    global _test_session
    _test_session = session


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get a database session context manager.
    
    - In production: creates a new session from SessionLocal
    - In tests: uses the injected test session (participates in test transaction)
    
    Usage:
        with get_db_session() as session:
            user = session.query(User).filter(User.email == email).first()
    
    Yields:
        Session: Database session
    """
    if _test_session is not None:
        # During tests, use the test session (participates in test transaction)
        # Don't close it - the test fixture manages its lifecycle
        yield _test_session
    else:
        # In production, create a new session
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
