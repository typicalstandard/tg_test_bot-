## Telegram-бот для управления корзиной с админ панелью

### Шаги для запуска
1. Убедитесь, что установлен **Docker** и **Docker Compose**.
2. Клонируйте репозиторий:
```

 git clone https://github.com/typicalstandard/tg_test_bot-.git
 cd tg_test_bot

```
3. Создайте файл .env
```
  
# Telegram Bot Token
BOT_TOKEN = your_bot_token_here

# Database 
DB_NAME = your_database_name
DB_USER = your_database_user
DB_PASSWORD = your_database_password
DB_HOST = your_database_host
DB_PORT = your_database_port

# YooKassa 
YOOKASSA_SHOP_ID = your_yookassa_shop_id
YOOKASSA_SECRET_KEY = your_yookassa_secret_key

# Celery 
CELERY_BROKER_URL = redis://your_redis_url
CELERY_RESULT_BACKEND = redis://your_redis_url

# Redis 
REDIS_URL = redis://your_redis_url

```
4. Запустить билд образа
```

docker-compose up --build

```

** В админку можно зайти через этот url http://localhost:8000/admin **
