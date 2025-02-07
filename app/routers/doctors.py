import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import async_get_db
from ..schemas import DoctorSchema
from ..services import doctor_services

router = APIRouter(prefix="/doctors", tags=["doctors 👨🏻‍🔬"])
logger = logging.getLogger(__name__)


# ручки
@router.get("/", response_model=list[DoctorSchema])
async def get_all_doctors(db: AsyncSession = Depends(async_get_db)):
    return await doctor_services.get_all_doctors(db)


@router.get("/{doctor_id}", response_model=DoctorSchema)
async def read_doctor_by_id(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    return await doctor_services.get_doctor_by_id(db, doctor_id)


@router.get("/name/{doctor_name}", response_model=DoctorSchema)
async def read_doctor_by_name(
    doctor_name: str, db: AsyncSession = Depends(async_get_db)
):
    return await doctor_services.get_doctor_by_name(db, doctor_name)


@router.post("/", response_model=DoctorSchema)
async def create_doctor(doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)):
    return await doctor_services.create_doctor_in_db(db, doctor)


@router.put("/{doctor_id}", response_model=DoctorSchema)
async def update_doctor(
    doctor_id: int, doctor: DoctorSchema, db: AsyncSession = Depends(async_get_db)
):
    return await doctor_services.update_doctor_in_db(db, doctor_id, doctor)


@router.delete("/{doctor_id}", response_model=dict)
async def delete_doctor(doctor_id: int, db: AsyncSession = Depends(async_get_db)):
    await doctor_services.delete_doctor_from_db(db, doctor_id)
    return {"detail": f"Doctor with id={doctor_id} deleted successfully"}
