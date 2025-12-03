# Automated Tests

This document covers the automated testing structure of the project, similar to Laravel with automatic rollback and Faker usage.

## Quick Reference - Commands

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestAuthLogin
```

### Run Specific Test Function
```bash
pytest tests/test_auth.py::TestAuthLogin::test_login_success
```

### Run with Detailed Output (shows print statements)
```bash
pytest -v -s
```

### Run Only Failed Tests from Last Run
```bash
pytest --lf
```

### Run Tests and Stop on First Failure
```bash
pytest -x
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Run Tests with SQL Query Logging
Edit `tests/conftest.py` and set `echo=True` in test_engine, then:
```bash
pytest -v
```

### Debug a Specific Test
```bash
pytest -s tests/test_auth.py::test_exemplo
```

## Project Structure

```markdown:systemDoc/tests.md
<code_block_to_apply_changes_from>
tests/
├── conftest.py          # Fixtures globais e configuração
├── test_auth.py         # Testes de autenticação
└── test_todos.py        # Testes de TODOs (exemplo futuro)
```

## Configuration

### Required Dependencies

The test dependencies are already in `requirements.txt`:
- `pytest` - Test framework
- `faker` - Fake data generation
- `httpx` - HTTP client for tests (already included in FastAPI)

### Configuration File

The `pytest.ini` configures test behavior:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
```

## How Automatic Rollback Works

### Concept

Each test runs within a **database transaction** that is automatically rolled back (rollback) after the test finishes. This ensures that:

1. The real database is never permanently modified
2. Each test starts with a clean database
3. Tests do not interfere with each other

### Implementation

```python
@pytest.fixture(scope="function")
def db_session():
    # Inicia uma transação
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session  # Teste roda aqui
    finally:
        # Rollback automático - reverte TUDO
        session.close()
        transaction.rollback()
        connection.close()
```

### Important: flush() vs commit()

In fixtures and tests, use **`flush()`** instead of **`commit()`**:

```python
# ✅ CORRETO - mantém na transação
db_session.add(user)
db_session.flush()
db_session.refresh(user)

# ❌ ERRADO - faz commit permanente (não será revertido)
db_session.add(user)
db_session.commit()
```

## Available Fixtures

### `db_session`

Database session with automatic rollback:

```python
def test_exemplo(db_session: Session):
    user = User(...)
    db_session.add(user)
    db_session.flush()
    # Após o teste, o rollback remove este usuário automaticamente
```

### `client`

HTTP client to test endpoints:

```python
def test_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
```

### `fake_user_data`

Fake user data generated with Faker:

```python
def test_register(client: TestClient, fake_user_data: dict):
    response = client.post("/auth/register", json=fake_user_data)
    # fake_user_data contém: name, surname, email, password, password_confirm
```

### `test_user`

User already created in the database (will be removed after the test):

```python
def test_login(client: TestClient, test_user: User, fake_user_data: dict):
    response = client.post("/auth/login", json={
        "email": fake_user_data["email"],
        "password": fake_user_data["password"]
    })
```

### `authenticated_client`

HTTP client already authenticated with a valid token:

```python
def test_protected_endpoint(authenticated_client):
    client, token, user = authenticated_client
    # client já tem o header Authorization configurado
    response = client.get("/auth/me")
    assert response.status_code == 200
```

## Best Practices

1. **Use fixtures**: Reuse `test_user`, `authenticated_client`, etc.
2. **Isolated tests**: Each test should be independent
3. **Descriptive names**: Use names that explain what is being tested
4. **Arrange-Act-Assert**: Organize tests into 3 clear parts
5. **Use `flush()` instead of `commit()`**: Keep data in the transaction
6. **Test both success and error cases**: Cover both scenarios
7. **Validate complete responses**: Check status code AND content

## Troubleshooting

### Centralized fakers

The project exposes reusable faker helpers under `app.database.faker` so you don't need to reinvent fake data in every test:

```python
from app.database.faker import (
    fake_user_data,
    make_user,
    fake_todo_data,
    make_todo,
    fake_session_data,
    make_session,
)
```

- `fake_user_data(...)` → returns a `dict` suitable for auth/profile requests. Emails are generated with a UUID suffix to avoid collisions with real data.
- `make_user(...)` → returns a `User` ORM instance (not added/committed).
- `fake_todo_data(user_id=...)` → returns a `dict` for creating TODOs, with `due_date` as timezone-aware UTC ISO string.
- `make_todo(user_id=...)` → returns a `Todo` ORM instance (not added/committed).
- `fake_session_data(...)` / `make_session(...)` → helpers for authentication sessions.

These helpers are also exposed indirectly via fixtures in `tests/conftest.py`:

- `fake_user_data` fixture → wraps `app.database.faker.fake_user_data()`
- `fake_todo_data` fixture → wraps `app.database.faker.fake_todo_data()` using the `test_user` / `authenticated_client` user.

Example usage in a feature test:

```python
def test_returning_all_todos(self, authenticated_client, fake_todo_data: dict):
    client, token, user = authenticated_client

    # create todo
    todoUrl = client.app.url_path_for("v1-todo-store")
    todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
    assert todoResponse.status_code == 200

    # get todos
    todosUrl = client.app.url_path_for("v1-todos")
    todosResponse = client.get(todosUrl, headers={"Authorization": f"Bearer {token}"})
    assert todosResponse.status_code == 200

    data = todosResponse.json()
    todo_item = data["items"][0]
    assert todo_item["title"] == fake_todo_data["title"]
```

### Code generation and faker skeletons

The `generate.py` script can create models, controllers, requests, tests, and **faker helpers** using skeleton templates located in the `skeleton/` directory.

Key commands:

- Generate model skeleton:

  ```bash
  python generate.py model Product
  ```

- Generate controller skeleton:

  ```bash
  python generate.py controller ProductController
  ```

- Generate request schema:

  ```bash
  python generate.py request RegisterRequest --fields name:str email:email password:str
  ```

- Generate test skeleton:

  ```bash
  python generate.py test AuthController --type controller
  python generate.py test AuthRouter --type router
  python generate.py test UserService --type generic
  ```

- Generate a faker helper for a model (root models only):

  ```bash
  python generate.py faker User
  ```

  This will:

  - Create `app/database/faker/user_faker.py` based on `skeleton/faker.txt`.
  - Automatically update `app/database/faker/__init__.py` to export `fake_user_data` and `make_user` for that model.

After generation you should open the new faker file and customize the fields inside `fake_<model>_data()` using `fake.<something>()` to match your domain model.

### Error: "DATABASE_URL not set"

Ensure that the test database environment variables are configured (see `docs/testing.md` for DB setup details).
