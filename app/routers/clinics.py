import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import ClinicSchema
from ..models import Clinic

router = APIRouter(prefix="/clinics", tags=["clinics 🏥"])
logger = logging.getLogger(__name__)


# вывод всех клиник
@router.get("/clinics/", response_model=list[ClinicSchema])
async def get_all_clinics(db: AsyncSession = Depends(async_get_db)):
    clinics = await db.execute(select(Clinic))
    return clinics.scalars().all()


# вывод клиник по id
@router.get("/clinics/{clinic_id}", response_model=ClinicSchema)
async def read_clinic_by_id(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    clinic = await db.get(Clinic, clinic_id)
    if clinic is None:
        raise HTTPException(status_code=404, detail="Clinic not found")
    return clinic


# вывод клиник по имени
@router.get("/clinics/name/{clinic_name}", response_model=ClinicSchema)
async def read_clinic_by_name(
    clinic_name: str, db: AsyncSession = Depends(async_get_db)
):
    result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
    clinic = result.scalars().one_or_none()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clinic name not found")
    return clinic


# создание клиники
@router.post("/clinics/", response_model=ClinicSchema)
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    db_clinic = Clinic(name=clinic.name, address=clinic.address)
    db.add(db_clinic)
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic


# изменнение клиники
@router.put("/clinics/{clinic_id}", response_model=ClinicSchema)
async def update_clinic(
    clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)
):
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    db_clinic.name = clinic.name
    db_clinic.address = clinic.address
    await db.commit()
    await db.refresh(db_clinic)
    return db_clinic


# удаление клиники
@router.delete("/clinics/{clinic_id}", response_model=dict)
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    db_clinic = await db.get(Clinic, clinic_id)
    if not db_clinic:
        raise HTTPException(status_code=404, detail="Clinic not found")
    await db.delete(db_clinic)
    await db.commit()
    logger.info("Clinic with id=%s has been deleted.", clinic_id)
    return {"detail": f"Clinic with id={clinic_id} deleted successfully"}
