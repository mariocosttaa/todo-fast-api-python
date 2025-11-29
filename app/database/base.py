from sqlmodel import SQLModel, create_engine
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Construct database URL
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")

database_url = f"postgresql://{postgres_user}:{postgres_password}@localhost:5432/{postgres_db}"

# Create engine
engine = create_engine(database_url, echo=True)

# Base class for models
class Base(SQLModel):
    pass