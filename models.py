import asyncio
import datetime
import uuid
from sqlalchemy import Uuid
from sqlalchemy import String, select, Boolean, Float, ForeignKey, Date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, validates
from config import *

if DEVELOPING:
    DB_URL = f"postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_NAME}"
else:
    DB_URL = f"postgresql+asyncpg://{POSTGRES_LOGIN}:{POSTGRES_PASSWORD}@{POSTGRES_DOCKER_HOST}:{POSTGRES_PORT}/{POSTGRES_DOCKER_NAME}"



engine = create_async_engine(
    DB_URL,
    # echo=True,
)

new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class City(Model):
    __tablename__ = 'cities'
    hh_id: Mapped[int] = mapped_column(primary_key=True)
    city_name: Mapped[str]
    country_name: Mapped[str]


class Role(Model):
    __tablename__ = 'professional_roles'
    hh_id: Mapped[int] = mapped_column(primary_key=True)
    profession_role: Mapped[str]
    category: Mapped[str]


class Vacancy(Model):
    # По хорошему столбик с валютой следовало бы вынести в отдельную колонку и зарплаты сделать интом,
    # а также продумать связи city и professional_role для будущего взаимодействия
    __tablename__ = 'vacancies'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    url: Mapped[str] = mapped_column(String(256))
    city: Mapped[str] = mapped_column(String(64))
    professional_role: Mapped[str] = mapped_column(String(64))
    min_salary: Mapped[str] = mapped_column(String(16), nullable=True)
    max_salary: Mapped[str] = mapped_column(String(16), nullable=True)
    request_uuid: Mapped[uuid] = mapped_column(Uuid, nullable=False, index=True)
    created_at: Mapped[datetime.datetime] # это поле можно будет применить для дальнейшей очистки бд




async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
