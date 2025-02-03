import pytest
from httpx import AsyncClient

@pytest.mark.anyio
async def test_create_appointment(client: AsyncClient):
    response = await client.post("/appointments/", json={"doctor_id": 1, "patient_id": 1, "date": "2023-10-01T10:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

@pytest.mark.anyio
async def test_read_appointment(client: AsyncClient):
    # Создаем запись для теста
    create_response = await client.post("/appointments/", json={"doctor_id": 1, "patient_id": 1, "date": "2023-10-01T10:00:00"})
    appointment_id = create_response.json()["id"]

    response = await client.get(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == 1
    assert data["patient_id"] == 1

@pytest.mark.anyio
async def test_update_appointment(client: AsyncClient):
    # Создаем запись для теста
    create_response = await client.post("/appointments/", json={"doctor_id": 1, "patient_id": 1, "date": "2023-10-01T10:00:00"})
    appointment_id = create_response.json()["id"]

    response = await client.put(f"/appointments/{appointment_id}", json={"doctor_id": 1, "patient_id": 1, "date": "2023-10-02T10:00:00"})
    assert response.status_code == 200
    data = response.json()
    assert data["date"] == "2023-10-02T10:00:00"

@pytest.mark.anyio
async def test_delete_appointment(client: AsyncClient):
    # Создаем запись для теста
    create_response = await client.post("/appointments/", json={"doctor_id": 1, "patient_id": 1, "date": "2023-10-01T10:00:00"})
    appointment_id = create_response.json()["id"]

    response = await client.delete(f"/appointments/{appointment_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["detail"] == f"Appointment with id={appointment_id} deleted successfully"
