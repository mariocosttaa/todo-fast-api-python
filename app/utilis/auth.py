from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
import bcrypt
from fastapi import HTTPException, status, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.models.session import Session as SessionModel
from app.models.user import User
from uuid import UUID
import os

# JWT settings - should be in environment variables
SECRET_KEY = os.getenv("APP_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
SESSION_EXPIRE_DAYS = 7  # Session expiration in days

# Security scheme for token extraction
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Truncate password to 72 bytes if necessary (bcrypt limit)
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    try:
        # Handle both string and bytes for hashed_password
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash a password with bcrypt (max 72 bytes)"""
    # Bcrypt has a 72-byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token, checks session in database, and validates expiration.
    """
    token = credentials.credentials
    
    # Verify JWT token
    payload = verify_token(token, token_type="access")
    user_id_str = payload.get("sub")
    
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Convert string to UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )
    
    # Check if session exists in database
    db_session = db.query(SessionModel).filter(
        SessionModel.token == token,
        SessionModel.user_id == user_id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )
    
    # Check session expiration (based on last_used_at or created_at)
    now = datetime.utcnow()
    expiration_time = db_session.last_used_at or db_session.created_at
    
    # Convert timezone-aware datetime to naive for comparison
    if expiration_time.tzinfo is not None:
        expiration_time = expiration_time.replace(tzinfo=None)
    
    # Calculate time difference
    time_diff = now - expiration_time
    
    if time_diff.days >= SESSION_EXPIRE_DAYS:
        # Session expired - delete it
        db.delete(db_session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session has expired"
        )
    
    # Update last_used_at (database will handle timezone conversion)
    db_session.last_used_at = now
    db.commit()
    
    # Get and return user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user