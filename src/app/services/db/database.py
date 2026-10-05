from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.app.services.db.config import settings

DATABASE_URL = URL.create(  # автоматически экранирует (URL-кодирует) все спецсимволы
    drivername="postgresql+psycopg",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"connect_timeout": 5},  # если БД не отвечает
)

SessionLocal = sessionmaker(
    bind=engine,
)

# Базовый класс для моделей(таблиц)
class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()