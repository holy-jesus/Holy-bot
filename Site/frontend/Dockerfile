# ---------- Stage 1: build ----------
FROM node:25.2.1-alpine AS build

WORKDIR /app

# Устанавливаем зависимости
COPY Site/frontend/package.json Site/frontend/package-lock.json* Site/frontend/pnpm-lock.yaml* Site/frontend/yarn.lock* ./
RUN \
  if [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then npm install -g pnpm && pnpm install; \
  elif [ -f yarn.lock ]; then yarn install --frozen-lockfile; \
  else npm install; \
  fi

# Копируем исходники
COPY Site/frontend .

# Build-time environment variables for Vite
ARG VITE_BACKEND_PUBLIC_DOMAIN
ARG VITE_BACKEND_PATH
ARG VITE_APP_ENV

ENV VITE_BACKEND_PUBLIC_DOMAIN=$VITE_BACKEND_PUBLIC_DOMAIN
ENV VITE_BACKEND_PATH=$VITE_BACKEND_PATH
ENV VITE_APP_ENV=$VITE_APP_ENV

# Сборка Vite
RUN npm run build

# ---------- Stage 2: nginx ----------
FROM nginx:1.29.4-alpine

# Удаляем дефолтный конфиг
# RUN rm /etc/nginx/conf.d/default.conf

# Копируем свой конфиг
COPY configs/nginx.conf.template /etc/nginx/templates/default.conf.template

# Копируем билд Vite
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
