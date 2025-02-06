import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import DoctorSchema
from ..models import Doctor, Clinic

router = APIRouter(prefix="/doctors", tags=["doctors 👨🏻‍🔬"])
logger = logging.getLogger(__name__)


# Вспомогательные функции
async def _get_doctor_by_id(db: AsyncSession, doctor_id: int) -> Doctor:
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


async def _get_doctor_by_name(db: AsyncSession, doctor_name: str) -> Doctor:
    result = await db.execute(select(Doctor).filter(Doctor.name == doctor_name))
    doctor = result.scalars().one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor name not found")
    return doctor


async def _validate_clinic_exists(db: AsyncSession, clinic_id: int) -> Clinic:
    clinic = await db.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=404, detail=f"Clinic with id={clinic_id} not found"
        )
    return clinic


async def _create_doctor_in_db(db: AsyncSession, doctor: DoctorSchema) -> Doctor:
    if doctor.clinic_id:
        await _validate_clinic_exists(db, doctor.clinic_id)
    db_doctor = Doctor(name=doctor.name, clinic_id=doctor.clinic_id)
    db.add(db_doctor)
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


async def _update_doctor_in_db(
    db: AsyncSession, doctor_id: int, doctor: DoctorSchema
) -> Doctor:
    db_doctor = await _get_doctor_by_id(db, doctor_id)
    db_doctor.name = doctor.name
    db_doctor.clinic_id = doctor.clinic_id
    await db.commit()
    await db.refresh(db_doctor)
    return db_doctor


async def _delete_doctor_from_db(db: AsyncSession, doctor_id: int) -> None:
    db_doctor = await _get_doctor_by_id(db, doctor_id)
    await db.delete(db_doctor)
    await db.commit()
    logger.info("Doctor with id=%s has been deleted.", doctor_id)


# ручки
@router.get("/", response_model=list[DoctorSchema])
async def get_all_doctors(db: AsyncSession = Depends(async_get_db)):
    doctors = await db.execute(select(Doctor))
    return doctors.scalars().all()


@router.get("/{doctor_id}", response_model=DoctorSchema)
async def read_doctor_by_id(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    return await _get_doctor_by_id(db, doctor_id)


@router.get("/name/{doctor_name}", response_model=DoctorSchema)
async def read_doctor_by_name(
    doctor_name: str, db: AsyncSession = Depends(async_get_db)
):
    return await _get_doctor_by_name(db, doctor_name)


@router.post("/", response_model=DoctorSchema)
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    return await _create_doctor_in_db(db, doctor)


@router.put("/{doctor_id}", response_model=DoctorSchema)
async def update_doctor(
    doctor_id: int, doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)
):
    return await _update_doctor_in_db(db, doctor_id, doctor)


@router.delete("/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    await _delete_doctor_from_db(db, doctor_id)
    return {"detail": f"Doctor with id={doctor_id} deleted successfully"}
