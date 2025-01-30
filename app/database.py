from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_TYPE = os.getenv("DB_TYPE", "+asyncpg")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "postgres")


DATABASE_URL = f"postgresql{DB_TYPE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

async def async_get_db():
    async with AsyncSessionLocal() as db:  # Создаём асинхронную сессию
        try:
            yield db  # Передаём её в зависимости
        finally:
            await db.close()  # Закрываем сессию после использования
