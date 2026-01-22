"""
Tests for task endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date, timedelta


def test_create_task(client: TestClient):
    """Test creating a new task."""
    response = client.post(
        "/api/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high",
            "due_date": str(date.today() + timedelta(days=1))
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["priority"] == "high"
    assert data["is_completed"] == False
    assert "id" in data


def test_create_task_with_project(client: TestClient):
    """Test creating a task with a project."""
    # Create project first
    project_response = client.post("/api/projects", json={"name": "Work"})
    project_id = project_response.json()["id"]
    
    response = client.post(
        "/api/tasks",
        json={
            "title": "Review code",
            "project_id": project_id,
            "priority": "medium"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["project_id"] == project_id
    assert data["project"]["name"] == "Work"


def test_create_task_with_tags(client: TestClient):
    """Test creating a task with tags."""
    # Create tags first
    tag1_response = client.post("/api/tags", json={"name": "urgent"})
    tag2_response = client.post("/api/tags", json={"name": "important"})
    tag1_id = tag1_response.json()["id"]
    tag2_id = tag2_response.json()["id"]
    
    response = client.post(
        "/api/tasks",
        json={
            "title": "Critical task",
            "tag_ids": [tag1_id, tag2_id],
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["tags"]) == 2
    tag_names = [tag["name"] == "urgent" for tag in data["tags"]]
    assert any(tag_names)


def test_get_tasks(client: TestClient):
    """Test getting all tasks."""
    # Create some tasks
    client.post("/api/tasks", json={"title": "Task 1", "priority": "low"})
    client.post("/api/tasks", json={"title": "Task 2", "priority": "high"})
    
    response = client.get("/api/tasks")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_filter_tasks_by_completion(client: TestClient):
    """Test filtering tasks by completion status."""
    client.post("/api/tasks", json={"title": "Task 1", "priority": "low"})
    task2_response = client.post("/api/tasks", json={"title": "Task 2", "priority": "high"})
    task2_id = task2_response.json()["id"]
    
    # Mark one as completed
    client.patch(f"/api/tasks/{task2_id}", json={"is_completed": True})
    
    # Get only incomplete tasks
    response = client.get("/api/tasks?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Task 1"


def test_filter_tasks_by_project(client: TestClient):
    """Test filtering tasks by project."""
    # Create projects
    project1 = client.post("/api/projects", json={"name": "Work"}).json()
    project2 = client.post("/api/projects", json={"name": "Personal"}).json()
    
    # Create tasks
    client.post("/api/tasks", json={"title": "Work task", "project_id": project1["id"], "priority": "medium"})
    client.post("/api/tasks", json={"title": "Personal task", "project_id": project2["id"], "priority": "low"})
    
    # Filter by project
    response = client.get(f"/api/tasks?project_id={project1['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Work task"


def test_search_tasks(client: TestClient):
    """Test searching tasks by title/description."""
    client.post("/api/tasks", json={"title": "Buy groceries", "description": "Milk and bread", "priority": "low"})
    client.post("/api/tasks", json={"title": "Review code", "description": "PR #123", "priority": "high"})
    
    # Search for "groceries"
    response = client.get("/api/tasks?search=groceries")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Buy groceries"
    
    # Search for "code"
    response = client.get("/api/tasks?search=code")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Review code"


def test_today_view(client: TestClient):
    """Test the 'today' smart view."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    client.post("/api/tasks", json={"title": "Today task", "due_date": str(today), "priority": "high"})
    client.post("/api/tasks", json={"title": "Tomorrow task", "due_date": str(tomorrow), "priority": "low"})
    
    response = client.get("/api/tasks?view=today")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Today task"


