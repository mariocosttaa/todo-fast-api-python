#!/usr/bin/env python3
"""Interactive shell for database operations and model management"""
from sqlalchemy import inspect, text, select
from sqlalchemy.orm import Session
from app.database.base import engine, SessionLocal
from app.models import User, Todo, Session as SessionModel
from datetime import datetime
from typing import Type, TypeVar, Any
import uuid

# ============================================================================
# Database Session
# ============================================================================
session = SessionLocal()

# ============================================================================
# Type Definitions
# ============================================================================
ModelType = TypeVar('ModelType')

# ============================================================================
# Generic ORM Helper Functions
# ============================================================================
def all(model_class: Type[ModelType]) -> list[ModelType]:
    """Get all records from a model"""
    return list(session.query(model_class).all())

def find(model_class: Type[ModelType], id: Any) -> ModelType | None:
    """Find a record by ID"""
    return session.get(model_class, id)

def first(model_class: Type[ModelType]) -> ModelType | None:
    """Get the first record from a model"""
    return session.query(model_class).first()

def count(model_class: Type[ModelType]) -> int:
    """Count total records in a model"""
    return session.query(model_class).count()

def create(model_class: Type[ModelType], **kwargs) -> ModelType:
    """Create a new record"""
    instance = model_class(**kwargs)
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance

def delete(instance: ModelType) -> None:
    """Delete a record from the database"""
    session.delete(instance)
    session.commit()

def save(instance: ModelType) -> ModelType:
    """Save or update a record"""
    session.add(instance)
    session.commit()
    session.refresh(instance)
    return instance

# ============================================================================
# Model Method Extensions
# ============================================================================
def _add_model_methods(model_class):
    """Add convenient ORM methods to model classes"""
    @staticmethod
    def all():
        return list(session.query(model_class).all())
    
    @staticmethod
    def find(id):
        return session.get(model_class, id)
    
    @staticmethod
    def first():
        return session.query(model_class).first()
    
    @staticmethod
    def count():
        return session.query(model_class).count()
    
    @staticmethod
    def create(**kwargs):
        instance = model_class(**kwargs)
        session.add(instance)
        session.commit()
        session.refresh(instance)
        return instance
    
    model_class.all = all
    model_class.find = find
    model_class.first = first
    model_class.count = count
    model_class.create = create

# ============================================================================
# Database Management Functions
# ============================================================================
def drop_all_tables(force: bool = False):
    """Drop all tables and clear alembic_version - DANGEROUS!"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"Found {len(tables)} tables: {tables}")
    
    if not force:
        confirm = input("Are you sure you want to drop ALL tables? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        for table in tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
        conn.commit()
    
    print("✅ All tables dropped!")

def reset_database():
    """Complete reset: drop all tables and clear alembic version"""
    drop_all_tables()
    print("✅ Database reset complete!")

# ============================================================================
# Initialize Model Extensions
# ============================================================================
_add_model_methods(User)
_add_model_methods(Todo)
_add_model_methods(SessionModel)

# ============================================================================
# Command Line Interface
# ============================================================================
import sys

if len(sys.argv) > 1:
    command = sys.argv[1]
    if command == "drop-tables":
        force = "--force" in sys.argv or "-f" in sys.argv
        drop_all_tables(force=force)
        sys.exit(0)
    elif command == "reset":
        force = "--force" in sys.argv or "-f" in sys.argv
        drop_all_tables(force=force)
        print("✅ Database reset complete!")
        sys.exit(0)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: drop-tables, reset")
        sys.exit(1)

# ============================================================================
# Welcome Message
# ============================================================================
print("=" * 60)
print("FastAPI Interactive Shell")
print("=" * 60)
print("\n📦 Available Models:")
print("  - User, Todo, SessionModel")
print("\n🔧 Available Utilities:")
print("  - session: Database session")
print("  - datetime, uuid: Python utilities")
print("\n✨ Generic ORM Functions:")
print("  all(Model)              # Get all records")
print("  find(Model, id)         # Find by ID")
print("  first(Model)            # Get first record")
print("  count(Model)            # Count records")
print("  create(Model, **kwargs) # Create new record")
print("  save(instance)          # Save/update record")
print("  delete(instance)        # Delete record")
print("\n🎯 Model Static Methods:")
print("  Model.all()             # Get all records")
print("  Model.find(id)          # Find by ID")
print("  Model.first()           # Get first record")
print("  Model.count()           # Count records")
print("  Model.create(**kwargs)  # Create new record")
print("=" * 60)
print()

# Start interactive shell
import code
code.interact(local=locals(), banner="")

# ============================================================================
# EXAMPLES - Run these in the shell:
# ============================================================================
#
# # Get all users
# users = all(User)
# # or
# users = User.all()
#
# # Find user by ID
# user = find(User, uuid.UUID('some-uuid-here'))
# # or
# user = User.find(uuid.UUID('some-uuid-here'))
#
# # Get first user
# first_user = first(User)
# # or
# first_user = User.first()
#
# # Count users
# user_count = count(User)
# # or
# user_count = User.count()
#
# # Create a new user
# new_user = create(User, name='John', email='john@example.com', hashed_password='hashed')
# # or
# new_user = User.create(name='John', email='john@example.com', hashed_password='hashed')
#
# # Update a user
# user.name = 'Jane'
# save(user)
#
# # Delete a user
# delete(user)
#
# # Work with todos
# todos = Todo.all()
# todo = Todo.find(some_uuid)
# new_todo = Todo.create(title='My Todo', user_id=user.id, order=1)
#
# # Work with any model generically
# all_sessions = all(SessionModel)
# session_count = count(SessionModel)
#
# # Access session directly for advanced queries
# from sqlalchemy import select
# users = session.query(User).filter(User.email == 'test@example.com').all()
#
# ============================================================================
