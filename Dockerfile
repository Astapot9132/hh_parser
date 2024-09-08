FROM python:3.10

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/


CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class",\
     "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:2027",\
     "--timeout", "200"]
