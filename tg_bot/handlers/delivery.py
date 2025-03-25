from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router
from asgiref.sync import sync_to_async

from bot_admin_panel.models import Client
from tg_bot.states.delivery_states import UserInfo
from tg_bot.utils.payments import start_payment_step
from tg_bot.utils.validators_delivery import validate_address, validate_phone, validate_email

router = Router()

EXIT_KEYWORD = "выйти"

def register_handlers(router: Router):
    router.callback_query.register(
        start_user_info_input,
        lambda callback_query: callback_query.data == "start_user_info_input"
    )
    router.message.register(process_address, UserInfo.waiting_for_address)
    router.message.register(process_phone, UserInfo.waiting_for_phone)
    router.message.register(process_email, UserInfo.waiting_for_email)

async def start_user_info_input(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await callback_query.message.reply("Введите ваш адрес (или отправьте 'выйти' для отмены):")
    await state.set_state(UserInfo.waiting_for_address)

async def process_address(message: Message, state: FSMContext):
    user_address = message.text
    if user_address.lower() == EXIT_KEYWORD:  # Проверка на выход
        await cancel_process(message, state)
        return

    if not validate_address(user_address):
        await message.reply("Адрес слишком короткий. Попробуйте снова (или отправьте 'выйти' для отмены):")
        return

    await state.update_data(address=user_address)
    await message.reply("Введите ваш номер телефона (например, +375291234567, или 'выйти' для отмены):")
    await state.set_state(UserInfo.waiting_for_phone)

async def process_phone(message: Message, state: FSMContext):
    user_phone = message.text
    if user_phone.lower() == EXIT_KEYWORD:
        await cancel_process(message, state)
        return

    if not validate_phone(user_phone):
        await message.reply("Неверный формат номера телефона. Попробуйте снова (или отправьте 'выйти' для отмены):")
        return

    await state.update_data(phone=user_phone)
    await message.reply("Введите ваш email (или 'выйти' для отмены):")
    await state.set_state(UserInfo.waiting_for_email)


async def process_email(message: Message, state: FSMContext):
    user_email = message.text
    if user_email.lower() == EXIT_KEYWORD:
        await cancel_process(message, state)
        return

    if not validate_email(user_email):
        await message.reply("Неверный формат email. Попробуйте снова (или отправьте 'выйти' для отмены):")
        return

    # Получение данных из FSM
    user_data = await state.get_data()
    address = user_data.get("address")
    phone = user_data.get("phone")
    telegram_id = message.from_user.id

    async def save_client():
        client, created = await sync_to_async(Client.objects.update_or_create)(
            telegram_id=telegram_id,
            defaults={
                "address": address,
                "phone": phone,
                "email": user_email,
                "is_active": True,
            }
        )
        return client, created

    client, created = await save_client()

    if created:
        await message.reply("Ваши данные успешно сохранены в системе!")
    else:
        await message.reply("Ваши данные обновлены!")

    await start_payment_step(message, client, state)


async def cancel_process(message: Message, state: FSMContext):
    await message.reply("Вы вышли из процесса ввода данных.")
    await state.clear()
