import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import PatientSchema
from ..models import Patient, Doctor, Clinic

router = APIRouter(prefix="/patients", tags=["patients 🙆‍♂️"])
logger = logging.getLogger(__name__)


@router.get("/patients", response_model=list[PatientSchema])
async def get_all_patients(db: AsyncSession = Depends(async_get_db)):
    result = await db.execute(select(Patient))
    patients = result.scalars().all()
    return patients


@router.get("/patients/{patient_id}", response_model=PatientSchema)
async def read_patient_by_id(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    db_patient = await db.get(Patient, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@router.get("/patients/name/{patient_name}", response_model=PatientSchema)
async def read_patient_by_name(
    patient_name: str, db: AsyncSession = Depends(async_get_db)
):
    result = await db.execute(select(Patient).filter(Patient.name == patient_name))
    patients = result.scalars().all()
    if not patients:
        raise HTTPException(status_code=404, detail="Patient name not found")
    return patients


@router.post("/patients/", response_model=PatientSchema)
async def create_patient(
    patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    if patient.doctor_id is not None:
        doctor = await db.get(Doctor, patient.doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor with id={patient.doctor_id} not found",
            )

        if patient.clinic_id is not None and doctor.clinic_id != patient.clinic_id:
            raise HTTPException(
                status_code=400,
                detail=f"Doctor with id={patient.doctor_id} is not associated with clinic id={patient.clinic_id}",
            )

    db_patient = Patient(
        name=patient.name,
        doctor_id=patient.doctor_id,
        clinic_id=patient.clinic_id
        or (doctor.clinic_id if patient.doctor_id else None),
    )
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient


@router.put("/patients/{patient_id}", response_model=PatientSchema)
async def update_patient(
    patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    db_patient = await db.get(Patient, patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient.doctor_id is not None and patient.doctor_id != db_patient.doctor_id:
        if not await db.get(Doctor, patient.doctor_id):
            raise HTTPException(
                status_code=404, detail=f"Doctor with id={patient.doctor_id} not found"
            )

    if patient.clinic_id is not None and patient.clinic_id != db_patient.clinic_id:
        if not await db.get(Clinic, patient.clinic_id):
            raise HTTPException(
                status_code=404, detail=f"Clinic with id={patient.clinic_id} not found"
            )

    db_patient.name = patient.name
    db_patient.doctor_id = patient.doctor_id
    db_patient.clinic_id = patient.clinic_id

    await db.commit()
    await db.refresh(db_patient)
    return db_patient


# упрощаю для запросов по id делаю по db.get()
@router.delete("/patients/{patient_id}", response_model=dict)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    db_patient = await db.get(Patient, patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    await db.delete(db_patient)
    await db.commit()

    logger.info("Patient with id=%s has been deleted.", patient_id)
    return {"detail": f"Patient with id={patient_id} deleted successfully"}
