from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Clinic


async def get_all_clinics_from_db(db: AsyncSession):
    """Получить список всех клиник."""
    result = await db.execute(select(Clinic))
    return result.scalars().all()


async def get_clinic_by_id(db: AsyncSession, clinic_id: int):
    """Получить клинику по ID."""
    clinic = await db.get(Clinic, clinic_id)
    if clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


async def get_clinic_by_name(db: AsyncSession, clinic_name: str):
    """Получить клинику по имени."""
    result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
    clinic = result.scalars().one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic name not found")
    return clinic


async def create_new_clinic(db: AsyncSession, clinic_data):
    """Создать новую клинику."""
    db_clinic = Clinic(name=clinic_data.name, address=clinic_data.address)
    db.add(db_clinic)
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic


async def update_existing_clinic(db: AsyncSession, clinic_id: int, clinic_data):
    """Обновить информацию о клинике."""
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    db_clinic.name = clinic_data.name
    db_clinic.address = clinic_data.address

    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic


async def delete_clinic_by_id(db: AsyncSession, clinic_id: int):
    """Удалить клинику."""
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    await db.delete(db_clinic)
    await db.commit()

    return {"detail": f"Clinic with id={clinic_id} deleted successfully"}
