import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

class Testlogin:
    '''Tests for login'''
    
    def test_user_can_login(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test User Login'''

        #create user
        createUserUrl = client.app.url_path_for("v1-auth-register")
        doUserRegistration= client.post(createUserUrl, json=fake_user_data)
        assert doUserRegistration.status_code == 200

        #login create user
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin= client.post(loginUrl, json={"email": fake_user_data["email"], "password": fake_user_data["password"]})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

        # check if user was loggin
        meUrl = client.app.url_path_for("v1-auth-me")
        doUserMe= client.get(meUrl, headers={"Authorization": f"Bearer {token}"})
        assert doUserMe.status_code == 200

        #check return response if return the values of user loggin
        assert doUserMe.json()["email"] == fake_user_data["email"]  
        assert doUserMe.json()["name"] == fake_user_data["name"]
        assert doUserMe.json()["surname"] == fake_user_data["surname"]

    def test_user_can_logout(self, client: TestClient, db_session: Session, fake_user_data: dict):
        '''Test User Logout'''

        #create user
        createUserUrl = client.app.url_path_for("v1-auth-register")
        doUserRegistration = client.post(createUserUrl, json=fake_user_data)
        assert doUserRegistration.status_code == 200

        #login with user created
        loginUrl = client.app.url_path_for("v1-auth-login")
        doUserLogin = client.post(loginUrl, json={"email": fake_user_data["email"], "password": fake_user_data["password"]})
        assert doUserLogin.status_code == 200
        token = doUserLogin.json()["access_token"]

        #logout user
        logoutUrl = client.app.url_path_for("v1-auth-logout")
        doUserLogout = client.delete(logoutUrl, headers={"Authorization": f"Bearer {token}"})
        assert doUserLogout.status_code == 200

        #try to access protected route
        meUrl = client.app.url_path_for("v1-auth-me")
        doUserMe= client.get(meUrl, headers={"Authorization": f"Bearer {token}"})
        assert doUserMe.status_code == 401
        

        