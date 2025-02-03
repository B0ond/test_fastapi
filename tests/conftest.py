import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient
from app.main import app
from app.database import get_db, Base

# Настройка тестовой базы данных
TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost/test_db"

# Создаём асинхронный движок БД без пула подключений
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)

# Создаём асинхронный sessionmaker
TestingSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """Создание и удаление схемы БД"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_session():
    """Создаёт новую сессию БД на каждый тест"""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # Откатываем изменения после каждого теста

@pytest.fixture(scope="function")
async def client(db_session):
    """Тестовый клиент с переопределённой зависимостью get_db"""
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
