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

# Сборка Vite
RUN npm run build

# ---------- Stage 2: nginx ----------
FROM nginx:1.29.4-alpine

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Копируем свой конфиг
COPY configs/nginx.conf /etc/nginx/conf.d/default.conf

# Копируем билд Vite
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
