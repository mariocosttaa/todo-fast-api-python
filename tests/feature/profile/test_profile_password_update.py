from app.utilis.auth import get_password_hash
from app.models.user import User
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pprint import pprint

class Testprofile_password_update:
    '''Tests for profile_password_update'''
    
    def test_profile_password_update(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update'''
        # Arrange
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

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": fake_user_data["password"],
            "password": "new-password",
            "password_confirm": "new-password"
        })

        assert doProfileUpdate.status_code == 200

    def test_profile_password_update_with_different_passwords(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update with different passwords'''
        # Arrange
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

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": fake_user_data["password"],
            "password": "1new-password",
            "password_confirm": "new-password"
        })

        assert doProfileUpdate.status_code == 422
        assert "passwords do not match" in doProfileUpdate.json()["detail"][0]["msg"]

    def test_profile_password_update_with_the_same_old_password(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update with the same old password'''
        # Arrange
        oldPassword = "12345678"
        password = "12345678"
        user = User(
            id=uuid.uuid4(),
            name=fake_user_data["name"],    
            surname=fake_user_data["surname"],
            email=fake_user_data["email"],
            hashed_password=get_password_hash(oldPassword)
        )
        db_session.add(user)
        db_session.commit()

        #login with user created
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin = client.post(loginUrl, json={"email": fake_user_data["email"], "password": oldPassword})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": oldPassword,
            "password": password,
            "password_confirm": password
        })

        assert doProfileUpdate.status_code == 401
        assert "New password cannot be the same as the old password" in doProfileUpdate.json()["detail"]

    def test_profile_password_update_with_old_password_incorrect(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update with old password incorrect'''
        # Arrange
        old_password = "123456789101112"
        password = "12345678"
        user = User(
            id=uuid.uuid4(),
            name=fake_user_data["name"],    
            surname=fake_user_data["surname"],
            email=fake_user_data["email"],
            hashed_password=get_password_hash(old_password)
        )
        db_session.add(user)
        db_session.commit()

        #login with user created
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin = client.post(loginUrl, json={"email": fake_user_data["email"], "password": old_password})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": "blablabla120001",
            "password": password,
            "password_confirm": password
        })

        pprint(doProfileUpdate.json())

        assert doProfileUpdate.status_code == 401
        assert "Old password is incorrect" in doProfileUpdate.json()["detail"]