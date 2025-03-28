import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')

import django
django.setup()

import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from bot_config import BOT_TOKEN, REDIS_URL
from handlers import start, catalog, cart, faq, delivery

redis = Redis.from_url(REDIS_URL)
storage = RedisStorage(redis)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    router = Router()


    start.register_handlers(router)
    catalog.register_handlers(router)
    cart.register_handlers(router)
    faq.register_handlers(router)
    delivery.register_handlers(router)

    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

