import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import async_get_db
from ..schemas import ClinicSchema

# from ..models import Clinic
from ..services import clinic_services

router = APIRouter(prefix="/clinics", tags=["clinics 🏥"])
logger = logging.getLogger(__name__)


# вывод всех клиник
@router.get("/", response_model=list[ClinicSchema])
async def get_all_clinics(db: AsyncSession = Depends(async_get_db)):
    return await clinic_services.get_all_clinics_from_db(db)


@router.get("/{clinic_id}", response_model=ClinicSchema)
async def read_clinic_by_id(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    """Получить клинику по ID."""
    return await clinic_services.get_clinic_by_id(db, clinic_id)


@router.get("/name/{clinic_name}", response_model=ClinicSchema)
async def read_clinic_by_name(
    clinic_name: str, db: AsyncSession = Depends(async_get_db)
):
    """Получить клинику по имени."""
    return await clinic_services.get_clinic_by_name(db, clinic_name)


@router.post("/", response_model=ClinicSchema)
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    """Создать новую клинику."""
    return await clinic_services.create_new_clinic(db, clinic)


@router.put("/{clinic_id}", response_model=ClinicSchema)
async def update_clinic(
    clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)
):
    """Обновить информацию о клинике."""
    return await clinic_services.update_existing_clinic(db, clinic_id, clinic)


@router.delete("/{clinic_id}", response_model=dict)
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    """Удалить клинику."""
    return await clinic_services.delete_clinic_by_id(db, clinic_id)
