import asyncio
import datetime
import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import pygsheets
from celery import Celery
from celery.schedules import crontab
from config import *

from backend.repository import VacancyRepository

celery_app = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL'), backend=os.getenv('CELERY_RESULT_BACKEND'), broker_connection_retry_on_startup=True)


@celery_app.task(name='work_with_gsheets')
def work_with_gsheets(uuid):
    start = datetime.datetime.now()
    client = pygsheets.authorize(service_account_file="credentials.json")
    spreadsheet_id = PGSHEETS_ID
    spreadsht = client.open(PGSHEETS_NAME)
    m = spreadsht.worksheet_by_title(PGSHEETS_LIST_NAME)
    loop = asyncio.get_event_loop()
    values = loop.run_until_complete(VacancyRepository.vacancies_get_by_uuid(uuid))
    stop_1 = datetime.datetime.now() - start
    print('stop_1 ', stop_1)
    start_values = ['Название', 'Ссылка', 'Город', 'Специальность', 'Минимальная зарплата', 'Максимальная зарплата']
    real_values = list(map(lambda x: [x.name, x.url, x.city, x.professional_role, x.min_salary, x.max_salary], values))
    real_values.insert(0, start_values)
    stop_2 = datetime.datetime.now() - start
    print('stop_2 ', stop_2)
    m.clear()
    m.insert_rows(0, len(real_values) + 1, real_values)
    return True