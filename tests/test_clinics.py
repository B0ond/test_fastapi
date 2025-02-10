import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Clinic


async def create_test_clinic(
    db: AsyncSession,
    clinic_name: str = "Test Clinic",
    clinic_address: str = "Test Address",
):
    """Helper function to create a test clinic."""
    clinic = Clinic(name=clinic_name, address=clinic_address)
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic


@pytest.mark.asyncio
async def test_create_clinic(async_client: AsyncClient, test_db: AsyncSession):
    clinic_data = {"name": "New Clinic", "address": "New Address"}
    response = await async_client.post("/clinics/", json=clinic_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == clinic_data["name"]
    assert data["address"] == clinic_data["address"]

    # Verify clinic exists in the database
    clinic = await test_db.get(Clinic, data["id"])
    assert clinic is not None
    assert clinic.name == clinic_data["name"]
    assert clinic.address == clinic_data["address"]


@pytest.mark.asyncio
async def test_get_all_clinics(async_client: AsyncClient, test_db: AsyncSession):
    # Create some clinics in the test database
    await create_test_clinic(test_db, "Clinic 1")
    await create_test_clinic(test_db, "Clinic 2", "Address 2")

    response = await async_client.get("/clinics/")
    assert response.status_code == 200
    clinics = response.json()
    assert len(clinics) >= 2


@pytest.mark.asyncio
async def test_read_clinic_by_id(async_client: AsyncClient, test_db: AsyncSession):
    clinic = await create_test_clinic(test_db, "Clinic to Read", "Read Address")
    response = await async_client.get(f"/clinics/{clinic.id}")
    assert response.status_code == 200
    clinic_data = response.json()
    assert clinic_data["name"] == "Clinic to Read"
    assert clinic_data["address"] == "Read Address"


@pytest.mark.asyncio
async def test_update_clinic(async_client: AsyncClient, test_db: AsyncSession):
    clinic = await create_test_clinic(test_db, "Clinic to Update", "Original Address")
    updated_data = {"name": "Updated Clinic", "address": "Updated Address"}
    response = await async_client.put(f"/clinics/{clinic.id}", json=updated_data)

    assert response.status_code == 200
    updated_clinic = response.json()
    assert updated_clinic["name"] == "Updated Clinic"
    assert updated_clinic["address"] == "Updated Address"

    clinic = await test_db.get(Clinic, clinic.id)
    assert clinic is not None
    assert clinic.name == "Updated Clinic"
    assert clinic.address == "Updated Address"


@pytest.mark.asyncio
async def test_delete_clinic(async_client: AsyncClient, test_db: AsyncSession):
    clinic = await create_test_clinic(test_db, "Clinic to Delete", "Delete Address")
    response = await async_client.delete(f"/clinics/{clinic.id}")
    assert response.status_code == 200

    clinic = await test_db.get(Clinic, clinic.id)
    assert clinic is None


@pytest.mark.asyncio
async def test_read_clinic_by_name(async_client: AsyncClient, test_db: AsyncSession):
    clinic = await create_test_clinic(test_db, "Unique Clinic Name", "Some Address")
    response = await async_client.get(f"/clinics/name/{clinic.name}")
    assert response.status_code == 200
    clinic_data = response.json()
    assert clinic_data["name"] == "Unique Clinic Name"
    assert clinic_data["address"] == "Some Address"
