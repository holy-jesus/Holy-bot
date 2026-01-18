FROM python:3.14.2-trixie

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .

CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
