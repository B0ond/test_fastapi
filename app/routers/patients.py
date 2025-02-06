import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import PatientSchema
from ..models import Patient, Doctor, Clinic

router = APIRouter(prefix="/patients", tags=["patients 🙆‍♂️"])
logger = logging.getLogger(__name__)


# Вспомогательные функции
async def _get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def _get_patient_by_name(db: AsyncSession, patient_name: str) -> list[Patient]:
    result = await db.execute(select(Patient).filter(Patient.name == patient_name))
    patients = result.scalars().all()
    if not patients:
        raise HTTPException(status_code=404, detail="Patient name not found")
    return patients


async def _validate_doctor_exists(db: AsyncSession, doctor_id: int) -> Doctor:
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail=f"Doctor with id={doctor_id} not found")
    return doctor


async def _validate_clinic_exists(db: AsyncSession, clinic_id: int) -> Clinic:
    clinic = await db.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(status_code=404, detail=f"Clinic with id={clinic_id} not found")
    return clinic


async def _create_patient_in_db(db: AsyncSession, patient: PatientSchema) -> Patient:
    if patient.doctor_id is not None:
        doctor = await _validate_doctor_exists(db, patient.doctor_id)
        if patient.clinic_id is not None and doctor.clinic_id != patient.clinic_id:
            raise HTTPException(
                status_code=400,
                detail=f"Doctor with id={patient.doctor_id} is not associated with clinic id={patient.clinic_id}",
            )

    db_patient = Patient(
        name=patient.name,
        doctor_id=patient.doctor_id,
        clinic_id=patient.clinic_id or (doctor.clinic_id if patient.doctor_id else None),
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient


async def _update_patient_in_db(
    db: AsyncSession, patient_id: int, patient: PatientSchema
) -> Patient:
    db_patient = await _get_patient_by_id(db, patient_id)

    if patient.doctor_id is not None and patient.doctor_id != db_patient.doctor_id:
        await _validate_doctor_exists(db, patient.doctor_id)

    if patient.clinic_id is not None and patient.clinic_id != db_patient.clinic_id:
        await _validate_clinic_exists(db, patient.clinic_id)

    db_patient.name = patient.name
    db_patient.doctor_id = patient.doctor_id
    db_patient.clinic_id = patient.clinic_id

    await db.commit()
    await db.refresh(db_patient)
    return db_patient


async def _delete_patient_from_db(db: AsyncSession, patient_id: int) -> None:
    db_patient = await _get_patient_by_id(db, patient_id)
    await db.delete(db_patient)
    await db.commit()
    logger.info("Patient with id=%s has been deleted.", patient_id)


# Ручки
@router.get("/", response_model=list[PatientSchema])
async def get_all_patients(db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    return patients


@router.get("/{patient_id}", response_model=PatientSchema)
async def read_patient_by_id(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    return await _get_patient_by_id(db, patient_id)


@router.get("/name/{patient_name}", response_model=list[PatientSchema])
async def read_patient_by_name(
    patient_name: str, db: AsyncSession = Depends(async_get_db)
):
    return await _get_patient_by_name(db, patient_name)


@router.post("/", response_model=PatientSchema)
async def create_patient(patient: PatientSchema, db: AsyncSession = Depends(async_get_db)):
    return await _create_patient_in_db(db, patient)


@router.put("/{patient_id}", response_model=PatientSchema)
async def update_patient(
    patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    return await _update_patient_in_db(db, patient_id, patient)


@router.delete("/{patient_id}", response_model=dict)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    await _delete_patient_from_db(db, patient_id)
    return {"detail": f"Patient with id={patient_id} deleted successfully"}