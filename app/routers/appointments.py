import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import AppointmentSchema
from ..models import Appointment, Doctor, Patient

router = APIRouter(prefix="/appointemts", tags=["appointemts 📲"])
logger = logging.getLogger(__name__)


@router.get("/appointments/{appointment_id}", response_model=AppointmentSchema)
async def read_appointment(
    appointment_id: int, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        appointment = result.scalars().first()
        if appointment is None:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment
    except Exception as e:
        logger.error(f"Error reading appointment with id={appointment_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Appointment with id={appointment_id} not found"
        )


@router.post("/appointments/", response_model=AppointmentSchema)
async def create_appointment(
    appointment: AppointmentSchema, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(
            select(Doctor).filter(Doctor.id == appointment.doctor_id)
        )
        doctor = result.scalars().first()
        if doctor is None:
            raise HTTPException(
                status_code=404,
                detail=f"Doctor with id={appointment.doctor_id} not found",
            )

        result = await db.execute(
            select(Patient).filter(Patient.id == appointment.patient_id)
        )
        patient = result.scalars().first()
        if patient is None:
            raise HTTPException(
                status_code=404,
                detail=f"Patient with id={appointment.patient_id} not found",
            )

        if appointment.date.tzinfo is not None:
            appointment_date_naive = appointment.date.replace(tzinfo=None)
        else:
            appointment_date_naive = appointment.date

        db_appointment = Appointment(
            doctor_id=appointment.doctor_id,
            patient_id=appointment.patient_id,
            date=appointment_date_naive,
        )
        db.add(db_appointment)
        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/appointments/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment(
    appointment_id: int,
    appointment: AppointmentSchema,
    db: AsyncSession = Depends(async_get_db),
):
    try:
        result = await db.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        db_appointment = result.scalars().first()
        if db_appointment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with id={appointment_id} not found",
            )

        if appointment.doctor_id != db_appointment.doctor_id:
            result = await db.execute(
                select(Doctor).filter(Doctor.id == appointment.doctor_id)
            )
            doctor = result.scalars().first()
            if doctor is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Doctor with id={appointment.doctor_id} not found",
                )

        if appointment.patient_id != db_appointment.patient_id:
            result = await db.execute(
                select(Patient).filter(Patient.id == appointment.patient_id)
            )
            patient = result.scalars().first()
            if patient is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Patient with id={appointment.patient_id} not found",
                )

        if appointment.date.tzinfo is not None:
            appointment_date_naive = appointment.date.replace(tzinfo=None)
        else:
            appointment_date_naive = appointment.date

        db_appointment.doctor_id = appointment.doctor_id
        db_appointment.patient_id = appointment.patient_id
        db_appointment.date = appointment_date_naive

        await db.commit()
        await db.refresh(db_appointment)
        return db_appointment
    except Exception as e:
        logger.error(f"Error updating appointment with id={appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/appointments/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: int, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(
            select(Appointment).filter(Appointment.id == appointment_id)
        )
        db_appointment = result.scalars().first()
        if db_appointment is None:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment with id={appointment_id} not found",
            )

        await db.delete(db_appointment)
        await db.commit()

        logger.info(f"Appointment with id={appointment_id} has been deleted.")
        return {"detail": f"Appointment with id={appointment_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting appointment with id={appointment_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
