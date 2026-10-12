import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    response = await client.post("/api/v1/projects", json={"name": "Test Project", "description": "A test"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["description"] == "A test"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_project_validation(client: AsyncClient):
    response = await client.post("/api/v1/projects", json={"name": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    await client.post("/api/v1/projects", json={"name": "Project 1"})
    await client.post("/api/v1/projects", json={"name": "Project 2"})
    response = await client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 20


@pytest.mark.asyncio
async def test_list_projects_pagination(client: AsyncClient):
    for i in range(5):
        await client.post("/api/v1/projects", json={"name": f"Project {i}"})
    response = await client.get("/api/v1/projects?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total_pages"] == 3


@pytest.mark.asyncio
async def test_list_projects_filter_status(client: AsyncClient):
    # Create active project
    resp1 = await client.post("/api/v1/projects", json={"name": "Active Project"})
    project1_id = resp1.json()["id"]
    await client.patch(f"/api/v1/projects/{project1_id}", json={"status": "active"})

    # Create draft project (default)
    await client.post("/api/v1/projects", json={"name": "Draft Project"})

    response = await client.get("/api/v1/projects?status=active")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Active Project"

@pytest.mark.asyncio
async def test_list_projects_search(client: AsyncClient):
    await client.post("/api/v1/projects", json={"name": "Alpha Project", "description": "First"})
    await client.post("/api/v1/projects", json={"name": "Beta Project", "description": "Second"})
    response = await client.get("/api/v1/projects?search=Alpha")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Alpha Project"


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    create_resp = await client.post("/api/v1/projects", json={"name": "Get Me"})
    project_id = create_resp.json()["id"]
    response = await client.get(f"/api/v1/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == "Get Me"


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    response = await client.get("/api/v1/projects/99999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_project(client: AsyncClient):
    create_resp = await client.post("/api/v1/projects", json={"name": "Original"})
    project_id = create_resp.json()["id"]
    response = await client.patch(f"/api/v1/projects/{project_id}", json={"name": "Updated", "status": "active"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"
    assert data["status"] == "active"


@pytest.mark.asyncio
async def test_update_project_not_found(client: AsyncClient):
    response = await client.patch("/api/v1/projects/99999", json={"name": "Nope"})
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    create_resp = await client.post("/api/v1/projects", json={"name": "To Delete"})
    project_id = create_resp.json()["id"]
    response = await client.delete(f"/api/v1/projects/{project_id}")
    assert response.status_code == 204
    get_resp = await client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/projects/99999")
    assert response.status_code == 404
