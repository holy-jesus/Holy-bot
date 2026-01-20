FROM python:3.14.2-alpine

WORKDIR /app
ENV PYTHONPATH=/app

RUN pip install --no-cache-dir --upgrade --root-user-action ignore SQLAlchemy~=2.0.45 alembic~=1.18.1 psycopg[binary,pool]~=3.3.2

COPY ./configs/alembic.ini /app/configs/alembic.ini
COPY ./Shared/alembic /app/Shared/alembic
COPY ./Shared/holybot_shared /app/Shared/holybot_shared

CMD ["alembic", "-c", "/app/configs/alembic.ini", "upgrade", "head"]
