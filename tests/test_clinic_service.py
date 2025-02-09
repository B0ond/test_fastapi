import pytest
from fastapi import HTTPException
from app.services import clinic_services
from app.models import Clinic
from tests.conftest import TestingSessionLocal  # Импортируйте TestingSessionLocal

@pytest.mark.asyncio
async def test_get_clinic_by_id_success():
    async with TestingSessionLocal() as db:  # Используйте TestingSessionLocal
        # 1. Arrange
        clinic = Clinic(name="Test Clinic", address="Test Address")
        db.add(clinic)
        await db.commit()
        await db.refresh(clinic)

        # 2. Act
        retrieved_clinic = await clinic_services.get_clinic_by_id(db, clinic.id)

        # 3. Assert
        assert retrieved_clinic == clinic

@pytest.mark.asyncio
async def test_get_clinic_by_id_not_found():
    async with TestingSessionLocal() as db:
        with pytest.raises(HTTPException) as exc_info:
            await clinic_services.get_clinic_by_id(db, 1)
        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Clinic not found"

@pytest.mark.asyncio
async def test_create_new_clinic(clinic_schema):
    async with TestingSessionLocal() as db:
        clinic = await clinic_services.create_new_clinic(db, clinic_schema)
        await db.refresh(clinic)
        assert clinic.name == clinic_schema.name
        assert clinic.address == clinic_schema.address