FROM python:3.14.2-alpine

WORKDIR /app
ENV PYTHONPATH=/app

RUN apk add --no-cache gcc musl-dev

COPY ./Shared /app/Shared
RUN pip install --no-cache-dir --upgrade --root-user-action ignore ./Shared

COPY ./API/requirements.txt /app/API/requirements.txt
RUN pip install --no-cache-dir --upgrade --root-user-action ignore -r /app/API/requirements.txt

COPY ./API /app/API

CMD ["python", "/app/API"]
