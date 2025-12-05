from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Get database URL from environment or construct it
database_url = os.getenv("DATABASE_URL")

if not database_url:
    # Construct DATABASE_URL from individual variables
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")
    
    # Use 'db' as host when in Docker (service name), 'localhost' when running locally
    postgres_host = os.getenv("POSTGRES_HOST", "db")
    
    if postgres_user and postgres_password and postgres_db:
        database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/{postgres_db}"

if not database_url:
    raise ValueError("DATABASE_URL or POSTGRES_* environment variables must be set")

# Create engine
engine = create_engine(database_url, echo=False)  # Set to False to reduce SQL log noise

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

"""Database base configuration and FastAPI DB dependency."""


# Dependency for FastAPI
def get_db():
    """Yield a DB session.

    In normal app usage (server running):
    - open a new session
    - yield it to the request handler
    - on success, commit
    - on error, rollback

    In tests, this function is overridden in tests/conftest.py so that:
    - the same test session is reused
    - commit is **not** called here (tests use transactions + rollback)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()