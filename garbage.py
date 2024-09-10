import asyncio
import csv
import datetime
import json
from io import StringIO
from pprint import pprint
from copy import deepcopy
import httpx

from config import *
import pygsheets
import requests

""" файл для исследовательских тестов :) """
#
# res = requests.get('https://api.hh.ru/areas')
# counter = 0
# # pprint(res.json())
# result = []
#
# for c in res.json():
#     for region in c['areas']:
#         if region['areas']:
#             for city in region['areas']:
#                 result.append({'country_name': c['name'], 'hh_id': city['id'], 'city_name': city['name']})
#         else:
#             result.append({'country_name': c['name'], 'hh_id': region['id'], 'city_name': region['name']})
# pprint(result)
#
# # print(len(result))
#
#
# def get_vacancies(page=0):
#     params = {
#         'text': '',
#         # 'area': '',
#         'page': page,
#         'per_page': 10,
#         'period': 2,
#         # 'professional_role': 'Юрист'
#     }
#
#     req = requests.get('https://api.hh.ru/vacancies', params)
#     data = req.json()
#     return data
# v = get_vacancies()
#
#
# async def a_get(pages):
#     params = {
#         'text': '',
#         'area': 1,
#         'page': '',
#         'per_page': 100,
#         'period': 2,
#         'professional_role': 146
#     }
#     tasks = []
#     result = []
#     async with httpx.AsyncClient() as c:
#         for p in range(pages):
#
#             new_params = deepcopy(params)
#             new_params.update({'page': p})
#             tasks.append(asyncio.create_task(c.get('https://api.hh.ru/vacancies', params=new_params)))
#         for task in tasks:
#             r = await task
#             pprint(r.status_code)
#         await asyncio.sleep(0.1)
#
#
# asyncio.run(a_get(5))
# def get_professional_roles():
#     res = requests.get('https://api.hh.ru/professional_roles')
#     return res.json()
#
# def get_order_by():
#     res = requests.get('https://api.hh.ru/dictionaries')
#     return res.json()

# pprint(get_order_by())
#
# def get_industries():
#     res = requests.get('https://api.hh.ru/industries')
#     return res.json()
#
# # pprint(get_industries())
#
# # pprint(get_professional_roles())
# r = []
# ids = {}
# for category in get_professional_roles()['categories']:
#     for profession in category['roles']:
#         profession_id = profession['id']
#         if not ids.get(profession_id):
#             r.append({'category': category['name'], 'profession_role': profession['name'], 'hh_id': profession_id})
#             ids[profession_id] = 1
# pprint(r)
# print(len(r))
# #
#
# print(len(r))
# ids = set()
# for c in r:
#     if c['hh_id'] in ids:
#         print(c['hh_id'])
#     ids.add(c['hh_id'])
# print(len(ids))

# client = pygsheets.authorize(service_account_file="credentials_new.json")
# spreadsheet_id = PGSHEETS_ID
# spreadsht = client.open("TEST")
# m = spreadsht.worksheet_by_title('testpage')
# values = m.get_all_values(value_render="FORMATTED_VALUE")
# sheet_id = m.jsonSheet['properties']['sheetId']
# url = 'https://docs.google.com/spreadsheets/d/' + spreadsheet_id + '/gviz/tq?tqx=out:csv&gid=' + str(sheet_id)
# res = requests.get(url, headers={'Authorization': 'Bearer ' + client.oauth.token})
# f = StringIO(res.text)
# reader = csv.reader(f, delimiter=',')
# ar = [row for row in reader]
# # m.delete_rows(2, len(ar) + 1)
# m.clear(2)
# m.insert_rows(1, 2, [['a', 'b', 'c'], ['b', 'c']])

# print(spreadsht)
#
# dict_ = [{'a':'b', 'c': 'b'}, {'a': 'b', 'D': 'b'}]
#

# result = requests.post('http://localhost:8000/start-task')
# print(result.json())
# print(result)