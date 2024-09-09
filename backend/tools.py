import asyncio
import uuid
from copy import deepcopy

import httpx
from config import *
from .repository import VacancyRepository, CityRepository, RolesRepository
import requests


async def get_first_params(text, page, area, roles):
    params = {
        'text': text,
        'page': page,
        'per_page': 100,
        'period': 2,
        'order_by': 'salary_asc',
        'only_with_salary': 'true',
    }
    if area:
        city_task = asyncio.create_task(CityRepository.city_get_id_by_name(area.lower()))
    if roles:
        role_task = asyncio.create_task(RolesRepository.role_get_id_by_name(roles.lower()))
    if area:
        city = await city_task
        if city:
            params.update({'area': city})
    if roles:
        role = await role_task
        if role:
            params.update({'professional_role': role})
    return params

async def get_vacancies_for_bd(first_request, first_vacancies, first_params, now, request_uuid: uuid) -> list[dict]:
    """
     Функция, формирующая полный список отсортированных вакансий для записи в БД через запросы ко всем страницам

     """
    url = 'https://api.hh.ru/vacancies'
    vacancies_for_bd = first_vacancies.copy()
    # print(result.json()['pages'])
    tasks = {}
    result_vacancies = []
    async with httpx.AsyncClient() as client:
        for p in range(1,
                       first_request.json()['pages'],
                       ):
            # дип копи формирует новый объект и он не перетреся при создании задач
            new_params = deepcopy(first_params)
            new_params.update({'page': p})
            tasks[p] = asyncio.create_task(client.get(url, params=new_params))
            # необходимо засыпать иначе будут отваливаться некоторые запросы
            await asyncio.sleep(0.1)
        for p in range(1, first_request.json()['pages']):
            try:
                a = await tasks[p]
                result_vacancies.extend(a.json()['items'])
            except Exception as e:
                send_tg(e)
                logger.info(f'Возникла ошибка запроса вакансий: {e}')
        for v in result_vacancies:
            vacancies_for_bd.append({'name': v['name'],
                                     'url': v['alternate_url'],
                                     'city': v['area']['name'],
                                     'professional_role': ', '.join(
                                         [role['name'] for role in v['professional_roles']]),
                                     'min_salary': f"{v['salary']['from']} {v['salary']['currency']}",
                                     'max_salary': f"{v['salary']['to']} {v['salary']['currency']}",
                                     'created_at': now,
                                     'request_uuid': request_uuid
                                     })
    print(len(vacancies_for_bd))
    return vacancies_for_bd

