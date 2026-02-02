FROM python:3.14.2-alpine

WORKDIR /app/Site/backend
ENV PYTHONPATH=/app

RUN apk add --no-cache build-base curl

COPY ./Site/backend/requirements.txt /app/Site/backend/requirements.txt
COPY ./Shared /app/Shared

RUN pip install --no-cache-dir --upgrade --root-user-action ignore -r /app/Site/backend/requirements.txt /app/Shared

COPY ./Site/backend /app/Site/backend

CMD ["fastapi", "run", "main.py", "--port", "80", "--proxy-headers"]
