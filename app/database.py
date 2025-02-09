import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Получаем конфигурацию базы данных
DB_TYPE = os.getenv("DB_TYPE")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "db")  # Значение по умолчанию для локальной разработки
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Используем переменную окружения TESTING для определения, использовать ли тестовую базу данных
TESTING = os.getenv("TESTING") == "True"
print(f"TESTING: {TESTING}")

DATABASE_URL = (
    f"postgresql{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")  # Получаем из .env

# Используем переменную для подключения к базе данных
DATABASE_URL_TO_USE = TEST_DATABASE_URL if TESTING and TEST_DATABASE_URL else DATABASE_URL
print(f"Using database URL: {DATABASE_URL_TO_USE}")


# Настроим engine и сессии
engine = create_async_engine(DATABASE_URL_TO_USE, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

async def async_get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()