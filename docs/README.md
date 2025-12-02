# System Documentation

This directory contains technical documentation for the FastAPI Todo application.

## Documentation Files

### [database-access.md](./database-access.md)
**Database Access Guide** - How to properly access the database in the application.

**Topics covered:**
- Database helper pattern (`get_db_session()`)
- Where to use database access (validators, controllers, services)
- Common patterns (CRUD operations)
- Best practices and anti-patterns
- Transaction management
- Performance tips
- Migration guide

**Key takeaway:** Always use `get_db_session()` in validators/utilities and dependency injection in controllers. Use `db.flush()` instead of `db.commit()`.

---

### [testing.md](./testing.md)
**Testing Guide** - How to write and run tests with automatic database rollback.

**Topics covered:**
- How the database helper pattern works in tests
- Transaction rollback mechanism
- Writing tests with available fixtures
- Best practices for test isolation
- Running tests
- Troubleshooting common issues
- Testing architecture

**Key takeaway:** Tests automatically rollback all database changes. Use `get_db_session()` to ensure validators work in tests.

---

### [alembic.md](./alembic.md)
**Database Migrations** - How to manage database schema changes with Alembic.

---

### [manage.md](./manage.md)
**Management Commands** - CLI commands for managing the application.

---

### [tests.md](./tests.md) *(Legacy)*
**Legacy Testing Documentation** - Older testing documentation. See `testing.md` for current best practices.

---

## Quick Reference

### Database Access

```python
# In validators, utilities, background tasks
from app.database.db_helper import get_db_session

with get_db_session() as session:
    user = session.query(User).filter(User.email == email).first()
```

```python
# In controllers (dependency injection)
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.base import get_db

def handler(db: Session = Depends(get_db)):
    user = db.query(User).first()
    db.add(user)
    db.flush()  # Not commit!
    db.refresh(user)
```

### Testing

```python
# Test with automatic rollback
def test_example(client: TestClient, db_session: Session):
    user = User(id=uuid4(), email="test@example.com")
    db_session.add(user)
    db_session.flush()
    
    response = client.post("/api/endpoint", json={...})
    assert response.status_code == 200
    # Automatic rollback - no cleanup needed!
```

### Running Tests

```bash
# Start database
docker-compose up -d db

# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest --cov=app tests/
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         Application Layer               │
│  - Controllers (dependency injection)   │
│  - Validators (get_db_session)          │
│  - Services (both methods)              │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         Database Helper                 │
│  Production: SessionLocal()             │
│  Tests: Injected test session           │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│         PostgreSQL Database             │
│  Production: Commits on success         │
│  Tests: Rollback after each test        │
└─────────────────────────────────────────┘
```

## Contributing

When adding new features:

1. **Use the database helper pattern** - See `database-access.md`
2. **Write tests** - See `testing.md`
3. **Create migrations** - See `alembic.md`
4. **Update documentation** - Keep these docs current

## Getting Help

- **Database access issues?** → Read `database-access.md`
- **Tests not working?** → Read `testing.md`
- **Migration problems?** → Read `alembic.md`
- **CLI commands?** → Read `manage.md`
