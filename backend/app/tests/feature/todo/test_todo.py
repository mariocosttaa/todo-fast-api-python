from pprint import pprint
import pytest
from fastapi.testclient import TestClient

class Testtodo:
    '''Tests for todo'''
    
    def test_returning_all_todos(self, authenticated_client, fake_todo_data: dict):
        '''test returning all todos'''
        
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
    
    def test_todo_search_create_and_filter(self, authenticated_client, fake_todo_data: dict):
        '''test todo search create and filter'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl1 = client.app.url_path_for("v1-todo-store")
        todoResponse1 = client.post(todoUrl1, json={
            "title": "testing search",
            "description": "test",
            "priority": "low",
        }, headers={"Authorization": f"Bearer {token}"})

        todoUrl2 = client.app.url_path_for("v1-todo-store")
        todoResponse2 = client.post(todoUrl2, json={
            "title": "bla bla",
            "description": "test",
            "priority": "low",
        }, headers={"Authorization": f"Bearer {token}"})

        assert todoResponse1.status_code == 200
        assert "Todo stored successfully" in todoResponse1.json()["message"]
        
        assert todoResponse2.status_code == 200
        assert "Todo stored successfully" in todoResponse2.json()["message"]
        
        #get todos and verify search
        todosUrl = client.app.url_path_for("v1-todos")
        todosResponse = client.get(todosUrl, headers={"Authorization": f"Bearer {token}"}, params={"search": "testing search"})
        assert todosResponse.status_code == 200

        pprint(todosResponse.json())
        
        data = todosResponse.json()
        todo_item = data["items"][0]
        assert todo_item["title"] == "testing search"
    
    def test_todo_completed_create_and_filter(self, authenticated_client, fake_todo_data: dict):
        '''test todo completed create and filter'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #get todos
        todosUrl = client.app.url_path_for("v1-todos")
        todosResponse = client.get(todosUrl, headers={"Authorization": f"Bearer {token}"}, params={"completed": True})
        assert todosResponse.status_code == 200

        data = todosResponse.json()
        for todo_item in data["items"]:
            assert todo_item["is_completed"] == True
    
    def test_todo_priority_create_and_filter(self, authenticated_client, fake_todo_data: dict):
        '''test todo priority create and filter'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json={
            "title": "testing priority",
            "description": "test",
            "priority": "high",
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]

        #create todo 2
        todoUrl2 = client.app.url_path_for("v1-todo-store")
        todoResponse2 = client.post(todoUrl2, json={
            "title": "testing priority 2",
            "description": "test",
            "priority": "medium",
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse2.status_code == 200
        assert "Todo stored successfully" in todoResponse2.json()["message"]
        
        #create todo 3
        todoUrl3 = client.app.url_path_for("v1-todo-store")
        todoResponse3 = client.post(todoUrl3, json={
            "title": "testing priority 3",
            "description": "test",
            "priority": "low",
        }, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse3.status_code == 200
        assert "Todo stored successfully" in todoResponse3.json()["message"]


        #get todos
        todosUrl = client.app.url_path_for("v1-todos")
        todosResponse = client.get(todosUrl, headers={"Authorization": f"Bearer {token}"}, params={"priority": "high"})
        assert todosResponse.status_code == 200

        data = todosResponse.json()
        for todo_item in data["items"]:
            assert todo_item["priority"] == "high"
    
    def test_todo_delete(self, authenticated_client, fake_todo_data: dict):
        '''test todo delete'''

        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        #create todo
        todoUrl = client.app.url_path_for("v1-todo-store")
        todoResponse = client.post(todoUrl, json=fake_todo_data, headers={"Authorization": f"Bearer {token}"})
        assert todoResponse.status_code == 200
        assert "Todo stored successfully" in todoResponse.json()["message"]
        id = todoResponse.json()["todo"]["id"]

        #delete todo
        todoDeleteUrl = client.app.url_path_for("v1-todo-destroy", id=id)
        todoDeleteResponse = client.delete(todoDeleteUrl, headers={"Authorization": f"Bearer {token}"})
        assert todoDeleteResponse.status_code == 200
        assert "Todo deleted successfully" in todoDeleteResponse.json()["message"]