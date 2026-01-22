"""
Tests for project endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_create_project(client: TestClient):
    """Test creating a new project."""
    response = client.post(
        "/api/projects",
        json={"name": "Work", "color": "#FF5733", "description": "Work tasks"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Work"
    assert data["color"] == "#FF5733"
    assert data["description"] == "Work tasks"
    assert "id" in data
    assert data["task_count"] == 0


def test_get_projects(client: TestClient):
    """Test getting all projects."""
    # Create some projects
    client.post("/api/projects", json={"name": "Work"})
    client.post("/api/projects", json={"name": "Personal"})
    
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(p["name"] == "Work" for p in data)
    assert any(p["name"] == "Personal" for p in data)


def test_get_single_project(client: TestClient):
    """Test getting a single project by ID."""
    create_response = client.post("/api/projects", json={"name": "Work"})
    project_id = create_response.json()["id"]
    
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Work"
    assert data["id"] == project_id


def test_get_nonexistent_project(client: TestClient):
    """Test getting a project that doesn't exist."""
    response = client.get("/api/projects/9999")
    assert response.status_code == 404


def test_update_project(client: TestClient):
    """Test updating a project."""
    create_response = client.post("/api/projects", json={"name": "Work"})
    project_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/projects/{project_id}",
        json={"name": "Work Projects", "color": "#00FF00"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Work Projects"
    assert data["color"] == "#00FF00"


def test_delete_project(client: TestClient):
    """Test deleting a project."""
    create_response = client.post("/api/projects", json={"name": "Work"})
    project_id = create_response.json()["id"]
    
    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 204
    
    # Verify it's deleted
    get_response = client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404


def test_duplicate_project_name(client: TestClient):
    """Test that duplicate project names are not allowed."""
    client.post("/api/projects", json={"name": "Work"})
    response = client.post("/api/projects", json={"name": "Work"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
