import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import ClinicSchema
from ..models import Clinic

router = APIRouter(prefix="/clinics", tags=["clinics 🏥"])
logger = logging.getLogger(__name__)


async def get_all_clinics_from_db(db: AsyncSession):
    """Получить список всех клиник."""
    result = await db.execute(select(Clinic))
    return result.scalars().all()

async def get_clinic_by_id(db: AsyncSession, clinic_id: int):
    """Получить клинику по ID."""
    clinic = await db.get(Clinic, clinic_id)
    if clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic

async def get_clinic_by_name(db: AsyncSession, clinic_name: str):
    """Получить клинику по имени."""
    result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
    clinic = result.scalars().one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic name not found")
    return clinic

async def create_new_clinic(db: AsyncSession, clinic_data):
    """Создать новую клинику."""
    db_clinic = Clinic(name=clinic_data.name, address=clinic_data.address)
    db.add(db_clinic)
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic

async def update_existing_clinic(db: AsyncSession, clinic_id: int, clinic_data):
    """Обновить информацию о клинике."""
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    
    db_clinic.name = clinic_data.name
    db_clinic.address = clinic_data.address
    
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic

async def delete_clinic_by_id(db: AsyncSession, clinic_id: int):
    """Удалить клинику."""
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")

    await db.delete(db_clinic)
    await db.commit()
    
    logger.info("Clinic with id=%s has been deleted.", clinic_id)
    return {"detail": f"Clinic with id={clinic_id} deleted successfully"}

# вывод всех клиник
@router.get("/clinics/", response_model=list[ClinicSchema])
async def get_all_clinics(db: AsyncSession = Depends(async_get_db)):
    clinics = await db.execute(select(Clinic))
    return clinics.scalars().all()


@router.get("/{clinic_id}", response_model=ClinicSchema)
async def read_clinic_by_id(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    """Получить клинику по ID."""
    return await get_clinic_by_id(db, clinic_id)

@router.get("/name/{clinic_name}", response_model=ClinicSchema)
async def read_clinic_by_name(clinic_name: str, db: AsyncSession = Depends(async_get_db)):
    """Получить клинику по имени."""
    return await get_clinic_by_name(db, clinic_name)

@router.post("/", response_model=ClinicSchema)
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    """Создать новую клинику."""
    return await create_new_clinic(db, clinic)

@router.put("/{clinic_id}", response_model=ClinicSchema)
async def update_clinic(clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    """Обновить информацию о клинике."""
    return await update_existing_clinic(db, clinic_id, clinic)

@router.delete("/{clinic_id}", response_model=dict)
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    """Удалить клинику."""
    return await delete_clinic_by_id(db, clinic_id)