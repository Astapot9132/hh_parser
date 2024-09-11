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
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')

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



class ProgressForUpload:
    progress = 0

    """
     Класс для прогресс-бара при загрузке вакансий,
     Интересно, что если делать экземпляр этого класса то по личным мотивам после 1 запуска экземпляр
     принимает значение 0 и не меняет его вообще, тоже самое происходит при определении бара через глобалку
     
     Хотя судя по тестам и этот прогрессбар подтупливает..
     """
    @classmethod
    def get_progress(cls):
        return cls.progress

    @classmethod
    def set_progress(cls, value):
        if value:
            cls.progress = value
        return value

    @classmethod
    def reset_progress(cls):
        cls.progress = 0

