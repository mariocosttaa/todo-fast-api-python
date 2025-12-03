import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.main import app
from app.database.base import Base, get_db
from app.models.user import User
from app.models.session import Session as SessionModel
from app.utilis.auth import get_password_hash
from app.database.faker import fake_user_data as faker_fake_user_data, fake_todo_data as faker_fake_todo_data, make_session
from uuid import uuid4
import os
from dotenv import load_dotenv
from pathlib import Path

# Carregar variáveis de ambiente
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Usar o mesmo banco de dados real, mas com uma conexão separada para testes
TEST_DATABASE_URL = os.getenv("DATABASE_URL")

if not TEST_DATABASE_URL:
    # Construir DATABASE_URL se não existir
    postgres_user = os.getenv("POSTGRES_USER")
    postgres_password = os.getenv("POSTGRES_PASSWORD")
    postgres_db = os.getenv("POSTGRES_DB")
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    
    if postgres_user and postgres_password and postgres_db:
        TEST_DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:5432/{postgres_db}"

if not TEST_DATABASE_URL:
    raise ValueError("DATABASE_URL or POSTGRES_* environment variables must be set for tests")

# Engine para testes (conexão separada do banco real)
test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True para ver SQL queries nos testes
    pool_pre_ping=True,  # Verifica conexões antes de usar
)

# SessionLocal para testes
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Cria uma sessão de banco de dados para cada teste no banco REAL.
    Usa transações com rollback automático (similar ao Laravel DatabaseTransactions).
    
    IMPORTANTE: Cada teste roda em uma transação que é revertida ao final,
    então o banco de dados real nunca é modificado permanentemente.
    """
    from app.database.db_helper import set_test_session
    
    # Criar uma conexão e iniciar uma transação
    connection = test_engine.connect()
    transaction = connection.begin()
    
    # Criar sessão vinculada à transação
    # Isso garante que tudo que acontecer nesta sessão será revertido
    session = TestingSessionLocal(bind=connection)
    
    # Inject test session into db_helper so validators can use it
    set_test_session(session)
    
    try:
        yield session
    finally:
        # Clear test session from db_helper
        set_test_session(None)
        
        # Rollback automático após o teste
        # Isso reverte TODAS as mudanças feitas durante o teste
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Cria um TestClient do FastAPI com override do get_db.
    Cada teste recebe um cliente isolado com rollback automático.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            # Não fazemos commit aqui, o rollback é feito no db_session fixture
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Limpar override após o teste
    app.dependency_overrides.clear()


@pytest.fixture
def fake_user_data():
    """Gera dados fake de usuário usando Faker"""
    return faker_fake_user_data()


@pytest.fixture
def fake_todo_data(test_user: User):
    """Gera dados fake de todo usando faker centralizado"""
    return faker_fake_todo_data(user_id=test_user.id)


@pytest.fixture
def test_user(db_session: Session, fake_user_data: dict):
    """
    Cria um usuário de teste no banco.
    Útil para testes que precisam de um usuário já cadastrado.
    O rollback automático remove este usuário após o teste.
    """
    user = User(
        id=uuid4(),
        name=fake_user_data["name"],
        surname=fake_user_data["surname"],
        email=fake_user_data["email"],
        hashed_password=get_password_hash(fake_user_data["password"])
    )
    db_session.add(user)
    db_session.flush()  # Usa flush ao invés de commit para manter na transação
    db_session.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User, db_session: Session):
    """
    Cria um cliente autenticado com token válido.
    Retorna (client, token, user) para facilitar o uso nos testes.
    """
    from app.utilis.auth import create_access_token
    from datetime import datetime
    
    # Criar token
    token = create_access_token(data={"sub": str(test_user.id)})
    
    # Criar sessão no banco
    session = make_session(user_id=test_user.id, token=token)
    db_session.add(session)
    db_session.flush()  # Usa flush para manter na transação
    
    # Adicionar token ao cliente
    client.headers.update({"Authorization": f"Bearer {token}"})
    
    return client, token, test_user
