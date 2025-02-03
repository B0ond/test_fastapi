import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_doctor(client: AsyncClient):
    response = await client.post("/doctors/", json={"name": "Dr. Test", "clinic_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dr. Test"
    assert "id" in data

@pytest.mark.anyio
async def test_read_doctor(client: AsyncClient):
    # Создаем доктора для теста
    create_response = await client.post("/doctors/", json={"name": "Dr. Test", "clinic_id": 1})
    doctor_id = create_response.json()["id"]

    response = await client.get(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dr. Test"

@pytest.mark.anyio
async def test_update_doctor(client: AsyncClient):
    # Создаем доктора для теста
    create_response = await client.post("/doctors/", json={"name": "Dr. Test", "clinic_id": 1})
    doctor_id = create_response.json()["id"]

    response = await client.put(f"/doctors/{doctor_id}", json={"name": "Dr. Updated", "clinic_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Dr. Updated"

@pytest.mark.anyio
async def test_delete_doctor(client: AsyncClient):
    # Создаем доктора для теста
    create_response = await client.post("/doctors/", json={"name": "Dr. Test", "clinic_id": 1})
    doctor_id = create_response.json()["id"]

    response = await client.delete(f"/doctors/{doctor_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Doctor with id={doctor_id} deleted successfully"
