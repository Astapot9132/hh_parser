import asyncio
import datetime
import time
import uuid
from copy import deepcopy
from pprint import pprint

import pygsheets
import requests
from .repository import CityRepository, RolesRepository, VacancyRepository
from fastapi.responses import RedirectResponse
import httpx
from fastapi import APIRouter, Depends, Request
from starlette import status
from config import *
import aiohttp

router = APIRouter(
    prefix='/vacancies'
)


@router.get("/")
async def hello(request: Request):
    """ Начальная страница """
    return templates.TemplateResponse(name='main.html', context={'request': request})


@router.post('/load_cities')
async def load_cities(request: Request):
    """ Post запрос для обновления списка городов и юидов """
    async with httpx.AsyncClient() as client:
        cities = await client.get('https://api.hh.ru/areas')
        result = []

        for c in cities.json():
            for region in c['areas']:
                if region['areas']:
                    for city in region['areas']:
                        result.append({'country_name': c['name'], 'hh_id': int(city['id']), 'city_name': city['name'].lower()})
                else:
                    result.append({'country_name': c['name'], 'hh_id': int(region['id']), 'city_name': region['name'].lower()})
        await CityRepository.cities_add(result)
    return RedirectResponse('/vacancies/', status_code=status.HTTP_302_FOUND)


@router.post('/load_roles')
async def load_roles(request: Request):
    """ Post запрос для обновления специальностей """
    async with httpx.AsyncClient() as client:
        roles = await client.get('https://api.hh.ru/professional_roles')
        r = []
        ids = {}
        for category in roles.json()['categories']:
            for profession in category['roles']:
                profession_id = profession['id']
                if not ids.get(profession_id):
                    r.append(
                        {'category': category['name'], 'profession_role': profession['name'].lower(), 'hh_id': int(profession_id)})
                    ids[profession_id] = 1
        await RolesRepository.roles_add(r)
        return RedirectResponse('/vacancies/', status_code=status.HTTP_302_FOUND)


@router.post('/load_gsheets/{uuid:str}')
async def load_gsheets(uuid: str):
    """
    Post запрос для загрузки данных в google sheets

    тут надо добавить celery как фоновую задачу и не париться,
    поскольку длинная обработка именно в удалении + вставке записей

    """
    try:
        start = datetime.datetime.now()
        client = pygsheets.authorize(service_account_file="credentials.json")
        spreadsheet_id = PGSHEETS_ID
        spreadsht = client.open(PGSHEETS_NAME)
        m = spreadsht.worksheet_by_title(PGSHEETS_LIST_NAME)
        values = await VacancyRepository.vacancies_get_by_uuid(uuid)
        stop_1 = datetime.datetime.now() - start
        print('stop_1 ', stop_1)
        start_values = ['Название', 'Ссылка', 'Город', 'Специальность', 'Минимальная зарплата', 'Максимальная зарплата']
        real_values = list(map(lambda x: [x.name, x.url, x.city, x.professional_role, x.min_salary, x.max_salary], values))
        real_values.insert(0, start_values)
        stop_2 = datetime.datetime.now() - start
        print('stop_2 ', stop_2)
        m.clear()
        m.insert_rows(0, len(real_values) + 1, real_values)
        end = datetime.datetime.now() - start
        print('google sheets load: ', end)
        #Это не лучший вариант, стоит потом переделать
        return RedirectResponse('/vacancies/', status_code=status.HTTP_302_FOUND)
    except Exception as e:
        logger.info(f'Возникла ошибка при отправке в гугл таблицы: {e}')
        send_tg(e)
        return RedirectResponse('/vacancies/', status_code=status.HTTP_302_FOUND)

@router.get('/get_vacancies/')
async def get_vacancies(request: Request, area: str = '', roles: str = '', text: str = '', page: int = 0, new: bool = True):
    """

    Получение списка вакансий по заданным параметрам.

    В случае если будут найдены вакансии, они добавятся в БД

     """
    try:
        url = 'https://api.hh.ru/vacancies'
        #Формирование параметров запросов на ххру
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
        async with httpx.AsyncClient() as client:
            result = await client.get(url, params=params)
        print(result.json()['pages'])

        #Пагинация
        pages_count = result.json()['pages'] - 1
        page_range = list(filter(lambda x: 0 <= x <= pages_count, list(range(int(page) - 3, int(page) + 4))))
        previous = True if int(page) > 0 else False
        next = True if int(page) < pages_count else False
        now = datetime.datetime.now().replace(microsecond=0)
        request_uuid = uuid.uuid4()

        #Формирование таблицы
        vacancies = []
        for v in result.json()['items']:
            vacancies.append({'name': v['name'],
                              'url': v['alternate_url'],
                              'city': v['area']['name'],
                              'professional_role': ', '.join([role['name'] for role in v['professional_roles']]),
                              'min_salary': f"{v['salary']['from']} {v['salary']['currency']}",
                              'max_salary': f"{v['salary']['to']} {v['salary']['currency']}",
                              'created_at': now,
                              'request_uuid': request_uuid
                              })
        pprint(result.json().keys())

        #Добавление в БД
        if vacancies and new:
            start = datetime.datetime.now()
            vacancies_for_bd = vacancies.copy()
            # print(result.json()['pages'])



            tasks = {}
            result_vacancies = []
            async with httpx.AsyncClient() as client:
                for p in range(1,
                               result.json()['pages'],
                               ):
                    #дип копи формирует новый объект и он не перетреся при создании задач
                    new_params = deepcopy(params)
                    new_params.update({'page': p})
                    tasks[p] = asyncio.create_task(client.get(url, params=new_params))
                    # необходимо засыпать иначе будут отваливаться некоторые запросы
                    await asyncio.sleep(0.1)
                for p in range(1, result.json()['pages']):
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
            await VacancyRepository.vacancies_add(vacancies_for_bd)
            end = datetime.datetime.now() - start
            print(end)
        return templates.TemplateResponse('vacancies.html', context={
            'request': request,
            'vacancies': vacancies,
            'page_range': page_range,
            'previous': previous,
            'next': next,
            'page': page,
            'text': text,
            'roles': roles,
            'area': area,
            'request_uuid': request_uuid,
        })
    except Exception as e:
        send_tg(e)
        logger.info(f'При запросе на получение вакансий возникла ошибка {e}')
        return RedirectResponse('/vacancies/', status_code=status.HTTP_302_FOUND)



