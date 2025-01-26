from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')

# SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:AAAaaa111@localhost/misa_db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
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
