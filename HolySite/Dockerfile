# Step 1: Build the frontend
FROM node:20-slim AS frontend-build

WORKDIR /frontend

COPY ./frontend .

RUN npm ci

RUN npm run build

# Step 2: Backend setup
FROM python:3.12.6

WORKDIR /app

COPY --from=frontend-build /frontend/dist /app/static

ENV frontend=/app/static

COPY ./backend .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "run"]
