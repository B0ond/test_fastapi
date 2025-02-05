import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import DoctorSchema
from ..models import Doctor, Clinic

router = APIRouter(prefix="/doctors", tags=["doctors 👨🏻‍🔬"])
logger = logging.getLogger(__name__)


@router.get("/doctors/", response_model=list[DoctorSchema])
async def get_all_doctors(db: AsyncSession = Depends(async_get_db)):
    doctors = await db.execute(select(Doctor))
    return doctors.scalars().all()


@router.get("/doctors/{doctor_id}", response_model=DoctorSchema)
async def read_doctor_by_id(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
    doctor = result.scalars().first()
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.get("/doctors/name/{doctor_name}", response_model=list[DoctorSchema])
async def read_doctor_by_name(
    doctor_name: str, db: AsyncSession = Depends(async_get_db)
):
    result = await db.execute(select(Doctor).filter(Doctor.name == doctor_name))
    doctors = result.scalars().all()
    if not doctors:
        raise HTTPException(status_code=404, detail="Doctor name not found")
    return doctors


@router.post("/doctors/", response_model=DoctorSchema)
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        if doctor.clinic_id is not None:
            result = await db.execute(
                select(Clinic).filter(Clinic.id == doctor.clinic_id)
            )
            clinic = result.scalars().first()
            if clinic is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clinic with id={doctor.clinic_id} not found",
                )
        db_doctor = Doctor(name=doctor.name, clinic_id=doctor.clinic_id)
        db.add(db_doctor)
        await db.commit()
        await db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        logger.error("Error creating doctor: %s", e)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.put("/doctors/{doctor_id}", response_model=DoctorSchema)
async def update_doctor(
    doctor_id: int, doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
        db_doctor = result.scalars().first()
        if db_doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        db_doctor.name = doctor.name
        db_doctor.clinic_id = doctor.clinic_id
        await db.commit()
        await db.refresh(db_doctor)
        return db_doctor
    except Exception as e:
        logger.error("Error updating doctor with id=%s: %s", doctor_id, e)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.delete("/doctors/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Doctor).filter(Doctor.id == doctor_id))
        db_doctor = result.scalars().first()
        if db_doctor is None:
            raise HTTPException(status_code=404, detail="Doctor not found")
        await db.delete(db_doctor)
        await db.commit()
        logger.info("Doctor with id=%s has been deleted.", doctor_id)
        return {"detail": f"Doctor with id={doctor_id} deleted successfully"}
    except Exception as e:
        logger.error("Error deleting doctor with id=%s: %s", doctor_id, e)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
