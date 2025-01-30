import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database import async_get_db
from ..schemas import ClinicSchema
from ..models import Clinic

router = APIRouter(prefix="/clinics", tags=["clinics 🏥"])
logger = logging.getLogger(__name__)


@router.get("/clinics/{clinic_id}", response_model=ClinicSchema)
async def read_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        clinic = result.scalars().first()
        if clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")
        return clinic
    except Exception as e:
        logger.error(f"Error reading clinic with id={clinic_id}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Clinic  with id={clinic_id} not found"
        )


@router.get("/clinics/name/{clinic_name}", response_model=ClinicSchema)
async def read_clinic_by_name(
    clinic_name: str, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.name == clinic_name))
        clinic = result.scalars().first()
        if not clinic:
            raise HTTPException(status_code=404, detail="Clinic name not found")
        return clinic
    except Exception as e:
        logger.error(f"Error reading clinic by name={clinic_name}: {e}")
        raise HTTPException(
            status_code=404, detail=f"Clinic  with name={clinic_name} not found"
        )


@router.post("/clinics/", response_model=ClinicSchema)
async def create_clinic(clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)):
    try:
        db_clinic = Clinic(name=clinic.name, address=clinic.address)
        db.add(db_clinic)
        await db.commit()
        await db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        logger.error(f"Error creating clinic: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/clinics/{clinic_id}", response_model=ClinicSchema)
async def update_clinic(
    clinic_id: int, clinic: ClinicSchema, db: AsyncSession = Depends(async_get_db)
):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        db_clinic = result.scalars().first()
        if db_clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")
        db_clinic.name = clinic.name
        db_clinic.address = clinic.address
        await db.commit()
        await db.refresh(db_clinic)
        return db_clinic
    except Exception as e:
        logger.error(f"Error updating clinic with id={clinic_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.delete("/clinics/{clinic_id}", response_model=dict)
async def delete_clinic(clinic_id: int, db: AsyncSession = Depends(async_get_db)):
    try:
        result = await db.execute(select(Clinic).filter(Clinic.id == clinic_id))
        db_clinic = result.scalars().first()
        if db_clinic is None:
            raise HTTPException(status_code=404, detail="Clinic not found")

        await db.delete(db_clinic)
        await db.commit()

        logger.info(f"Clinic with id={clinic_id} has been deleted.")
        return {"detail": f"Clinic with id={clinic_id} deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting clinic with id={clinic_id}: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal Server Error")
