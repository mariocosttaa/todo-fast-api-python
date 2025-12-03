import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

class TestRegister:
    '''Tests for Register'''
    
    def test_user_can_register_and_is_logged_in(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Testing if user can register and is automatically logged in'''

        # Act - register user
        createUserUrl = client.app.url_path_for("v1-auth-register")
        response = client.post(createUserUrl, json=fake_user_data)

        # Assert basic registration data
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == fake_user_data["email"]
        assert data["user"]["name"] == fake_user_data["name"]
        assert data["user"]["surname"] == fake_user_data["surname"]
        assert "id" in data["user"]

        # Assert auto-login: access token is returned and works with /auth/me
        assert "access_token" in data
        token = data["access_token"]

        me_url = client.app.url_path_for("v1-auth-me")
        me_response = client.get(me_url, headers={"Authorization": f"Bearer {token}"})
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == fake_user_data["email"]
        assert me_data["name"] == fake_user_data["name"]
        assert me_data["surname"] == fake_user_data["surname"]
    
    def test_register_with_duplicate_email(self, client: TestClient, test_user):
        '''Testing that duplicate email cannot be registered'''
        
        # Arrange
        user_data = {
            "name": "Jane",
            "surname": "Doe",
            "email": test_user.email,  # Use existing user's email
            "password": "password123",
            "password_confirm": "password123"
        }
        
        # Act
        createUserUrl = client.app.url_path_for("v1-auth-register")
        response = client.post(createUserUrl, json=user_data)
        
        # Assert
        assert response.status_code == 422  # Pydantic validation error
        assert "already exists" in str(response.json()).lower()
    
    def test_register_password_mismatch(self, client: TestClient, fake_user_data: dict):
        '''Testing that passwords must match'''
        
        # Arrange
        fake_user_data["password_confirm"] = "different_password"
        
        # Act
        createUserUrl = client.app.url_path_for("v1-auth-register")
        response = client.post(createUserUrl, json=fake_user_data)
        
        # Assert
        assert response.status_code == 422  # Pydantic validation error
        assert "do not match" in str(response.json()).lower()
