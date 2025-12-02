import uuid
from app.utilis.auth import get_password_hash
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User
from pprint import pprint

class Testprofile_update:
    '''Tests for profile_update'''
    
    def test_profile_update(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile update'''
        # Arrange
        #create user
        password = get_password_hash(fake_user_data["password"])
        user = User(
            id=uuid.uuid4(),
            name=fake_user_data["name"],
            surname=fake_user_data["surname"],
            email=fake_user_data["email"],
            hashed_password=password
        )
        db_session.add(user)
        db_session.commit()

        #login with user created
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin = client.post(loginUrl, json={"email": fake_user_data["email"], "password": fake_user_data["password"]})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

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

    def test_profile_update_with_existent_email(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile update with existent email'''
        #create user
        password = get_password_hash(fake_user_data["password"])
        user1 = User(
            id=uuid.uuid4(),
            name=fake_user_data["name"],
            surname=fake_user_data["surname"],
            email='email-1@example.com',
            hashed_password=password
        )
        user2 = User(
            id=uuid.uuid4(),
            name=fake_user_data["name"],
            surname=fake_user_data["surname"],
            email='email-2@example.com',
            hashed_password=password
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()

        #login with user 1 created
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin = client.post(loginUrl, json={"email": user1.email, "password": fake_user_data["password"]})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

        #update profile with the exisitent email
        profileUrl = client.app.url_path_for("v1-profile-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "name": "new name", 
            "surname": "new surname",
            "email": "email-2@example.com"
        })
        assert doProfileUpdate.status_code == 401
        assert "Email already exists" in doProfileUpdate.json()["detail"]
