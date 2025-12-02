# Testing Guide

## Overview

This project uses pytest for testing with automatic database transaction rollback, ensuring test isolation without persisting data to the database.

## How It Works

### Database Helper Pattern

The testing infrastructure uses a **database helper pattern** that allows the same code to work in both production and tests:

```python
# app/database/db_helper.py
from app.database.db_helper import get_db_session

# In validators, controllers, or anywhere you need DB access:
with get_db_session() as session:
    user = session.query(User).filter(User.email == email).first()
```

**In Production:**
- `get_db_session()` creates a new database session from `SessionLocal()`
- Each request gets its own session
- Sessions are automatically closed after use

**In Tests:**
- `get_db_session()` uses the injected test session
- All operations participate in the test transaction
- Everything is rolled back after each test

### Transaction Rollback

Each test runs in its own transaction that is automatically rolled back:

1. Test starts → Create connection and begin transaction
2. Test runs → All DB operations use this transaction
3. Test ends → Rollback transaction (nothing persists)

This is similar to Laravel's `DatabaseTransactions` trait.

## Writing Tests

### Basic Test Structure

```python
def test_example(client: TestClient, db_session: Session):
    """Test with automatic rollback"""
    # Create test data
    user = User(id=uuid4(), email="test@example.com", ...)
    db_session.add(user)
    db_session.flush()  # Make visible in this transaction
    
    # Make API request
    response = client.post("/api/endpoint", json={...})
    
    # Assert results
    assert response.status_code == 200
    
    # No cleanup needed - automatic rollback!
```

### Available Fixtures

#### `db_session`
Provides a database session with automatic rollback.

```python
def test_with_db(db_session: Session):
    user = User(...)
    db_session.add(user)
    db_session.flush()
    # ... test logic ...
```

#### `client`
Provides a FastAPI TestClient with the test database session injected.

```python
def test_api(client: TestClient):
    response = client.post("/auth/register", json={...})
    assert response.status_code == 200
```

#### `test_user`
Creates a test user in the database (automatically rolled back).

```python
def test_with_user(test_user: User):
    assert test_user.email is not None
```

#### `authenticated_client`
Provides a client with authentication token and user.

```python
def test_protected_endpoint(authenticated_client):
    client, token, user = authenticated_client
    response = client.get("/auth/me")
    assert response.status_code == 200
```

#### `fake_user_data`
Generates fake user data using Faker.

```python
def test_registration(client: TestClient, fake_user_data: dict):
    response = client.post("/auth/register", json=fake_user_data)
    assert response.status_code == 200
```

## Best Practices

### ✅ DO

1. **Use `db.flush()` instead of `db.commit()` in application code**
   ```python
   db.add(user)
   db.flush()  # Flushes to DB but doesn't commit
   db.refresh(user)
   ```
   FastAPI will automatically commit when the request completes successfully.

2. **Use `get_db_session()` for database access in validators**
   ```python
   @validator('email')
   def validate_email(cls, v):
       with get_db_session() as session:
           user = session.query(User).filter(User.email == v).first()
           if user:
               raise ValueError("Email already exists")
       return v
   ```

3. **Use test fixtures for common setup**
   ```python
   def test_login(client: TestClient, test_user: User):
       # test_user is automatically created and will be rolled back
       response = client.post("/auth/login", json={...})
   ```

### ❌ DON'T

1. **Don't use `SessionLocal()` directly in application code**
   ```python
   # ❌ BAD - bypasses test transaction
   with SessionLocal() as session:
       user = session.query(User).first()
   
   # ✅ GOOD - participates in test transaction
   with get_db_session() as session:
       user = session.query(User).first()
   ```

2. **Don't call `db.commit()` in controllers**
   ```python
   # ❌ BAD - breaks test rollback
   db.add(user)
   db.commit()
   
   # ✅ GOOD - allows test rollback
   db.add(user)
   db.flush()
   ```

3. **Don't manually clean up test data**
   ```python
   # ❌ BAD - unnecessary, automatic rollback handles this
   def test_example(db_session):
       user = User(...)
       db_session.add(user)
       db_session.flush()
       # ... test ...
       db_session.delete(user)  # Not needed!
   
   # ✅ GOOD - let rollback handle cleanup
   def test_example(db_session):
       user = User(...)
       db_session.add(user)
       db_session.flush()
       # ... test ...
       # Automatic rollback!
   ```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test class or method
```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_success
```

### Run tests multiple times (verify isolation)
```bash
pytest tests/test_auth.py --count=3
```

## Database Setup

Tests require a PostgreSQL database to be running. You can start it with Docker:

```bash
docker-compose up -d db
```

Or configure your own PostgreSQL instance and update the `.env` file:

```env
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
POSTGRES_HOST=localhost
```

## Troubleshooting

### Tests fail with "Connection refused"
The database isn't running. Start it with `docker-compose up -d db`.

### Tests fail with "User already exists"
Test isolation is broken. Check that:
1. All DB access uses `get_db_session()` instead of `SessionLocal()`
2. Controllers use `db.flush()` instead of `db.commit()`
3. Test fixtures properly inject the test session

### Validators don't see test data
Make sure validators use `get_db_session()` instead of `SessionLocal()`.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Test Fixture                      │
│  - Creates connection & transaction                 │
│  - Injects test session via set_test_session()     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Database Helper                        │
│  get_db_session():                                  │
│    if _test_session:                                │
│      yield _test_session  ← Test uses this          │
│    else:                                            │
│      yield SessionLocal() ← Production uses this    │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│         Validators & Controllers                    │
│  with get_db_session() as session:                  │
│    # DB operations participate in test transaction  │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              Test Cleanup                           │
│  - set_test_session(None)                           │
│  - transaction.rollback()                           │
│  - All changes reverted!                            │
└─────────────────────────────────────────────────────┘
```
