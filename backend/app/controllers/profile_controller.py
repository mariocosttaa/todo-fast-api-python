from app.utilis.auth import verify_password
from app.utilis.auth import get_password_hash
from app.models.user import User
from app.utilis.logger import get_logger
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException

logger = get_logger(__name__)

class ProfileController:
    
    @staticmethod
    def get_me(current_user: User) -> object:
        return {
            "id": str(current_user.id),
            "name": current_user.name,
            "surname": current_user.surname,
            "email": current_user.email,
        }

    @staticmethod
    def update(currenct_user: User, name: str, surname: str, email: str, db: Session) -> object:
        try:
            if email != currenct_user.email:
                searchEmail = db.query(User).filter(User.email == email).first()
                if searchEmail:
                    raise HTTPException(status_code=401, detail="Email already exists")
               
            user = {
                "name": name,
                "surname": surname,
                "email": email
            }
            db.query(User).filter(User.id == currenct_user.id).update(user)
            db.flush()
            
            return {
                "message": "Profile updated successfully",
            }
            
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Update profile error for user {currenct_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to update your profile")

    @staticmethod
    def update_password(current_user: User, old_password: str, password: str, password_confirm: str, db: Session) -> object:
        try:
            if verify_password(old_password, current_user.hashed_password) == False:
                raise HTTPException(status_code=401, detail="Old password is incorrect")
            
            if verify_password(password, current_user.hashed_password) == True:
                raise HTTPException(status_code=401, detail="New password cannot be the same as the old password")

            newPasswordHash = get_password_hash(password)
            user = {
                "hashed_password": newPasswordHash
            }
            db.query(User).filter(User.id == current_user.id).update(user)
            db.flush()
            
            return {
                "message": "Password updated successfully",
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error(f"Update password error for user {current_user.id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="We found some issue trying to update your password")