import logging
import os
from starlette.templating import Jinja2Templates
import dotenv

dotenv.load_dotenv()


# параметры для переопределения в .env
# БД хост
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# БД порт
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
# БД логин
POSTGRES_LOGIN = os.getenv('POSTGRES_LOGIN')
# БД пароль
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# БД название базы локально
POSTGRES_NAME = os.getenv('POSTGRES_NAME')
# БД название базы в докере
POSTGRES_DOCKER_NAME = os.getenv('POSTGRES_DOCKER_NAME')
# БД хост при запуске из докера
POSTGRES_DOCKER_HOST = os.getenv('POSTGRES_DOCKER_HOST')
# Секретный ключ приложения
SECRET_KEY = os.getenv('SECRET_KEY')
# Порт приложения
APP_PORT = os.getenv('APP_PORT')
# ID google sheets
PGSHEETS_ID = os.getenv('PGSHEETS_ID')
# Название файла
PGSHEETS_NAME = os.getenv('PGSHEETS_NAME')
# Название листа с данными для записи
PGSHEETS_LIST_NAME = os.getenv('PGSHEETS_LIST_NAME')
#


# параметр для использования локальной БД
DEVELOPING = False

TG_ADRESSES = ['1']

logger = logging.getLogger('main')
handler = logging.StreamHandler()
logging.basicConfig(filename='hh_parser_log.txt', level=logging.INFO)

templates = Jinja2Templates(directory='templates')
# REDIS_DB = redis.from_url("redis://redis:6379/1", decode_responses=True)


def send_tg(message):
    # Функция send_tg по идее должна уведомлять об ошибках в телеграмме
    for dev_id in TG_ADRESSES:
        try:
            print(f'Пользователю {dev_id} отправлено: {message}')
        except Exception as e:
            print(e)
            logger.info(e)
    return