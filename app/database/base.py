from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
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
engine = create_engine(database_url, echo=True)

# Base class for models
class Base(SQLModel):
    pass