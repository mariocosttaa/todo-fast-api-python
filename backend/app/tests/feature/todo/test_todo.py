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
    
    def test_returning_multiple_todos_index(self, authenticated_client):
        '''test that multiple created todos are returned by index'''
        
        # authenticated_client fixture already creates user, session and token
        client, token, user = authenticated_client

        # create multiple todos with different data
        todo_url = client.app.url_path_for("v1-todo-store")
        created_titles = []

        for i in range(5):
            payload = {
                "title": f"multi todo {i}",
                "description": f"multi desc {i}",
                "priority": "low",
            }
            response = client.post(todo_url, json=payload, headers={"Authorization": f"Bearer {token}"})
            assert response.status_code == 200
            assert "Todo stored successfully" in response.json()["message"]
            created_titles.append(payload["title"])

        # get todos
        todos_url = client.app.url_path_for("v1-todos")
        todos_response = client.get(todos_url, headers={"Authorization": f"Bearer {token}"})
        assert todos_response.status_code == 200

        data = todos_response.json()
        items = data["items"]
        titles_in_response = [item["title"] for item in items]

        # ensure all 5 created todos are present in the index response
        for title in created_titles:
            assert title in titles_in_response
    
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

    def test_todo_index_combined_filters(self, authenticated_client):
        '''create multiple todos and verify index filters by completed, priority and search'''

        client, token, user = authenticated_client

        todo_url = client.app.url_path_for("v1-todo-store")

        # create todos with different priorities
        payloads = [
            {"title": "todo high 1", "description": "h1", "priority": "high"},
            {"title": "todo high 2", "description": "h2", "priority": "high"},
            {"title": "todo medium 1", "description": "m1", "priority": "medium"},
            {"title": "todo low 1", "description": "l1", "priority": "low"},
        ]

        created = []
        for p in payloads:
            resp = client.post(todo_url, json=p, headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200
            body = resp.json()["todo"]
            created.append(body)

        # mark one high and the medium todo as completed using API
        completed_url_template = client.app.url_path_for("v1-todo-completed-update", id="00000000-0000-0000-0000-000000000000")

        def mark_completed(todo_id: str, is_completed: bool):
            url = completed_url_template.replace("00000000-0000-0000-0000-000000000000", todo_id)
            r = client.put(url, json={"is_completed": is_completed}, headers={"Authorization": f"Bearer {token}"})
            assert r.status_code == 200
            return r.json()["todo"]

        completed_high = mark_completed(created[0]["id"], True)
        completed_medium = mark_completed(created[2]["id"], True)

        # 1) no filters -> all todos
        todos_url = client.app.url_path_for("v1-todos")
        r_all = client.get(todos_url, headers={"Authorization": f"Bearer {token}"})
        assert r_all.status_code == 200
        data_all = r_all.json()["items"]
        titles_all = {t["title"] for t in data_all}
        for p in payloads:
            assert p["title"] in titles_all

        # 2) completed=true -> only completed todos
        r_completed = client.get(todos_url, headers={"Authorization": f"Bearer {token}"}, params={"completed": True})
        assert r_completed.status_code == 200
        items_completed = r_completed.json()["items"]
        assert len(items_completed) >= 2
        for item in items_completed:
            assert item["is_completed"] is True

        # 3) completed=false -> only active (not completed) todos
        r_active = client.get(todos_url, headers={"Authorization": f"Bearer {token}"}, params={"completed": False})
        assert r_active.status_code == 200
        items_active = r_active.json()["items"]
        for item in items_active:
            assert item["is_completed"] is False

        # 4) priority filter -> only high priority
        r_high = client.get(todos_url, headers={"Authorization": f"Bearer {token}"}, params={"priority": "high"})
        assert r_high.status_code == 200
        items_high = r_high.json()["items"]
        assert len(items_high) >= 2
        for item in items_high:
            assert item["priority"] == "high"

        # 5) combined filter: completed=true & priority=high
        r_completed_high = client.get(
            todos_url,
            headers={"Authorization": f"Bearer {token}"},
            params={"completed": True, "priority": "high"},
        )
        assert r_completed_high.status_code == 200
        items_completed_high = r_completed_high.json()["items"]
        for item in items_completed_high:
            assert item["is_completed"] is True
            assert item["priority"] == "high"

        # 6) search filter should match by title
        r_search = client.get(todos_url, headers={"Authorization": f"Bearer {token}"}, params={"search": "medium 1"})
        assert r_search.status_code == 200
        items_search = r_search.json()["items"]
        assert any(it["title"] == "todo medium 1" for it in items_search)