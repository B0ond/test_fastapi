# tests/test_doctor.py
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Doctor


@pytest.mark.asyncio
async def test_get_all_doctors(app: FastAPI, async_client: AsyncClient, doctors, db: AsyncSession):
    """Тест получения списка всех докторов."""
    response = await async_client.get("/doctors/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Test Doctor 1"
    assert data[1]["name"] == "Test Doctor 2"

@pytest.mark.asyncio
async def test_get_doctor_by_id(app: FastAPI, async_client: AsyncClient, doctors, db: AsyncSession):
    """Тест получения доктора по ID."""
    doctor = doctors[0]
    response = await async_client.get(f"/doctors/{doctor.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Doctor 1"
    assert data["clinic_id"] == doctor.clinic_id

@pytest.mark.asyncio
async def test_get_doctor_by_name(app: FastAPI, async_client: AsyncClient, doctors, db: AsyncSession):
    """Тест получения доктора по имени."""
    doctor = doctors[0]
    response = await async_client.get(f"/doctors/name/{doctor.name}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Doctor 1"
    assert data["clinic_id"] == doctor.clinic_id

@pytest.mark.asyncio
async def test_create_doctor(app: FastAPI, async_client: AsyncClient, clinics, db: AsyncSession):
    """Тест создания доктора."""
    clinic = clinics[0]
    doctor_data = {"name": "New Doctor", "clinic_id": clinic.id}
    response = await async_client.post("/doctors/", json=doctor_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Doctor"
    assert data["clinic_id"] == clinic.id

    # Проверяем, что доктор действительно создан в базе данных
    created_doctor = await db.get(Doctor, data["id"])
    assert created_doctor.name == "New Doctor"
    assert created_doctor.clinic_id == clinic.id

@pytest.mark.asyncio
async def test_update_doctor(app: FastAPI, async_client: AsyncClient, doctors, clinics, db: AsyncSession):
    """Тест обновления доктора."""
    doctor = doctors[0]
    clinic = clinics[1]
    update_data = {"name": "Updated Doctor", "clinic_id": clinic.id}
    response = await async_client.put(f"/doctors/{doctor.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Doctor"
    assert data["clinic_id"] == clinic.id

    # Проверяем, что доктор действительно обновлен в базе данных
    updated_doctor = await db.get(Doctor, doctor.id)
    assert updated_doctor.name == "Updated Doctor"
    assert updated_doctor.clinic_id == clinic.id

@pytest.mark.asyncio
async def test_delete_doctor(app: FastAPI, async_client: AsyncClient, doctors, db: AsyncSession):
    """Тест удаления доктора."""
    doctor = doctors[0]
    response = await async_client.delete(f"/doctors/{doctor.id}")
    assert response.status_code == 200

    # Пытаемся получить удаленного доктора из базы данных
    deleted_doctor = await db.get(Doctor, doctor.id)
    assert deleted_doctor is None