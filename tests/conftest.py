import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from faker import Faker
from app.main import app
from app.database import Base
from app.models import Doctor, Clinic, Patient, Appointment

fake = Faker()

# Настройка базы данных для тестов
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/test_database"
engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Фикстура для создания базы перед запуском тестов
@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Фикстура для создания сессии БД
@pytest.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # Откатываем изменения после каждого теста


# Фикстура для клиента FastAPI
@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac


# Фикстуры для тестовых данных
@pytest.fixture
async def fake_clinic(db_session: AsyncSession):
    clinic = Clinic(name=fake.company(), address=fake.address())
    db_session.add(clinic)
    await db_session.commit()
    await db_session.refresh(clinic)
    return clinic


@pytest.fixture
async def fake_doctor(db_session: AsyncSession, fake_clinic: Clinic):
    doctor = Doctor(name=fake.name(), clinic_id=fake_clinic.id)
    db_session.add(doctor)
    await db_session.commit()
    await db_session.refresh(doctor)
    return doctor


@pytest.fixture
async def fake_patient(
    db_session: AsyncSession, fake_doctor: Doctor, fake_clinic: Clinic
):
    patient = Patient(
        name=fake.name(), doctor_id=fake_doctor.id, clinic_id=fake_clinic.id
    )
    db_session.add(patient)
    await db_session.commit()
    await db_session.refresh(patient)
    return patient


@pytest.fixture
async def fake_appointment(
    db_session: AsyncSession, fake_doctor: Doctor, fake_patient: Patient
):
    appointment = Appointment(
        doctor_id=fake_doctor.id, patient_id=fake_patient.id, date=fake.date_time()
    )
    db_session.add(appointment)
    await db_session.commit()
    await db_session.refresh(appointment)
    return appointment
