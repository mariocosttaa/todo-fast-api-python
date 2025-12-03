import pprint
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

class Testupdate_todo:
    '''Tests for update_todo'''
    
    def test_update_todo(self, authenticated_client, fake_todo_data: dict):
        '''test update todo'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-update", id=id)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "high",
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoUpdateResponse.status_code == 200
        assert "Todo completed updated successfully" in todoUpdateResponse.json()["message"]
        assert todoUpdateResponse.json()["todo"]["id"] == id
        assert todoUpdateResponse.json()["todo"]["title"] == "Updated title"
        assert todoUpdateResponse.json()["todo"]["description"] == "Updated description"
        assert todoUpdateResponse.json()["todo"]["priority"] == "high"

    def test_update_todo_with_invalid_id(self, authenticated_client, fake_todo_data: dict):
        '''test update todo with invalid id'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-update", id="123e4567-e89b-12d3-a456-426614174000")
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "high",
        }, headers={"Authorization": f"Bearer {token}"})

        assert todoUpdateResponse.status_code == 404
        assert "Todo not found" in todoUpdateResponse.json()["detail"]

    def test_update_todo_with_existent_title(self, authenticated_client, fake_todo_data: dict):
        '''test update todo with existent title'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #create another todo with same title
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "high",
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-update", id=id)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "high",
        }, headers={"Authorization": f"Bearer {token}"})

        assert todoUpdateResponse.status_code == 409
        assert "Title already exists" in todoUpdateResponse.json()["detail"]

    def test_update_todo_with_invalid_priority(self, authenticated_client, fake_todo_data: dict):
        '''test update todo with invalid priority'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-update", id=id)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "title": "Updated title",
            "description": "Updated description",
            "priority": "invalid_priority",
        }, headers={"Authorization": f"Bearer {token}"})

        assert todoUpdateResponse.status_code == 422
        assert "should be 'low', 'medium' or 'high'" in todoUpdateResponse.json()['detail'][0]['msg']

    def test_create_todo_with_due_date_in_past(self, authenticated_client, fake_todo_data: dict):
        '''test create todo with due date in past'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #create todo with due date in past
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        todoUrl = client.app.url_path_for("v1-todo-update", id=id)  
        todoResponse = client.put(
            todoUrl,
            json={**fake_todo_data, "due_date": past_date.isoformat()},
            headers={"Authorization": f"Bearer {token}"}
        )       

        assert todoResponse.status_code == 422
        assert 'Due date must be in the future' in todoResponse.json()['detail']

    def test_update_todo_order(self, authenticated_client, fake_todo_data: dict):
        '''test update todo order'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl1 = client.app.url_path_for("v1-todo-store")
        todoResponse1 = client.post(todoUrl1, json={**fake_todo_data, "title": "Todo 1"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse1.status_code == 200
        assert "Todo stored successfully" in todoResponse1.json()["message"]
        id1 = todoResponse1.json()["todo"]["id"]

        todoUrl2 = client.app.url_path_for("v1-todo-store")
        todoResponse2 = client.post(todoUrl2, json={**fake_todo_data, "title": "Todo 2"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse2.status_code == 200
        assert "Todo stored successfully" in todoResponse2.json()["message"]
        id2 = todoResponse2.json()["todo"]["id"]

        todoUrl3 = client.app.url_path_for("v1-todo-store")
        todoResponse3 = client.post(todoUrl3, json={**fake_todo_data, "title": "Todo 3"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse3.status_code == 200
        assert "Todo stored successfully" in todoResponse3.json()["message"]
        id3 = todoResponse3.json()["todo"]["id"]

        #update todo order
        todoUpdateUrl = client.app.url_path_for("v1-todo-order-update", id=id1)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "order": int(3)
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoUpdateResponse.status_code == 200
        assert "Todo order updated successfully" in todoUpdateResponse.json()["message"]
        assert todoUpdateResponse.json()["todo"]["order"] == 3

    def test_update_todo_order_with_max_order(self, authenticated_client, fake_todo_data: dict):
        '''test update todo order with max order'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl1 = client.app.url_path_for("v1-todo-store")
        todoResponse1 = client.post(todoUrl1, json={**fake_todo_data, "title": "Todo 1"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse1.status_code == 200
        assert "Todo stored successfully" in todoResponse1.json()["message"]
        id1 = todoResponse1.json()["todo"]["id"]

        todoUrl2 = client.app.url_path_for("v1-todo-store")
        todoResponse2 = client.post(todoUrl2, json={**fake_todo_data, "title": "Todo 2"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse2.status_code == 200
        assert "Todo stored successfully" in todoResponse2.json()["message"]
        id2 = todoResponse2.json()["todo"]["id"]

        todoUrl3 = client.app.url_path_for("v1-todo-store")
        todoResponse3 = client.post(todoUrl3, json={**fake_todo_data, "title": "Todo 3"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse3.status_code == 200
        assert "Todo stored successfully" in todoResponse3.json()["message"]
        id3 = todoResponse3.json()["todo"]["id"]

        #update todo order
        todoUpdateUrl = client.app.url_path_for("v1-todo-order-update", id=id1)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "order": int(4)
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoUpdateResponse.status_code == 200
        assert "Todo order updated successfully" in todoUpdateResponse.json()["message"]    
        assert todoUpdateResponse.json()["todo"]["order"] == 3


    def test_updated_completed_todo(self, authenticated_client, fake_todo_data: dict):

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-completed-update", id=id)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "is_completed": True
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoUpdateResponse.status_code == 200
        assert "Todo completed updated successfully" in todoUpdateResponse.json()["message"]
        assert todoUpdateResponse.json()["todo"]["is_completed"] == True
        
    def test_updated_todo_not_completed(self, authenticated_client, fake_todo_data: dict):

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #update todo
        todoUpdateUrl = client.app.url_path_for("v1-todo-completed-update", id=id)
        todoUpdateResponse = client.put(todoUpdateUrl, json={
            "is_completed": False
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoUpdateResponse.status_code == 200
        assert "Todo completed updated successfully" in todoUpdateResponse.json()["message"]
        assert todoUpdateResponse.json()["todo"]["is_completed"] == False