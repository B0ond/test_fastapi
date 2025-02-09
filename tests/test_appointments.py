# tests/test_appointment.py
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Appointment

@pytest.mark.asyncio
async def test_get_all_appointments(app: FastAPI, async_client: AsyncClient, appointments, db: AsyncSession):
    """Тест получения списка всех записей на прием."""
    response = await async_client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["doctor_id"] == appointments[0].doctor_id
    assert data[1]["doctor_id"] == appointments[1].doctor_id

@pytest.mark.asyncio
async def test_get_appointment_by_id(app: FastAPI, async_client: AsyncClient, appointments, db: AsyncSession):
    """Тест получения записи на прием по ID."""
    appointment = appointments[0]
    response = await async_client.get(f"/appointments/{appointment.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == appointment.doctor_id
    assert data["patient_id"] == appointment.patient_id

@pytest.mark.asyncio
async def test_create_appointment(app: FastAPI, async_client: AsyncClient, doctors, patients, db: AsyncSession):
    """Тест создания записи на прием."""
    doctor = doctors[0]
    patient = patients[0]
    appointment_data = {"doctor_id": doctor.id, "patient_id": patient.id, "date": "2024-01-05"}
    response = await async_client.post("/appointments/", json=appointment_data)
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == doctor.id
    assert data["patient_id"] == patient.id
    assert data["date"] == "2024-01-05"

    # Проверяем, что запись на прием действительно создана в базе данных
    created_appointment = await db.get(Appointment, data["id"])
    assert created_appointment.doctor_id == doctor.id
    assert created_appointment.patient_id == patient.id
    assert created_appointment.date == "2024-01-05"

@pytest.mark.asyncio
async def test_update_appointment(app: FastAPI, async_client: AsyncClient, appointments, doctors, patients, db: AsyncSession):
    """Тест обновления записи на прием."""
    appointment = appointments[0]
    doctor = doctors[1]
    patient = patients[1]
    update_data = {"doctor_id": doctor.id, "patient_id": patient.id, "date": "2024-01-10"}
    response = await async_client.put(f"/appointments/{appointment.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["doctor_id"] == doctor.id
    assert data["patient_id"] == patient.id
    assert data["date"] == "2024-01-10"

    # Проверяем, что запись на прием действительно обновлена в базе данных
    updated_appointment = await db.get(Appointment, appointment.id)
    assert updated_appointment.doctor_id == doctor.id
    assert updated_appointment.patient_id == patient.id
    assert updated_appointment.date == "2024-01-10"

@pytest.mark.asyncio
async def test_delete_appointment(app: FastAPI, async_client: AsyncClient, appointments, db: AsyncSession):
    """Тест удаления записи на прием."""
    appointment = appointments[0]
    response = await async_client.delete(f"/appointments/{appointment.id}")
    assert response.status_code == 200

    # Пытаемся получить удаленную запись на прием из базы данных
    deleted_appointment = await db.get(Appointment, appointment.id)
    assert deleted_appointment is None