from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.database.faker.base import fake
from app.models.todo import Todo


def fake_todo_data(
    *,
    user_id,
    title=None,
    description=None,
    is_completed=False,
    priority="low",
    with_due_date=True,
) -> dict:
    """
    Dados para criar um TODO via payload.
    """
    if title is None:
        title = fake.sentence(nb_words=4)
    if description is None:
        description = fake.text(max_nb_chars=120)

    data = {
        "user_id": str(user_id),
        "title": title,
        "description": description,
        "is_completed": is_completed,
        "priority": priority,
    }

    if with_due_date:
        due = datetime.now(timezone.utc) + timedelta(days=3)
        data["due_date"] = due.isoformat()

    return data


def make_todo(
    *,
    user_id,
    id=None,
    order=0,
    title=None,
    description=None,
    is_completed=False,
    priority="low",
    due_date=None,
) -> Todo:
    """
    Cria instância de Todo (não adiciona nem comita).
    """
    if id is None:
        id = uuid4()
    if title is None:
        title = fake.sentence(nb_words=4)
    if description is None:
        description = fake.text(max_nb_chars=120)

    if due_date is None:
        # manter consistente com fake_todo_data: datetime aware em UTC
        due_date = datetime.now(timezone.utc) + timedelta(days=3)

    return Todo(
        id=id,
        order=order,
        user_id=user_id,
        title=title,
        description=description,
        is_completed=is_completed,
        due_date=due_date,
        priority=priority,
    )