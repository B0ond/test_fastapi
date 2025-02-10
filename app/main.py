from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import clinics, doctors, patients, appointments


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables():
    async with engine.begin() as conn:
        logger.info("Создание таблиц...")
        await conn.run_sync(Base.metadata.create_all) 
        logger.info("Таблицы созданы")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Запуск приложения...")
    await create_tables()  # Выполняется при старте приложения
    yield
    logger.info("Остановка приложения...")
    await engine.dispose()  # Выполняется при завершении работы приложения


app = FastAPI(
    title="MISA Prototype",
    description="This is an ASGI MISA prototype for a test assignment",
    docs_url="/",
    lifespan=lifespan,
)

app.include_router(doctors.router)
app.include_router(patients.router)
app.include_router(clinics.router)
app.include_router(appointments.router)
