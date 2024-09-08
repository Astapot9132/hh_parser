
from sqlalchemy import select, delete, insert, update

from models import new_session, City, Vacancy, Role

class CityRepository:
    @classmethod
    async def cities_add(cls, cities: list[dict]):
        async with new_session() as session:
            query_delete = delete(City)
            await session.execute(query_delete)
            query_insert = insert(City).values(cities)
            await session.execute(query_insert)
            await session.commit()

    @classmethod
    async def cities_get(cls):
        async with new_session() as session:
            query = select(City)
            result = await session.execute(query)
            cities = result.scalars().all()
            return cities



    @classmethod
    async def city_get_id_by_name(cls, name):
        async with new_session() as session:
            query_exact = select(City).where(City.city_name==name)
            result = await session.execute(query_exact)
            city = result.scalars().first()
            if city:
                return city.hh_id
            query = select(City).where(City.city_name.like(f'%{name}%'))
            result = await session.execute(query)
            city = result.scalars().first()
            if city:
                return city.hh_id
            return

class RolesRepository:
    @classmethod
    async def roles_add(cls, roles: list[dict]):
        async with new_session() as session:
            query_delete = delete(Role)
            await session.execute(query_delete)
            query_insert = insert(Role).values(roles)
            await session.execute(query_insert)
            await session.commit()

    @classmethod
    async def role_get_id_by_name(cls, name):
        async with new_session() as session:
            query_exact = select(Role).where(Role.profession_role==name)
            result = await session.execute(query_exact)
            role = result.scalars().first()
            if role:
                return role.hh_id
            query = select(Role).where(Role.profession_role.like(f'%{name}%'))
            result = await session.execute(query)
            role = result.scalars().first()
            if role:
                return role.hh_id
            return

class VacancyRepository:

    @classmethod
    async def vacancies_add(cls, vacancies: list[dict]):
        async with new_session() as session:
            query_insert = insert(Vacancy).values(vacancies)
            await session.execute(query_insert)
            await session.commit()

    @classmethod
    async def vacancies_get_by_uuid(cls, uuid: str):
        async with new_session() as session:
            query_insert = select(Vacancy).where(Vacancy.request_uuid==uuid)
            result = await session.execute(query_insert)
            vacs = result.scalars().all()
            return vacs