from app.requests.auth.register_request import RegisterRequest
from app.requests.auth.login_request import LoginRequest
from app.utilis.auth import get_current_user, get_current_session
from app.models.user import User
from app.models.session import Session as SessionModel
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.auth_controller import AuthController
from app.database.base import get_db

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

# Exemplo de rota protegida - mostra como usar o usuário logado
@router.get("/auth/me", name="v1-auth-me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "surname": current_user.surname,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }