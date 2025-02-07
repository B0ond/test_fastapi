from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Doctor, Clinic
from ..schemas import DoctorSchema


# Вспомогательные функции
async def get_all_doctors(db: AsyncSession):
    """Получить список всех докторов."""
    result = await db.execute(select(Doctor))
    return result.scalars().all()


async def get_doctor_by_id(db: AsyncSession, doctor_id: int) -> Doctor:
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


async def get_doctor_by_name(db: AsyncSession, doctor_name: str) -> Doctor:
    result = await db.execute(select(Doctor).filter(Doctor.name == doctor_name))
    doctor = result.scalars().one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor name not found")
    return doctor


async def validate_clinic_exists(db: AsyncSession, clinic_id: int) -> Clinic:
    clinic = await db.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=404, detail=f"Clinic with id={clinic_id} not found"
        )
    return clinic


async def create_doctor_in_db(db: AsyncSession, doctor: DoctorSchema) -> Doctor:
    if doctor.clinic_id:
        await validate_clinic_exists(db, doctor.clinic_id)
    db_doctor = Doctor(name=doctor.name, clinic_id=doctor.clinic_id)
    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


async def update_doctor_in_db(
    db: AsyncSession, doctor_id: int, doctor: DoctorSchema
) -> Doctor:
    db_doctor = await get_doctor_by_id(db, doctor_id)
    db_doctor.name = doctor.name
    db_doctor.clinic_id = doctor.clinic_id
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


async def delete_doctor_from_db(db: AsyncSession, doctor_id: int) -> None:
    db_doctor = await get_doctor_by_id(db, doctor_id)
    await db.delete(db_doctor)
    await db.commit()
    return {"detail": f"Doctor with id={doctor_id} has been deleted."}
