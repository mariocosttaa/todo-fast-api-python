from app.requests.auth.register_request import RegisterRequest
from app.requests.auth.login_request import LoginRequest
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.controllers.auth_controller import AuthController
from app.database.base import get_db

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "API ToDo - FastAPI (esqueleto)"}

@router.get("/health")
def health_check():
    return {"status": "ok"}

# auth
@router.post("/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    return AuthController.login(db, request.email, request.password)

@router.post('/auth/register')
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    return AuthController.register(db, request.name,  request.surname, request.email, request.password, request.password_confirm)