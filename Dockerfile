# Используем оптимизированный базовый образ Python
FROM python:3.10-slim

# Определяем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в контейнер
COPY requirements.txt /app/

# Обновляем pip и устанавливаем зависимости
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копируем исходный код приложения в контейнер
COPY . /app

# Создаем каталог для логов (для последующего монтирования volume)
RUN mkdir -p /app/logs

# Команда заведения Django-сервера.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
