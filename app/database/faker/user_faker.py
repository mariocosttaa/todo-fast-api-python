from uuid import uuid4

from app.database.faker.base import fake
from app.models.user import User
from app.utilis.auth import get_password_hash


def fake_user_data(
    password: str = "TestPassword123!",
    with_confirm: bool = True,
) -> dict:
    """
    Retorna um dict com dados de usuário para payloads de request.
    Se with_confirm=True, inclui password_confirm.
    """
    # Garantir e-mails praticamente únicos para não colidir com dados reais no banco
    # mesmo quando reutilizando o mesmo DB entre execuções de teste.
    email_local = fake.user_name()
    unique_suffix = uuid4().hex[:8]
    email = f"{email_local}.{unique_suffix}@example.com"

    data = {
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "email": email,
        "password": password,
    }
    if with_confirm:
        data["password_confirm"] = password
    return data


def make_user(
    *,
    id=None,
    name=None,
    surname=None,
    email=None,
    password: str = "TestPassword123!",
) -> User:
    """
    Cria uma instância de User (não adiciona nem comita).
    """
    if id is None:
        id = uuid4()

    if name is None or surname is None or email is None:
        # Usa fake_user_data para garantir consistência
        payload = fake_user_data(password=password, with_confirm=False)
        name = name or payload["name"]
        surname = surname or payload["surname"]
        email = email or payload["email"]

    return User(
        id=id,
        name=name,
        surname=surname,
        email=email,
        hashed_password=get_password_hash(password),
    )