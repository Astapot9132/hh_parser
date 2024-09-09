import asyncio
import datetime
import time
import uuid
from copy import deepcopy
from pprint import pprint
from .tools import *
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
        params = await get_first_params(text, page, area, roles)

        # Получение первой страницы вакансий
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

        #Добавление в БД
        if vacancies and new:
            start = datetime.datetime.now()
            # К сожалению запрос пришлось замедлить, иначе при ассинхронных запросах иногда возникают ошибки
            vacancies_for_bd = await get_vacancies_for_bd(result, vacancies, params, now, request_uuid)
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



