import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_clinic(client: AsyncClient):
    response = await client.post("/clinics/", json={"name": "Clinic Test", "address": "Test Address"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Clinic Test"
    assert "id" in data

@pytest.mark.anyio
async def test_read_clinic(client: AsyncClient):
    # Создаем клинику для теста
    create_response = await client.post("/clinics/", json={"name": "Clinic Test", "address": "Test Address"})
    clinic_id = create_response.json()["id"]

    response = await client.get(f"/clinics/{clinic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Clinic Test"

@pytest.mark.anyio
async def test_update_clinic(client: AsyncClient):
    # Создаем клинику для теста
    create_response = await client.post("/clinics/", json={"name": "Clinic Test", "address": "Test Address"})
    clinic_id = create_response.json()["id"]

    response = await client.put(f"/clinics/{clinic_id}", json={"name": "Clinic Updated", "address": "Updated Address"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Clinic Updated"

@pytest.mark.anyio
async def test_delete_clinic(client: AsyncClient):
    # Создаем клинику для теста
    create_response = await client.post("/clinics/", json={"name": "Clinic Test", "address": "Test Address"})
    clinic_id = create_response.json()["id"]

    response = await client.delete(f"/clinics/{clinic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Clinic with id={clinic_id} deleted successfully"
