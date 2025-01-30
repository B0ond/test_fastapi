import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import PatientSchema
from ..models import Patient, Doctor, Clinic

router = APIRouter(prefix="/patients", tags=["patients 🙆‍♂️"])
logger = logging.getLogger(__name__)


@router.get("/patients/{patient_id}", response_model=PatientSchema)
async def read_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        patient = result.scalars().first()
        if patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient
    except Exception as e:
        logger.error(f"Error reading patient with id={patient_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Patient with id={patient_id} not found"
        )


@router.get("/patients/name/{patient_name}", response_model=list[PatientSchema])
async def read_patient_by_name(
    patient_name: str, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Patient).filter(Patient.name == patient_name))
        patients = result.scalars().all()
        if not patients:
            raise HTTPException(status_code=404, detail="Patient name not found")
        return patients
    except Exception as e:
        logger.error(f"Error reading patient by name={patient_name}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Patient with name={patient_name} not found"
        )


@router.post("/patients/", response_model=PatientSchema)
async def create_patient(
    patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    try:
        if patient.doctor_id is not None:
            result = await db.execute(
                select(Doctor).filter(Doctor.id == patient.doctor_id)
            )
            doctor = result.scalars().first()
            if doctor is None:
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
            clinic_id=(
                patient.clinic_id
                if patient.clinic_id
                else (doctor.clinic_id if patient.doctor_id else None)
            ),
        )
        db.add(db_patient)
        await db.commit()
        await db.refresh(db_patient)
        return db_patient
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/patients/{patient_id}", response_model=PatientSchema)
async def update_patient(
    patient_id: int, patient: PatientSchema, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        db_patient = result.scalars().first()
        if db_patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")

        if patient.doctor_id is not None and patient.doctor_id != db_patient.doctor_id:
            result = await db.execute(
                select(Doctor).filter(Doctor.id == patient.doctor_id)
            )
            doctor = result.scalars().first()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with id={patient.doctor_id} not found",
                )

        if patient.clinic_id is not None and patient.clinic_id != db_patient.clinic_id:
            result = await db.execute(
                select(Clinic).filter(Clinic.id == patient.clinic_id)
            )
            clinic = result.scalars().first()
            if clinic is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Clinic with id={patient.clinic_id} not found",
                )

        db_patient.name = patient.name
        db_patient.doctor_id = patient.doctor_id
        db_patient.clinic_id = patient.clinic_id
        await db.commit()
        await db.refresh(db_patient)
        return db_patient
    except Exception as e:
        logger.error(f"Error updating patient with id={patient_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/patients/{patient_id}", response_model=dict)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Patient).filter(Patient.id == patient_id))
        db_patient = result.scalars().first()
        if db_patient is None:
            raise HTTPException(status_code=404, detail="Patient not found")

        await db.delete(db_patient)
        await db.commit()

        logger.info(f"Patient with id={patient_id} has been deleted.")
        return {"detail": f"Patient with id={patient_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting patient with id={patient_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
