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

### Error: "DATABASE_URL not set"

Ensure that the
