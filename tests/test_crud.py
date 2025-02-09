import os
import pytest_asyncio  # Импортируем pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from app.main import app
from app.database import Base, async_get_db
from app.models import Clinic, Doctor, Patient, Appointment

# Конфигурация тестовой базы данных
DATABASE_URL = os.environ.get("TEST_DATABASE_URL") # Берем из .env
engine = create_async_engine(DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Переопределяем зависимость get_db для тестов
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[async_get_db] = override_get_db

#@pytest.fixture(scope="module") #заменено на pytest_asyncio.fixture
@pytest_asyncio.fixture(scope="module")
def anyio_backend():
    return "asyncio"

#@pytest.fixture(scope="module") #заменено на pytest_asyncio.fixture
@pytest_asyncio.fixture(scope="module")
async def async_client():
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app=app)) as client:
        yield client

# Фикстура для инициализации базы данных и ее очистки
#@pytest.fixture(scope="module", autouse=True) #заменено на pytest_asyncio.fixture
@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_db():
    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Очищаем базы данных после тестов
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Создание тестовых данных (клиники, доктора, пациенты)
#@pytest.fixture
@pytest_asyncio.fixture
async def test_clinics():
    return [
        {"name": "Test Clinic 1", "address": "Test Address 1"},
        {"name": "Test Clinic 2", "address": "Test Address 2"}
    ]

#@pytest.fixture
@pytest_asyncio.fixture
async def test_doctors(test_clinics):
    async with TestingSessionLocal() as session:
        # Создаем клиники
        for clinic_data in test_clinics:
            clinic = Clinic(**clinic_data)
            session.add(clinic)
        await session.commit()
        await session.refresh(clinic)  # Обновляем объект clinic, чтобы получить clinic.id

        clinics = await session.execute(select(Clinic)).scalars().all() #получаем все клиники
        clinic_ids = [clinic.id for clinic in clinics] #создаем список id клиник

        doctors_data = [
            {"name": "Test Doctor 1", "clinic_id": clinic_ids[0]},
            {"name": "Test Doctor 2", "clinic_id": clinic_ids[1]}
        ]

        doctors = []
        for doctor_data in doctors_data:
            doctor = Doctor(**doctor_data)
            session.add(doctor)
            doctors.append(doctor)
        await session.commit()
        for doctor in doctors:
            await session.refresh(doctor)  # Получаем doctor.id
        doctor_ids = [doctor.id for doctor in doctors]
        return [{"id": doctor.id, "name": doctor.name, "clinic_id": doctor.clinic_id} for doctor in doctors]


#@pytest.fixture
@pytest_asyncio.fixture
async def test_patients(test_doctors):
    async with TestingSessionLocal() as session:
        patients_data = [
            {"name": "Test Patient 1", "doctor_id": test_doctors[0]["id"]},
            {"name": "Test Patient 2", "doctor_id": test_doctors[1]["id"]}
        ]

        patients = []
        for patient_data in patients_data:
            patient = Patient(**patient_data)
            session.add(patient)
            patients.append(patient)
        await session.commit()
        for patient in patients:
            await session.refresh(patient)  # Получаем patient.id
        return [{"id": patient.id, "name": patient.name, "doctor_id": patient.doctor_id} for patient in patients]


# Фикстура для записи на прием
#@pytest.fixture
@pytest_asyncio.fixture
async def test_appointments(test_patients, test_doctors):
    async with TestingSessionLocal() as session:

        appointments_data = [
            {"doctor_id": test_doctors[0]["id"], "patient_id": test_patients[0]["id"], "date": "2025-02-10T10:00:00"},
            {"doctor_id": test_doctors[1]["id"], "patient_id": test_patients[1]["id"], "date": "2025-02-11T11:00:00"}
        ]

        appointments = []
        for appointment_data in appointments_data:
            appointment = Appointment(**appointment_data)
            session.add(appointment)
            appointments.append(appointment)
        await session.commit()
        for appointment in appointments:
            await session.refresh(appointment)  # Получаем appointment.id

        return [{"id": appointment.id, "doctor_id": appointment.doctor_id, "patient_id": appointment.patient_id, "date": appointment.date} for appointment in appointments]

# Тесты для клиник
async def test_create_clinics_endpoint(async_client, test_clinics):
    for clinic_data in test_clinics:
        response = await async_client.post("/clinics/", json=clinic_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == clinic_data["name"]
        assert data["address"] == clinic_data["address"]

async def test_read_clinics_endpoint(async_client, test_clinics):
    for clinic_data in test_clinics:
        create_response = await async_client.post("/clinics/", json=clinic_data)
        clinic_id = create_response.json()["id"]
        response = await async_client.get(f"/clinics/{clinic_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == clinic_data["name"]
        assert data["address"] == clinic_data["address"]

async def test_list_clinics_endpoint(async_client, test_clinics):
    response = await async_client.get("/clinics/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# Тесты для докторов
async def test_create_doctor_endpoint(async_client, test_doctors):
    for doctor_data in test_doctors:
        response = await async_client.post("/doctors/", json=doctor_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == doctor_data["name"]

async def test_read_doctor_by_id_endpoint(async_client, test_doctors):
    for doctor_data in test_doctors:
        create_response = await async_client.post("/doctors/", json=doctor_data)
        doctor_id = create_response.json()["id"]
        response = await async_client.get(f"/doctors/{doctor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == doctor_data["name"]

async def test_list_doctors_endpoint(async_client, test_doctors):
    response = await async_client.get("/doctors/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# Тесты для пациентов
async def test_create_patient_endpoint(async_client, test_patients):
    for patient_data in test_patients:
        response = await async_client.post("/patients/", json=patient_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == patient_data["name"]

async def test_read_patient_by_id_endpoint(async_client, test_patients):
    for patient_data in test_patients:
        create_response = await async_client.post("/patients/", json=patient_data)
        patient_id = create_response.json()["id"]
        response = await async_client.get(f"/patients/{patient_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == patient_data["name"]

async def test_list_patients_endpoint(async_client, test_patients):
    response = await async_client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

# Тесты для записи на прием
async def test_create_appointment_endpoint(async_client, test_appointments):
    for appointment_data in test_appointments:
        response = await async_client.post("/appointments/", json=appointment_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["doctor_id"] == appointment_data["doctor_id"]
        assert data["patient_id"] == appointment_data["patient_id"]
        assert data["date"] == appointment_data["date"]

async def test_read_appointment_by_id_endpoint(async_client, test_appointments):
    for appointment_data in test_appointments:
        create_response = await async_client.post("/appointments/", json=appointment_data)
        appointment_id = create_response.json()["id"]
        response = await async_client.get(f"/appointments/{appointment_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["doctor_id"] == appointment_data["doctor_id"]
        assert data["patient_id"] == appointment_data["patient_id"]
        assert data["date"] == appointment_data["date"]

async def test_list_appointments_endpoint(async_client, test_appointments):
    response = await async_client.get("/appointments/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0