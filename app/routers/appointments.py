import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import async_get_db
from ..schemas import AppointmentSchema
from ..services import appointmenr_services

router = APIRouter(prefix="/appointemts", tags=["appointemts 📲"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=list[AppointmentSchema])
async def get_all_appointments(db: AsyncSession = Depends(async_get_db)):
    return await appointmenr_services.get_all_patient(db)


@router.get("/{appointment_id}", response_model=AppointmentSchema)
async def read_appointment_by_id(
    appointment_id: int, db: AsyncSession = Depends(async_get_db)
):
    """Получить запись на прием по ID."""
    return await appointmenr_services.get_appointment_by_id(db, appointment_id)


@router.post("/", response_model=AppointmentSchema)
async def create_appointment(
    appointment: AppointmentSchema, db: AsyncSession = Depends(async_get_db)
):
    """Создать новую запись на прием."""
    return await appointmenr_services.create_new_appointment(db, appointment)


@router.put("/{appointment_id}", response_model=AppointmentSchema)
async def update_appointment(
    appointment_id: int,
    appointment: AppointmentSchema,
    db: AsyncSession = Depends(async_get_db),
):
    """Обновить существующую запись на прием."""
    return await appointmenr_services.update_existing_appointment(
        db, appointment_id, appointment
    )


@router.delete("/{appointment_id}", response_model=dict)
async def delete_appointment(
    appointment_id: int, db: AsyncSession = Depends(async_get_db)
):
    """Удалить запись на прием."""
    return await appointmenr_services.delete_appointment_by_id(db, appointment_id)
