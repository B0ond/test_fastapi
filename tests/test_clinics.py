# tests/test_clinic.py
import pytest
from httpx import AsyncClient
from app.models import Clinic

@pytest.mark.asyncio
async def test_get_all_clinics(async_client: AsyncClient, clinics: list[Clinic]):
    """Тест получения списка всех клиник."""
    response = await async_client.get("/clinics/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Clinic 1"
    assert data[1]["name"] == "Test Clinic 2"

@pytest.mark.asyncio
async def test_get_clinic_by_id(async_client: AsyncClient, clinics: list[Clinic]):
    """Тест получения клиники по ID."""
    clinic = clinics[0]
    response = await async_client.get(f"/clinics/{clinic.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Clinic 1"
    assert data["address"] == "Test Address 1"

@pytest.mark.asyncio
async def test_get_clinic_by_name(async_client: AsyncClient, clinics: list[Clinic]):
    """Тест получения клиники по имени."""
    clinic = clinics[0]
    response = await async_client.get(f"/clinics/name/{clinic.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Clinic 1"
    assert data["address"] == "Test Address 1"

@pytest.mark.asyncio
async def test_create_clinic(async_client: AsyncClient):
    """Тест создания клиники."""
    clinic_data = {"name": "New Clinic", "address": "New Address"}
    response = await async_client.post("/clinics/", json=clinic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Clinic"
    assert data["address"] == "New Address"

@pytest.mark.asyncio
async def test_update_clinic(async_client: AsyncClient, clinics: list[Clinic]):
    """Тест обновления клиники."""
    clinic = clinics[0]
    update_data = {"name": "Updated Clinic", "address": "Updated Address"}
    response = await async_client.put(f"/clinics/{clinic.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Clinic"
    assert data["address"] == "Updated Address"

@pytest.mark.asyncio
async def test_delete_clinic(async_client: AsyncClient, clinics: list[Clinic]):
    """Тест удаления клиники."""
    clinic = clinics[0]
    response = await async_client.delete(f"/clinics/{clinic.id}")
    assert response.status_code == 200