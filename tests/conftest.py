# tests/conftest.py
import os

import pytest_asyncio
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import delete
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.database import Base, async_get_db
from app.main import app as fastapi_app
from app.models import Clinic, Doctor, Patient, Appointment


load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    await create_tables()
    

@pytest_asyncio.fixture(autouse=True)
async def clear_db():
    engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
             await conn.execute(delete(table))


@pytest_asyncio.fixture()
async def override_get_db():
    engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)
    async with TestingSessionLocal(bind=engine) as session:  # db: AsyncSession = TestingSessionLocal()
        yield session


fastapi_app.dependency_overrides[async_get_db] = override_get_db


@pytest_asyncio.fixture()
async def app() -> FastAPI:
    return fastapi_app


@pytest_asyncio.fixture()
async def async_client(app: FastAPI) -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


# Фикстуры для создания объектов
@pytest_asyncio.fixture()
async def clinics(db: AsyncSession):
    clinic1 = Clinic(name="Test Clinic 1", address="Test Address 1")
    clinic2 = Clinic(name="Test Clinic 2", address="Test Address 2")
    db.add_all([clinic1, clinic2])
    await db.commit()
    await db.refresh(clinic1)
    await db.refresh(clinic2)
    return [clinic1, clinic2]


@pytest_asyncio.fixture()
async def doctors(db: AsyncSession, clinics):
    doctor1 = Doctor(name="Test Doctor 1", clinic_id=clinics[0].id)
    doctor2 = Doctor(name="Test Doctor 2", clinic_id=clinics[1].id)
    db.add_all([doctor1, doctor2])
    await db.commit()
    await db.refresh(doctor1)
    await db.refresh(doctor2)
    return [doctor1, doctor2]


@pytest_asyncio.fixture()
async def patients(db: AsyncSession):
    patient1 = Patient(name="Test Patient 1")
    patient2 = Patient(name="Test Patient 2")
    db.add_all([patient1, patient2])
    await db.commit()
    await db.refresh(patient1)
    await db.refresh(patient2)
    return [patient1, patient2]


@pytest_asyncio.fixture()
async def appointments(db: AsyncSession, doctors, patients):
    appointment1 = Appointment(doctor_id=doctors[0].id, patient_id=patients[0].id, date="2024-01-01")
    appointment2 = Appointment(doctor_id=doctors[1].id, patient_id=patients[1].id, date="2024-01-02")
    db.add_all([appointment1, appointment2])
    await db.commit()
    await db.refresh(appointment1)
    await db.refresh(appointment2)
    return [appointment1, appointment2]


@pytest_asyncio.fixture()
async def db():
    """Фикстура для создания сессии БД."""
    engine = create_async_engine(DATABASE_URL, echo=True, poolclass=NullPool)  # Перемещено сюда
    async with TestingSessionLocal(bind=engine) as session:  # Тут мы привязываем TestingSessionLocal к engine
        yield session