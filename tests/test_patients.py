import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_patient(client: AsyncClient):
    response = await client.post("/patients/", json={"name": "Patient Test", "doctor_id": 1, "clinic_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patient Test"
    assert "id" in data

@pytest.mark.anyio
async def test_read_patient(client: AsyncClient):
    # Создаем пациента для теста
    create_response = await client.post("/patients/", json={"name": "Patient Test", "doctor_id": 1, "clinic_id": 1})
    patient_id = create_response.json()["id"]

    response = await client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patient Test"

@pytest.mark.anyio
async def test_update_patient(client: AsyncClient):
    # Создаем пациента для теста
    create_response = await client.post("/patients/", json={"name": "Patient Test", "doctor_id": 1, "clinic_id": 1})
    patient_id = create_response.json()["id"]

    response = await client.put(f"/patients/{patient_id}", json={"name": "Patient Updated", "doctor_id": 1, "clinic_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Patient Updated"

@pytest.mark.anyio
async def test_delete_patient(client: AsyncClient):
    # Создаем пациента для теста
    create_response = await client.post("/patients/", json={"name": "Patient Test", "doctor_id": 1, "clinic_id": 1})
    patient_id = create_response.json()["id"]

    response = await client.delete(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Patient with id={patient_id} deleted successfully"
