FROM python:3.13-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Открываем порт для Django
EXPOSE 8000

# Команда для запуска сервера с Gunicorn и 4 потоками
CMD ["sh", "-c", "./wait-for-it.sh db:5432 -- python manage.py migrate --noinput && uvicorn wallet_project.asgi:application --host 0.0.0.0 --port 8000"]