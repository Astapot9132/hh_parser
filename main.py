import datetime
import time

from config import *
from contextlib import asynccontextmanager
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from backend.router import router as vacancy_router
from models import create_tables, delete_tables
from fastapi.staticfiles import StaticFiles

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await delete_tables()
    await create_tables()
    yield

app = FastAPI(
    lifespan=lifespan,
)
app.include_router(vacancy_router)
app.mount("/static", StaticFiles(directory="static"), name="static")

#


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Datetime: {datetime.datetime.now().replace(microsecond=0)}")
    start = time.time()
    try:
        response = await call_next(request)
        logger.info(f"Response: {response.status_code}")
        logger.info(f'Response time: {time.time() - start}')
        return response
    except Exception as e:
        logger.info(f'RESPONSE ERROR: {e}')
        logger.info(f'Response time in exception: {time.time() - start}')
        send_tg(f'Возникла ошибка: {e}')
        return {'status': '500', 'error': 'send message to developer'}


@app.get('/')
def index():
    return RedirectResponse('/vacancies')


