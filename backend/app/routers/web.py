from app.controllers.todo_controller import TodoController
from app.requests.auth.register_request import RegisterRequest
from app.requests.auth.login_request import LoginRequest
from app.requests.todo.todo_create_request import TodoCreateRequest
from app.requests.todo.todo_update_request import TodoUpdateRequest
from app.utilis.auth import get_current_user, get_current_session
from app.models.user import User
from app.models.session import Session as SessionModel
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.controllers.auth_controller import AuthController
from app.database.base import get_db
from app.controllers.profile_controller import ProfileController
from app.requests.profile.profile_update_request import ProfileUpdateRequest
from app.requests.profile.profile_password_update_request import ProfilePasswordUpdateRequest
from app.requests.todo.todo_update_request import TodoUpdateRequest
from app.requests.todo.todo_index_request import TodoIndexRequest
from typing import Optional
import uuid

router = APIRouter()

# Auth endpoints
@router.post("/auth/login", name="v1-auth-login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthController.login(db, request.email, request.password)

@router.post('/auth/register', name="v1-auth-register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthController.register(db, request.name,  request.surname, request.email, request.password, request.password_confirm)

@router.delete('/auth/logout', name="v1-auth-logout")
def logout(current_user: User = Depends(get_current_user), current_session: SessionModel = Depends(get_current_session), db: Session = Depends(get_db)):
    return AuthController.logout(db, current_user, current_session)

#profile
@router.get("/auth/me", name="v1-auth-me")
def get_me(current_user: User = Depends(get_current_user)):
    return ProfileController.get_me(current_user)

@router.put("/profile/update", name="v1-profile-update")
def update_profile(request: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProfileController.update(current_user, request.name, request.surname, request.email, db)

@router.put("/profile/password/update", name="v1-profile-password-update")
def update_password(request: ProfilePasswordUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return ProfileController.update_password(current_user, request.old_password, request.password, request.password_confirm, db)

#todos
@router.get("/todos", name="v1-todos")
def index(request: TodoIndexRequest =  Depends(), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.index(current_user, db, request.page, request.page_size, request.search, request.completed, request.due_date, request.priority)

@router.get("/todos/today", name="v1-todos-today")
def today(priority: Optional[str] = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.today(current_user, db, priority)

@router.post("/todo/create", name="v1-todo-store")
def store(request: TodoCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.store(current_user, db, request.title, request.description, request.priority, request.due_date)

@router.put("/todo/update/{id}", name="v1-todo-update")
def update(id: uuid.UUID, request: TodoUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.update(current_user, db, id, request.title, request.description, request.priority, request.due_date)

@router.delete("/todo/delete/{id}", name="v1-todo-destroy")
def destroy(id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.destroy(current_user, db, id)

@router.put("/todo/order-update/{id}", name="v1-todo-order-update")
def update_order(id: uuid.UUID, order: int = Body(...,embed=True), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.update_order(current_user, db, id, order)

@router.put("/todo/completed/{id}", name="v1-todo-completed-update")
def update_completed(id: uuid.UUID, is_completed: bool = Body(...,embed=True), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return TodoController.update_completed(current_user, db, id, is_completed)
    