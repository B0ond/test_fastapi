from typing import AsyncGenerator
import asyncio
import pytest
import pytest_asyncio
import pytest_postgresql
import pytest_postgresql.janitor
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

from dotenv import load_dotenv

from app.database import Base, async_get_db
from app.main import app  # Ваше приложение FastAPI

load_dotenv()


# Создаем асинхронный engine с использованием pytest-postgresql
@pytest.fixture(scope="function")
def async_engine(postgresql: pytest_postgresql.janitor):
    engine = create_async_engine(
        url=str(postgresql.url()), echo=True, poolclass=NullPool
    )
    yield engine
    asyncio.run(engine.dispose())


# Фикстура для создания и удаления таблиц
@pytest_asyncio.fixture(
    scope="function", autouse=True
)  # Изменили область на "function"
async def create_test_database(async_engine):
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    finally:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


# Фикстура для асинхронной сессии
@pytest_asyncio.fixture
async def test_db(async_engine) -> AsyncGenerator[AsyncSession, None]:
    TestAsyncSessionLocal = sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with TestAsyncSessionLocal() as session:
        yield session
        await session.rollback()  # Откат изменений после каждого теста


# Фикстура для клиента FastAPI
@pytest_asyncio.fixture
async def async_client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        base_url="http://test",
        transport=ASGITransport(app=app),  # Use ASGITransport
    ) as client:
        app.dependency_overrides[async_get_db] = lambda: test_db
        yield client
        app.dependency_overrides.clear()
