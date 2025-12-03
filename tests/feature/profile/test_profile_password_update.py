from app.utilis.auth import get_password_hash
from app.models.user import User
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from pprint import pprint


class Testprofile_password_update:
    '''Tests for profile_password_update'''
    
    def test_profile_password_update(self, authenticated_client, fake_user_data: dict):
        '''Test for profile_password_update'''
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": fake_user_data["password"],
            "password": "new-password",
            "password_confirm": "new-password"
        })

        assert doProfileUpdate.status_code == 200

    def test_profile_password_update_with_different_passwords(self, authenticated_client, fake_user_data: dict):
        '''Test for profile_password_update with different passwords'''
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": fake_user_data["password"],
            "password": "1new-password",
            "password_confirm": "new-password"
        })

        assert doProfileUpdate.status_code == 422
        assert "passwords do not match" in doProfileUpdate.json()["detail"][0]["msg"]

    def test_profile_password_update_with_the_same_old_password(self, authenticated_client, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update with the same old password'''
        # Arrange
        client, token, user = authenticated_client
        oldPassword = fake_user_data["password"]
        password = fake_user_data["password"]

        #update password
        profileUrl = client.app.url_path_for("v1-profile-password-update")
        doProfileUpdate = client.put(profileUrl, headers={"Authorization": f"Bearer {token}"}, json={
            "old_password": oldPassword,
            "password": password,
            "password_confirm": password
        })

        assert doProfileUpdate.status_code == 401
        assert "New password cannot be the same as the old password" in doProfileUpdate.json()["detail"]

    def test_profile_password_update_with_old_password_incorrect(self, authenticated_client, db_session: Session, fake_user_data: dict):
        '''Test for profile_password_update with old password incorrect'''
        # Arrange
        client, token, user = authenticated_client
        old_password = fake_user_data["password"]
        password = "12345678"

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