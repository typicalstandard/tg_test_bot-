import asyncio
import os

from aiogram import Bot
from celery import shared_task
from .models import Broadcast, Client

from asgiref.sync import sync_to_async

async def send_message_to_clients(subject):
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    clients = await sync_to_async(list)(
        Client.objects.filter(is_active=True).values_list('telegram_id', flat=True)
    )
    for telegram_id in clients:
        try:
            await bot.send_message(chat_id=telegram_id, text=subject)
        except Exception as e:
            print(f"Ошибка при отправке сообщения клиенту {telegram_id}: {e}")
    await bot.session.close()


@shared_task
def send_broadcast_task(broadcast_id):
    broadcast = Broadcast.objects.get(id=broadcast_id)
    asyncio.run(send_message_to_clients(broadcast.subject))
    broadcast.sent = True
    broadcast.save()
