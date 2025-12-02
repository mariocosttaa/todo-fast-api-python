# Database Access Guide

## Overview

This document explains how to properly access the database in the application to ensure compatibility with both production and testing environments.

## The Database Helper Pattern

### Core Concept

The application uses a **database helper pattern** that provides a unified way to access the database:

```python
from app.database.db_helper import get_db_session

with get_db_session() as session:
    # Your database operations here
    user = session.query(User).filter(User.email == email).first()
```

### How It Works

**In Production:**
- Creates a new database session from `SessionLocal()`
- Automatically closes the session when done
- Each request gets its own isolated session

**In Tests:**
- Uses the injected test session
- All operations participate in the test transaction
- Automatic rollback ensures no data persists

## Where to Use Database Access

### 1. Request Validators (Pydantic)

Use `get_db_session()` in Pydantic validators that need database access:

```python
from pydantic import BaseModel, validator
from app.database.db_helper import get_db_session
from app.models.user import User

class LoginRequest(BaseModel):
    email: str
    password: str
    
    @validator('email')
    def validate_email(cls, v) -> str:
        with get_db_session() as session:
            user = session.query(User).filter(User.email == v).first()
            if not user:
                raise ValueError("User not found")
        return v
```

**✅ Benefits:**
- Works in both production and tests
- Participates in test transactions
- Automatic session management

### 2. Controllers

Controllers receive the database session via dependency injection:

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.base import get_db

