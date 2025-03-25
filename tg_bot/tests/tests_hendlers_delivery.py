import unittest
from unittest.mock import AsyncMock, patch
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from tg_bot.handlers.delivery import (
    start_user_info_input,
    process_address,
    process_phone,
    process_email,
    cancel_process,
)
from tg_bot.states.delivery_states import UserInfo
from tg_bot.utils.payments import start_payment_step
from tg_bot.utils.validators_delivery import validate_address, validate_phone, validate_email
from bot_admin_panel.models import Client


def create_dummy_state(data=None):
    state = AsyncMock(spec=FSMContext)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value=data or {})
    state.clear = AsyncMock()
    return state


def create_callback_query_delivery(data: str, text: str = "", caption=None, user_id=12345) -> CallbackQuery:
    cq = AsyncMock(spec=CallbackQuery)
    cq.data = data
    cq.answer = AsyncMock()
    dummy_message = AsyncMock(spec=Message)
    dummy_message.text = text
    dummy_message.reply = AsyncMock()
    dummy_message.edit_text = AsyncMock()
    dummy_message.edit_caption = AsyncMock()
    dummy_message.caption = caption
    cq.message = dummy_message
    cq.from_user.id = user_id
    return cq


def fake_sync_to_async(fn):
    async def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


class TestDeliveryHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_start_user_info_input(self):
        cq = create_callback_query_delivery("start_user_info_input")
        state = create_dummy_state()
        await start_user_info_input(cq, state)
        cq.answer.assert_awaited_once()
        cq.message.reply.assert_awaited_once_with("Введите ваш адрес (или отправьте 'выйти' для отмены):")
        state.set_state.assert_awaited_once_with(UserInfo.waiting_for_address)

    async def test_process_address_exit(self):
        msg = create_callback_query_delivery("", text="выйти").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.cancel_process", new=AsyncMock()) as mock_cancel:
            await process_address(msg, state)
            mock_cancel.assert_awaited_once_with(msg, state)

    async def test_process_address_invalid(self):
        msg = create_callback_query_delivery("", text="short").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.validate_address", return_value=False):
            await process_address(msg, state)
            msg.reply.assert_awaited_once_with(
                "Адрес слишком короткий. Попробуйте снова (или отправьте 'выйти' для отмены):")
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()

    async def test_process_address_valid(self):
        msg = create_callback_query_delivery("", text="Valid Address").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.validate_address", return_value=True):
            await process_address(msg, state)
            state.update_data.assert_awaited_once_with(address="Valid Address")
            msg.reply.assert_awaited_once_with(
                "Введите ваш номер телефона (например, +375291234567, или 'выйти' для отмены):")
            state.set_state.assert_awaited_once_with(UserInfo.waiting_for_phone)

    async def test_process_phone_exit(self):
        msg = create_callback_query_delivery("", text="выйти").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.cancel_process", new=AsyncMock()) as mock_cancel:
            await process_phone(msg, state)
            mock_cancel.assert_awaited_once_with(msg, state)

    async def test_process_phone_invalid(self):
        msg = create_callback_query_delivery("", text="invalid_phone").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.validate_phone", return_value=False):
            await process_phone(msg, state)
            msg.reply.assert_awaited_once_with(
                "Неверный формат номера телефона. Попробуйте снова (или отправьте 'выйти' для отмены):")
            state.update_data.assert_not_awaited()
            state.set_state.assert_not_awaited()

    async def test_process_phone_valid(self):
        msg = create_callback_query_delivery("", text="+375291234567").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.validate_phone", return_value=True):
            await process_phone(msg, state)
            state.update_data.assert_awaited_once_with(phone="+375291234567")
            msg.reply.assert_awaited_once_with("Введите ваш email (или 'выйти' для отмены):")
            state.set_state.assert_awaited_once_with(UserInfo.waiting_for_email)

    async def test_process_email_exit(self):
        msg = create_callback_query_delivery("", text="выйти").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.cancel_process", new=AsyncMock()) as mock_cancel:
            await process_email(msg, state)
            mock_cancel.assert_awaited_once_with(msg, state)

    async def test_process_email_invalid(self):
        msg = create_callback_query_delivery("", text="invalid_email").message
        state = create_dummy_state()
        with patch("tg_bot.handlers.delivery.validate_email", return_value=False):
            await process_email(msg, state)
            msg.reply.assert_awaited_once_with(
                "Неверный формат email. Попробуйте снова (или отправьте 'выйти' для отмены):")

    async def test_process_email_valid_created(self):
        dummy_client = Client(telegram_id=12345)
        msg = create_callback_query_delivery("", text="user@example.com").message
        state = create_dummy_state(data={"address": "Some Address", "phone": "12345"})
        with patch("tg_bot.handlers.delivery.validate_email", return_value=True):
            with patch("tg_bot.handlers.delivery.sync_to_async", side_effect=fake_sync_to_async):
                with patch("bot_admin_panel.models.Client.objects.update_or_create",
                           new=AsyncMock(return_value=(dummy_client, True))):
                    with patch("tg_bot.handlers.delivery.start_payment_step", new=AsyncMock()) as mock_payment:
                        await process_email(msg, state)
                        msg.reply.assert_any_await("Ваши данные успешно сохранены в системе!")
                        mock_payment.assert_awaited_once_with(msg, dummy_client, state)

    async def test_process_email_valid_updated(self):
        dummy_client = Client(telegram_id=12345)
        msg = create_callback_query_delivery("", text="user@example.com").message
        state = create_dummy_state(data={"address": "Some Address", "phone": "12345"})
        with patch("tg_bot.handlers.delivery.validate_email", return_value=True):
            with patch("tg_bot.handlers.delivery.sync_to_async", side_effect=fake_sync_to_async):
                with patch("bot_admin_panel.models.Client.objects.update_or_create",
                           new=AsyncMock(return_value=(dummy_client, False))):
                    with patch("tg_bot.handlers.delivery.start_payment_step", new=AsyncMock()) as mock_payment:
                        await process_email(msg, state)
                        msg.reply.assert_any_await("Ваши данные обновлены!")
                        mock_payment.assert_awaited_once_with(msg, dummy_client, state)

    async def test_cancel_process(self):
        msg = create_callback_query_delivery("").message
        state = create_dummy_state()
        await cancel_process(msg, state)
        msg.reply.assert_awaited_once_with("Вы вышли из процесса ввода данных.")
        state.clear.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
