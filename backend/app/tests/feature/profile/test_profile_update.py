import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from pprint import pprint
from uuid import uuid4
from app.utilis.auth import get_password_hash

class Testprofile_update:
    '''Tests for profile_update'''
    
    def test_profile_update(self, authenticated_client):
        '''Test for profile update'''
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #update profile
        profileUrl = client.app.url_path_for("v1-profile-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "name": "new name", 
            "surname": "new surname",
            "email": "new email"
        })
        assert doProfileUpdate.status_code == 200

        #check if profile was updated
        meUrl = client.app.url_path_for("v1-auth-me")
        doUserMe= client.get(meUrl, headers={"Authorization": f"Bearer {token}"})
        assert doUserMe.status_code == 200
        assert doUserMe.json()["name"] == "new name"
        assert doUserMe.json()["surname"] == "new surname"

    def test_profile_update_with_existent_email(self, authenticated_client, db_session: Session):
        '''Test for profile update with existent email'''
        # authenticated user (user1)
        client, token, user1 = authenticated_client

        # create another user with an email that will be used in update
        user2 = User(
            id=uuid4(),
            name="Other",
            surname="User",
            email="email-2@example.com",
            hashed_password=get_password_hash("password"),
        )
        db_session.add(user2)
        db_session.flush()

        # update profile with the existent email from user2
        profileUrl = client.app.url_path_for("v1-profile-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "name": "new name", 
            "surname": "new surname",
            "email": "email-2@example.com"
        })
        
        assert doProfileUpdate.status_code == 401
        assert "Email already exists" in doProfileUpdate.json()["detail"]
