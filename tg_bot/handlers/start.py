from aiogram import types, Router
from aiogram.filters import Command

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from bot_admin_panel.models import Client
from tg_bot.utils.subscription import check_subscription


router = Router()

def register_handlers(router: Router):
    @router.message(Command(commands=["start"]))
    async def start_handler(message: types.Message):
        is_subscribed = await check_subscription(message.from_user.id)
        if not is_subscribed:
            await message.answer(
                "Для использования бота вам необходимо подписаться на наши каналы."
            )
            return
        client, created = await Client.objects.aget_or_create(
            telegram_id=message.from_user.id,
            defaults={'name': message.from_user.full_name}
        )
        if created:
            await message.answer("Вы успешно зарегистрированы!")
        else:
            await message.answer(f"Добро пожаловать обратно, {client.name}!")

        markup = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Каталог", callback_data="catalog"),
             types.InlineKeyboardButton(text="Корзина", callback_data="cart")],
            [types.InlineKeyboardButton(text="FAQ", callback_data="faq")]
        ])
        await message.answer("Выберите раздел:", reply_markup=markup)
