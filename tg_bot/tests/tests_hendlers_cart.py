import unittest
from unittest.mock import AsyncMock, patch
from aiogram.types import CallbackQuery, Message

from bot_admin_panel.models import Client, Product, Cart
from tg_bot.handlers.cart import (
    confirm_add_to_cart_handler,
    confirm_yes_handler,
    confirm_no_handler,
    cart_button_handler,
    cart_pagination_handler,
    delete_item_handler,
)




def create_callback_query(data: str, caption=None, user_id=12345) -> CallbackQuery:
    cq = AsyncMock(spec=CallbackQuery)
    cq.data = data
    cq.answer = AsyncMock()
    dummy_message = AsyncMock(spec=Message)
    dummy_message.answer = AsyncMock()
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


class TestTelegramBotHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_confirm_add_to_cart_handler_with_caption(self):
        with patch('tg_bot.utils.catalog_utils.build_confirmation_keyboard', new=AsyncMock(return_value='dummy_markup')):
            cbq = create_callback_query(data="confirm_1_2_3_4", caption="Test Caption")
            await confirm_add_to_cart_handler(cbq)
            cbq.answer.assert_awaited_once()
            cbq.message.edit_caption.assert_awaited_once_with(reply_markup='dummy_markup')

    async def test_confirm_add_to_cart_handler_without_caption(self):
        cbq = create_callback_query(data="confirm_1_2_3_4", caption=None)
        await confirm_add_to_cart_handler(cbq)
        cbq.answer.assert_awaited_once_with("Ошибка: сообщение нельзя редактировать.")

    async def test_confirm_yes_handler(self):
        dummy_product = Product(id=1, name="Test Product", price=100)
        dummy_client = Client(telegram_id=12345)
        with patch('bot_admin_panel.models.Client.objects.aget', new=AsyncMock(return_value=dummy_client)):
            with patch('bot_admin_panel.models.Product.objects.aget', new=AsyncMock(return_value=dummy_product)):
                with patch('bot_admin_panel.models.Cart.objects.aget_or_create', new=AsyncMock()) as mock_cart_create:
                    with patch('tg_bot.utils.cart_utils.return_to_products_list', new=AsyncMock()) as mock_return:
                        cbq = create_callback_query(data="confirm_yes_1_2_3_4_5")
                        await confirm_yes_handler(cbq)
                        cbq.answer.assert_awaited_once_with("Добавление товара в корзину...")
                        mock_cart_create.assert_awaited_once_with(client=dummy_client, product=dummy_product, quantity=5)
                        mock_return.assert_awaited_once_with(cbq, 2, 3, 5)

    async def test_confirm_no_handler(self):
        with patch('tg_bot.utils.cart_utils.return_to_products_list', new=AsyncMock()) as mock_return:
            cbq = create_callback_query(data="confirm_no_1_2_3_4_5")
            await confirm_no_handler(cbq)
            cbq.answer.assert_awaited_once_with("Действие отменено.")
            mock_return.assert_awaited_once_with(cbq, 3, 4, 5)

    async def test_cart_button_handler_empty_cart(self):
        with patch('bot_admin_panel.models.Client.objects.get', new=AsyncMock()):
            with patch('bot_admin_panel.models.Cart.objects.filter', new=AsyncMock(return_value=[])):
                cbq = create_callback_query(data="cart")
                await cart_button_handler(cbq)
                cbq.answer.assert_awaited_once_with("Обновление корзины...")
                cbq.message.edit_text.assert_awaited_once_with("🛒 Ваша корзина пуста.")

    async def test_cart_button_handler_with_items(self):
        dummy_client = Client(telegram_id=12345)
        dummy_cart_items = [
            Cart(product=Product(name="Test Product 1", price=100), quantity=2),
            Cart(product=Product(name="Test Product 2", price=200), quantity=1),
        ]
        with patch('bot_admin_panel.models.Client.objects.get', new=AsyncMock(return_value=dummy_client)):
            with patch('bot_admin_panel.models.Cart.objects.filter', new=AsyncMock(return_value=dummy_cart_items)):
                with patch('tg_bot.utils.cart_utils.generate_cart_buttons', new=AsyncMock(return_value='dummy_keyboard')):
                    cbq = create_callback_query(data="cart")
                    await cart_button_handler(cbq)
                    cbq.answer.assert_awaited_once_with("Обновление корзины...")
                    cbq.message.edit_text.assert_awaited_once()

    async def test_cart_pagination_handler(self):
        with patch('tg_bot.handlers.cart.cart_button_handler', new=AsyncMock()) as mock_cart:
            cbq = create_callback_query(data="cart_1")
            await cart_pagination_handler(cbq)
            mock_cart.assert_awaited_once_with(cbq)

    async def test_delete_item_handler_success(self):
        dummy_client = Client(telegram_id=12345)
        with patch('bot_admin_panel.models.Cart.objects.filter', new=AsyncMock()) as mock_filter:
            with patch('bot_admin_panel.models.Cart.objects.filter(id=1).delete', new=AsyncMock()) as mock_delete:
                with patch('bot_admin_panel.models.Client.objects.get', new=AsyncMock(return_value=dummy_client)):
                    with patch('tg_bot.handlers.cart.cart_button_handler', new=AsyncMock()) as mock_cart:
                        cbq = create_callback_query(data="delete_1")
                        await delete_item_handler(cbq)
                        cbq.answer.assert_awaited_once_with("Удаление товара...")
                        mock_delete.assert_awaited_once()
                        mock_cart.assert_awaited_once_with(cbq)

    async def test_delete_item_handler_no_items_left(self):
        dummy_client = Client(telegram_id=12345)
        with patch('bot_admin_panel.models.Cart.objects.filter', new=AsyncMock(return_value=[])):
            with patch('bot_admin_panel.models.Client.objects.get', new=AsyncMock(return_value=dummy_client)):
                cbq = create_callback_query(data="delete_1")
                await delete_item_handler(cbq)
                cbq.answer.assert_awaited_once_with("Удаление товара...")
                cbq.message.edit_text.assert_awaited_once_with("🛒 Ваша корзина пуста.")

    async def test_delete_item_handler_invalid_id(self):
        cbq = create_callback_query(data="delete_invalid")
        await delete_item_handler(cbq)
        cbq.answer.assert_awaited_once_with("Ошибка: неверный идентификатор товара.", show_alert=True)


if __name__ == "__main__":
    unittest.main()
