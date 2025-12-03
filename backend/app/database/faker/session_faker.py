from datetime import datetime
from uuid import uuid4

from app.models.session import Session
from app.utilis.auth import create_access_token


def fake_session_data(*, user_id) -> dict:
    """
    Dados para criar uma sessão (por exemplo seed ou payload futuro).
    """
    token = create_access_token(data={"sub": str(user_id)})
    return {
        "user_id": str(user_id),
        "token": token,
    }


def make_session(
    *,
    user_id,
    id=None,
    token=None,
    last_used_at=None,
) -> Session:
    """
    Cria instância de Session (não adiciona nem comita).
    """
    if id is None:
        id = uuid4()
    if token is None:
        token = create_access_token(data={"sub": str(user_id)})
    if last_used_at is None:
        last_used_at = datetime.utcnow()

    return Session(
        id=id,
        user_id=user_id,
        token=token,
        last_used_at=last_used_at,
    )