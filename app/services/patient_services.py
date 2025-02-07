from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models import Patient, Doctor, Clinic
from ..schemas import PatientSchema


async def get_all_patient(db: AsyncSession):
    """Получить список всех пациентов."""
    result = await db.execute(select(Patient))
    return result.scalars().all()


async def get_patient_by_id(db: AsyncSession, patient_id: int) -> Patient:
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


async def get_patient_by_name(db: AsyncSession, patient_name: str) -> list[Patient]:
    result = await db.execute(select(Patient).filter(Patient.name == patient_name))
    patients = result.scalars().all()
    if not patients:
        raise HTTPException(status_code=404, detail="Patient name not found")
    return patients


async def validate_doctor_exists(db: AsyncSession, doctor_id: int) -> Doctor:
    doctor = await db.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=404, detail=f"Doctor with id={doctor_id} not found"
        )
    return doctor


async def validate_clinic_exists(db: AsyncSession, clinic_id: int) -> Clinic:
    clinic = await db.get(Clinic, clinic_id)
    if not clinic:
        raise HTTPException(
            status_code=404, detail=f"Clinic with id={clinic_id} not found"
        )
    return clinic


async def create_patient_in_db(db: AsyncSession, patient: PatientSchema) -> Patient:
    if patient.doctor_id is not None:
        doctor = await validate_doctor_exists(db, patient.doctor_id)
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


async def update_patient_in_db(
    db: AsyncSession, patient_id: int, patient: PatientSchema
) -> Patient:
    db_patient = await get_patient_by_id(db, patient_id)

    if patient.doctor_id is not None and patient.doctor_id != db_patient.doctor_id:
        await validate_doctor_exists(db, patient.doctor_id)

    if patient.clinic_id is not None and patient.clinic_id != db_patient.clinic_id:
        await validate_clinic_exists(db, patient.clinic_id)

    db_patient.name = patient.name
    db_patient.doctor_id = patient.doctor_id
    db_patient.clinic_id = patient.clinic_id

    await db.commit()
    await db.refresh(db_patient)
    return db_patient


async def delete_patient_from_db(db: AsyncSession, patient_id: int) -> None:
    db_patient = await get_patient_by_id(db, patient_id)
    await db.delete(db_patient)
    await db.commit()
