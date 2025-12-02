from typing import List
from sqlalchemy.orm import Session
from app.models.profile import Profile

class ProfileController:
    
    @staticmethod
    def all(session: Session) -> List[Profile]:
        return list(session.exec(select(Profile)).all())