def test_update_task(client: TestClient):
    """Test updating a task."""
    create_response = client.post("/api/tasks", json={"title": "Old title", "priority": "low"})
    task_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/tasks/{task_id}",
        json={"title": "New title", "priority": "high", "is_completed": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New title"
    assert data["priority"] == "high"
    assert data["is_completed"] == True


def test_delete_task(client: TestClient):
    """Test deleting a task."""
    create_response = client.post("/api/tasks", json={"title": "To delete", "priority": "low"})
    task_id = create_response.json()["id"]
    
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == 404


def test_sort_tasks_by_priority(client: TestClient):
    """Test sorting tasks by priority (high → medium → low)."""
    # Create tasks with different priorities
    client.post("/api/tasks", json={
        "title": "Low priority task",
        "priority": "low",
        "is_completed": False
    })
    client.post("/api/tasks", json={
        "title": "High priority task",
        "priority": "high",
        "is_completed": False
    })
    client.post("/api/tasks", json={
        "title": "Medium priority task",
        "priority": "medium",
        "is_completed": False
    })
    
    # Sort by priority
    response = client.get("/api/tasks?sort=priority")
    assert response.status_code == 200
    
    tasks = response.json()
    assert len(tasks) == 3
    assert tasks[0]["priority"] == "high"
    assert tasks[1]["priority"] == "medium"
    assert tasks[2]["priority"] == "low"


def test_sort_tasks_by_due_date(client: TestClient):
    """Test sorting tasks by due date."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)
    
    client.post("/api/tasks", json={
        "title": "Task 1",
        "due_date": str(tomorrow),
        "is_completed": False,
        "priority": "medium"
    })
    client.post("/api/tasks", json={
        "title": "Task 2",
        "due_date": str(yesterday),
        "is_completed": False,
        "priority": "medium"
    })
    client.post("/api/tasks", json={
        "title": "Task 3",
        "due_date": str(today),
        "is_completed": False,
        "priority": "medium"
    })
    
    # Sort ascending (earliest first)
    response = client.get("/api/tasks?sort=due_date_asc")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["due_date"] == str(yesterday)
    assert tasks[1]["due_date"] == str(today)
    assert tasks[2]["due_date"] == str(tomorrow)
    
    # Sort descending (latest first)
    response = client.get("/api/tasks?sort=due_date_desc")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["due_date"] == str(tomorrow)
    assert tasks[1]["due_date"] == str(today)
    assert tasks[2]["due_date"] == str(yesterday)


def test_sort_tasks_by_title(client: TestClient):
    """Test sorting tasks alphabetically by title."""
    client.post("/api/tasks", json={"title": "Zebra", "is_completed": False, "priority": "medium"})
    client.post("/api/tasks", json={"title": "Apple", "is_completed": False, "priority": "medium"})
    client.post("/api/tasks", json={"title": "Mango", "is_completed": False, "priority": "medium"})
    
    response = client.get("/api/tasks?sort=title")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["title"] == "Apple"
    assert tasks[1]["title"] == "Mango"
    assert tasks[2]["title"] == "Zebra"


def test_sort_tasks_by_created_at(client: TestClient):
    """Test sorting tasks by creation date."""
    client.post("/api/tasks", json={"title": "First", "is_completed": False, "priority": "medium"})
    client.post("/api/tasks", json={"title": "Second", "is_completed": False, "priority": "medium"})
    client.post("/api/tasks", json={"title": "Third", "is_completed": False, "priority": "medium"})
    
    # Sort descending (newest first) - default
    response = client.get("/api/tasks?sort=created_at_desc")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["title"] == "Third"
    assert tasks[2]["title"] == "First"
    
    # Sort ascending (oldest first)
    response = client.get("/api/tasks?sort=created_at_asc")
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["title"] == "First"
    assert tasks[2]["title"] == "Third"


def test_all_sort_options_work(client: TestClient):
    """Smoke test: ensure all sort options don't crash with 500 error."""
    # Create a sample task
    client.post("/api/tasks", json={"title": "Test", "is_completed": False, "priority": "medium"})
    
    sort_options = [
        'created_at_asc',
        'created_at_desc',
        'due_date_asc',
        'due_date_desc',
        'priority',
        'title'
    ]
    
    for sort in sort_options:
        response = client.get(f"/api/tasks?sort={sort}")
        assert response.status_code == 200, f"Sort option '{sort}' failed with status {response.status_code}"
