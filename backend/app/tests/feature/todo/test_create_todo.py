import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone


class Testcreate_todo:
    '''Tests for create_todo'''
    
    def test_create_todo(self, authenticated_client, fake_todo_data: dict):
        '''test create todo'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #get todos
        todosUrl = client.app.url_path_for("v1-todos")
        todosResponse = client.get(todosUrl, headers={"Authorization": f"Bearer {token}"})
        assert todosResponse.status_code == 200

        data = todosResponse.json()
        todo_item = data["items"][0]
        assert todo_item["title"] == fake_todo_data["title"]
        assert todo_item["description"] == fake_todo_data["description"]
        assert todo_item["priority"] == fake_todo_data["priority"]
        assert todo_item["due_date"] == fake_todo_data["due_date"]

    def test_create_todo_with_same_title(self, authenticated_client, fake_todo_data: dict):
        '''test create todo with same title'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #create todo with same title
        todoResponse2 = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse2.status_code == 409
        assert "Title already exists" in todoResponse2.json()["detail"]

    def test_create_todo_with_invalid_priority(self, authenticated_client, fake_todo_data: dict):
        '''test create todo with invalid priority'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo with invalid priority
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json={**fake_todo_data, "priority": "invalid"}, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 422
        assert "should be 'low', 'medium' or 'high'" in todoResponse.json()['detail'][0]['msg']

    def test_create_todo_with_due_date_in_past(self, authenticated_client, fake_todo_data: dict):
        '''test create todo with due date in past'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo with due date in past
        past_date = datetime.now(timezone.utc) - timedelta(days=1)
        todoUrl = client.app.url_path_for("v1-todo-store")  
        todoResponse = client.post(
            todoUrl,
            json={**fake_todo_data, "due_date": past_date.isoformat()},
            headers={"Authorization": f"Bearer {token}"}
        )       
        assert todoResponse.status_code == 422
        assert 'Due date must be in the future' in todoResponse.json()['detail'][0]['msg']