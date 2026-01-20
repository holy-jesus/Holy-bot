FROM python:3.14.2-alpine

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY alembic/* .

CMD ["alembic", "upgrade", "head"]
