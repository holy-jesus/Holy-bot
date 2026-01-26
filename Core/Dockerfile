FROM python:3.14.2-alpine

WORKDIR /app
ENV PYTHONPATH=/app

COPY ./Shared /app/Shared
RUN pip install --no-cache-dir --upgrade --root-user-action ignore ./Shared

COPY ./Core/requirements.txt /app/Core/requirements.txt
RUN pip install --no-cache-dir --upgrade --root-user-action ignore -r /app/Core/requirements.txt

COPY ./Core /app/Core

CMD ["python", "/app/Core"]
