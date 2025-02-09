# tests/test_patient.py
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Patient


@pytest.mark.asyncio
async def test_get_all_patients(app: FastAPI, async_client: AsyncClient, patients, db: AsyncSession):
    """Тест получения списка всех пациентов."""
    response = await async_client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Patient 1"
    assert data[1]["name"] == "Test Patient 2"

@pytest.mark.asyncio
async def test_get_patient_by_id(app: FastAPI, async_client: AsyncClient, patients, db: AsyncSession):
    """Тест получения пациента по ID."""
    patient = patients[0]
    response = await async_client.get(f"/patients/{patient.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Patient 1"

@pytest.mark.asyncio
async def test_get_patient_by_name(app: FastAPI, async_client: AsyncClient, patients, db: AsyncSession):
    """Тест получения пациента по имени."""
    patient = patients[0]
    response = await async_client.get(f"/patients/name/{patient.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Patient 1"

@pytest.mark.asyncio
async def test_create_patient(app: FastAPI, async_client: AsyncClient, db: AsyncSession):
    """Тест создания пациента."""
    patient_data = {"name": "New Patient"}
    response = await async_client.post("/patients/", json=patient_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Patient"

    # Проверяем, что пациент действительно создан в базе данных
    created_patient = await db.get(Patient, data["id"])
    assert created_patient.name == "New Patient"

@pytest.mark.asyncio
async def test_update_patient(app: FastAPI, async_client: AsyncClient, patients, db: AsyncSession):
    """Тест обновления пациента."""
    patient = patients[0]
    update_data = {"name": "Updated Patient"}
    response = await async_client.put(f"/patients/{patient.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Patient"

    # Проверяем, что пациент действительно обновлен в базе данных
    updated_patient = await db.get(Patient, patient.id)
    assert updated_patient.name == "Updated Patient"

@pytest.mark.asyncio
async def test_delete_patient(app: FastAPI, async_client: AsyncClient, patients, db: AsyncSession):
    """Тест удаления пациента."""
    patient = patients[0]
    response = await async_client.delete(f"/patients/{patient.id}")
    assert response.status_code == 200

    # Пытаемся получить удаленного пациента из базы данных
    deleted_patient = await db.get(Patient, patient.id)
    assert deleted_patient is None