class UserController:
    @staticmethod
    def get_user(user_id: str, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
```

**Important:** Use `db.flush()` instead of `db.commit()`:

```python
# ❌ DON'T DO THIS
db.add(user)
db.commit()  # Breaks test rollback!

# ✅ DO THIS
db.add(user)
db.flush()  # Flushes to DB but allows rollback
db.refresh(user)
```

FastAPI will automatically commit when the request completes successfully.

### 3. Services

Services can use either dependency injection or `get_db_session()`:

**Option A: Dependency Injection (Recommended for route handlers)**
```python
class UserService:
    @staticmethod
    def create_user(data: dict, db: Session):
        user = User(**data)
        db.add(user)
        db.flush()
        db.refresh(user)
        return user
```

**Option B: get_db_session() (For background tasks, validators, utilities)**
```python
from app.database.db_helper import get_db_session

class EmailService:
    @staticmethod
    def send_welcome_email(user_id: str):
        with get_db_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            # Send email logic...
```

### 4. Background Tasks

Use `get_db_session()` for background tasks:

```python
from fastapi import BackgroundTasks
from app.database.db_helper import get_db_session

def process_data(item_id: str):
    with get_db_session() as session:
        item = session.query(Item).filter(Item.id == item_id).first()
        # Process item...
        session.flush()

@app.post("/items/")
def create_item(background_tasks: BackgroundTasks):
    background_tasks.add_task(process_data, item_id)
    return {"status": "processing"}
```

## Common Patterns

### Creating Records

```python
from uuid import uuid4

def create_user(db: Session, email: str, password: str):
    user = User(
        id=uuid4(),
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(user)
    db.flush()  # ✅ Use flush, not commit
    db.refresh(user)
    return user
```

### Querying Records

```python
# Single record
user = db.query(User).filter(User.email == email).first()

# Multiple records
users = db.query(User).filter(User.is_active == True).all()

# With joins
from sqlalchemy.orm import joinedload

user = db.query(User)\
    .options(joinedload(User.sessions))\
    .filter(User.id == user_id)\
    .first()
```

### Updating Records

```python
user = db.query(User).filter(User.id == user_id).first()
user.name = "New Name"
db.flush()  # ✅ Use flush, not commit
db.refresh(user)
```

### Deleting Records

```python
user = db.query(User).filter(User.id == user_id).first()
db.delete(user)
db.flush()  # ✅ Use flush, not commit
```

## Best Practices

### ✅ DO

1. **Use `get_db_session()` in validators and utilities**
   ```python
   with get_db_session() as session:
       # Database operations
   ```

2. **Use dependency injection in controllers**
   ```python
   def handler(db: Session = Depends(get_db)):
       # Database operations
   ```

3. **Use `db.flush()` instead of `db.commit()`**
   ```python
   db.add(record)
   db.flush()
   db.refresh(record)
   ```

4. **Close sessions properly**
   - `get_db_session()` handles this automatically with context manager
   - Dependency injection handles this automatically

### ❌ DON'T

1. **Don't use `SessionLocal()` directly**
   ```python
   # ❌ BAD
   from app.database.base import SessionLocal
   with SessionLocal() as session:
       # This bypasses test transactions!
   ```

2. **Don't call `db.commit()` in application code**
   ```python
   # ❌ BAD
   db.add(user)
   db.commit()  # Breaks test rollback
   ```

3. **Don't forget to refresh after flush**
   ```python
   # ❌ BAD
   db.add(user)
   db.flush()
   # user.id is None!
   
   # ✅ GOOD
   db.add(user)
   db.flush()
   db.refresh(user)
   # user.id is populated
   ```

## Transaction Management

### Automatic Commits (Production)

FastAPI automatically commits the transaction when:
- The request handler completes successfully
- No exceptions are raised

FastAPI automatically rolls back when:
- An exception is raised
- The request handler fails

### Manual Transaction Control (Advanced)

If you need explicit transaction control:

```python
from sqlalchemy.orm import Session

def complex_operation(db: Session):
    try:
        # Multiple operations
        db.add(user)
        db.flush()
        
        db.add(profile)
        db.flush()
        
        # All good - FastAPI will commit
    except Exception as e:
        # FastAPI will rollback automatically
        raise
```

## Error Handling

### Database Errors

```python
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

def create_user(db: Session, email: str):
    try:
        user = User(email=email)
        db.add(user)
        db.flush()
        db.refresh(user)
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
```

### Not Found Errors

```python
def get_user(db: Session, user_id: str):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user
```

## Performance Tips

### 1. Use Eager Loading

Avoid N+1 queries by using `joinedload`:

```python
from sqlalchemy.orm import joinedload

# ❌ BAD - N+1 queries
users = db.query(User).all()
for user in users:
    print(user.sessions)  # Separate query for each user!

# ✅ GOOD - Single query
users = db.query(User)\
    .options(joinedload(User.sessions))\
    .all()
for user in users:
    print(user.sessions)  # Already loaded!
```

### 2. Use Pagination

```python
def get_users(db: Session, page: int = 1, per_page: int = 20):
    offset = (page - 1) * per_page
    users = db.query(User)\
        .offset(offset)\
        .limit(per_page)\
        .all()
    return users
```

### 3. Use Select Specific Columns

```python
# ❌ BAD - Loads entire object
emails = [user.email for user in db.query(User).all()]

# ✅ GOOD - Only loads email column
emails = [email for (email,) in db.query(User.email).all()]
```

## Migration to Database Helper

If you have existing code using `SessionLocal()`, migrate it:

### Before
```python
from app.database.base import SessionLocal

with SessionLocal() as session:
    user = session.query(User).first()
```

### After
```python
from app.database.db_helper import get_db_session

with get_db_session() as session:
    user = session.query(User).first()
```

That's it! Just change the import and function name.

## Summary

| Context | Method | Example |
|---------|--------|---------|
| Validators | `get_db_session()` | `with get_db_session() as session:` |
| Controllers | Dependency Injection | `db: Session = Depends(get_db)` |
| Services (routes) | Dependency Injection | `db: Session` parameter |
| Services (utilities) | `get_db_session()` | `with get_db_session() as session:` |
| Background Tasks | `get_db_session()` | `with get_db_session() as session:` |
| Commits | **Never** | Use `db.flush()` instead |

Following these patterns ensures your code works correctly in both production and testing environments!
