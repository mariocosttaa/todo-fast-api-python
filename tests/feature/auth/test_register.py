import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

class TestRegister:
    '''Tests for Register'''
    
    def test_user_can_register(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Testing if user can register'''
        
        # Arrange - fake_user_data fixture provides valid user data
        
        # Act
        response = client.post("/v1/auth/register", json=fake_user_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == fake_user_data["email"]
        assert data["user"]["name"] == fake_user_data["name"]
        assert data["user"]["surname"] == fake_user_data["surname"]
        assert "id" in data["user"]
    
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
        response = client.post("/v1/auth/register", json=user_data)
        
        # Assert
        assert response.status_code == 422  # Pydantic validation error
        assert "already exists" in str(response.json()).lower()
    
    def test_register_password_mismatch(self, client: TestClient, fake_user_data: dict):
        '''Testing that passwords must match'''
        
        # Arrange
        fake_user_data["password_confirm"] = "different_password"
        
        # Act
        response = client.post("/v1/auth/register", json=fake_user_data)
        
        # Assert
        assert response.status_code == 422  # Pydantic validation error
        assert "do not match" in str(response.json()).lower()
