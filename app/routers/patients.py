import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import PatientSchema
from ..models import Patient
from ..services import patient_services

router = APIRouter(prefix="/patients", tags=["patients 🙆‍♂️"])
logger = logging.getLogger(__name__)


# Ручки
@router.get("/", response_model=list[PatientSchema])
async def get_all_patients(db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientSchema)
async def cread_patient_by_id(
    patient_id: int, db: AsyncSession = Depends(async_get_db)
):
    return await patient_services.get_patient_by_id(db, patient_id)


@router.get("/name/{patient_name}", response_model=list[PatientSchema])
async def read_patient_by_name(
    patient_name: str, db: AsyncSession = Depends(async_get_db)
):
    return await patient_services.get_patient_by_name(db, patient_name)


@router.post("/", response_model=PatientSchema)
async def create_patient(
    patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    return await patient_services.create_patient_in_db(db, patient)


@router.put("/{patient_id}", response_model=PatientSchema)
async def update_patient(
    patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    return await patient_services.update_patient_in_db(db, patient_id, patient)


@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    await patient_services.delete_patient_from_db(db, patient_id)
    return {"detail": f"Patient with id={patient_id} deleted successfully"}
