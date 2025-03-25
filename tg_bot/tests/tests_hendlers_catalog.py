import unittest
from unittest.mock import AsyncMock, patch
from aiogram.types import CallbackQuery, Message

from tg_bot.handlers.catalog import catalog_handler, category_handler, category_pagination_handler, subcategory_handler, subcategory_pagination_handler, product_pagination_handler, quantity_handler


def create_callback_query(data: str) -> CallbackQuery:
    cq = AsyncMock(spec=CallbackQuery)
    cq.data = data
    cq.answer = AsyncMock()
    dummy_message = AsyncMock(spec=Message)
    dummy_message.answer = AsyncMock()
    dummy_message.edit_text = AsyncMock()
    cq.message = dummy_message
    return cq


def fake_sync_to_async(fn):
    async def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper


class TestTelegramBotHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_catalog_handler(self):
        dummy_categories = ['cat1', 'cat2']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('tg_bot.utils.catalog_utils.handle_page_switch', new=AsyncMock(return_value='dummy_markup')):
                with patch('bot_admin_panel.models.Category') as mock_Category:
                    mock_Category.objects.all.return_value = dummy_categories
                    cbq = create_callback_query("catalog")
                    await catalog_handler(cbq)
                    cbq.answer.assert_awaited_once()
                    cbq.message.answer.assert_awaited_once_with("Выберите категорию:", reply_markup='dummy_markup')

    async def test_category_handler(self):
        dummy_subcategories = ['subcat1', 'subcat2']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('tg_bot.utils.catalog_utils.handle_page_switch', new=AsyncMock(return_value='dummy_markup_subcat')):
                with patch('bot_admin_panel.models.SubCategory') as mock_SubCategory:
                    mock_SubCategory.objects.filter.return_value = dummy_subcategories
                    cbq = create_callback_query("cat_1")
                    await category_handler(cbq)
                    cbq.answer.assert_awaited_once()
                    cbq.message.answer.assert_awaited_once_with("Выберите подкатегорию:", reply_markup='dummy_markup_subcat')

    async def test_category_pagination_handler(self):
        dummy_categories = ['cat1', 'cat2', 'cat3']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('tg_bot.utils.catalog_utils.handle_page_switch', new=AsyncMock(return_value='dummy_markup_pag')):
                with patch('bot_admin_panel.models.Category') as mock_Category:
                    mock_Category.objects.all.return_value = dummy_categories
                    cbq = create_callback_query("cat_page_2")
                    await category_pagination_handler(cbq)
                    cbq.answer.assert_awaited_once()
                    cbq.message.edit_text.assert_awaited_once_with("Выберите категорию:", reply_markup='dummy_markup_pag')

    async def test_subcategory_handler_no_products(self):
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('bot_admin_panel.models.Product') as mock_Product:
                mock_Product.objects.filter.return_value = []
                cbq = create_callback_query("subcat_1_1")
                await subcategory_handler(cbq)
                cbq.answer.assert_awaited_once()
                cbq.message.answer.assert_awaited_once_with("В данной подкатегории нет товаров.")

    async def test_subcategory_handler_with_products(self):
        dummy_products = ['prod1', 'prod2']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('bot_admin_panel.models.Product') as mock_Product:
                mock_Product.objects.filter.return_value = dummy_products
                with patch('tg_bot.utils.cart_utils.send_product_with_pagination', new=AsyncMock()) as mock_send_product:
                    cbq = create_callback_query("subcat_1_1")
                    await subcategory_handler(cbq)
                    cbq.answer.assert_awaited_once()
                    mock_send_product.assert_awaited_once_with(cbq.message, dummy_products, 0, 1)

    async def test_subcategory_pagination_handler(self):
        dummy_subcategories = ['subcat1', 'subcat2']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('tg_bot.utils.catalog_utils.handle_page_switch', new=AsyncMock(return_value='dummy_markup_subpag')):
                with patch('bot_admin_panel.models.SubCategory') as mock_SubCategory:
                    mock_SubCategory.objects.filter.return_value = dummy_subcategories
                    cbq = create_callback_query("subcat_page_2_1")
                    await subcategory_pagination_handler(cbq)
                    cbq.answer.assert_awaited_once()
                    cbq.message.edit_text.assert_awaited_once_with("Выберите подкатегорию:", reply_markup='dummy_markup_subpag')

    async def test_product_pagination_handler(self):
        dummy_products = ['prod1', 'prod2', 'prod3']
        with patch('tg_bot.utils.catalog_utils.extract_pagination_data', return_value=(1, 2, 1)):
            with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
                with patch('bot_admin_panel.models.Product') as mock_Product:
                    mock_Product.objects.filter.return_value = dummy_products
                    with patch('tg_bot.utils.cart_utils.send_product_with_pagination', new=AsyncMock()) as mock_send_product:
                        cbq = create_callback_query("prod_page_dummy")
                        await product_pagination_handler(cbq)
                        cbq.answer.assert_awaited_once_with("Обновление товара...")
                        mock_send_product.assert_awaited_once_with(cbq.message, dummy_products, 1, 2, 1)

    async def test_quantity_handler_increment(self):
        dummy_products = ['prod1', 'prod2']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('bot_admin_panel.models.Product') as mock_Product:
                mock_Product.objects.filter.return_value = dummy_products
                with patch('tg_bot.utils.cart_utils.send_product_with_pagination', new=AsyncMock()) as mock_send_product:
                    cbq = create_callback_query("quantity_inc_0_1_2")
                    await quantity_handler(cbq)
                    cbq.answer.assert_awaited_once_with("Обновление количества...")
                    mock_send_product.assert_awaited_once_with(cbq.message, dummy_products, 0, 1, 3)

    async def test_quantity_handler_decrement(self):
        dummy_products = ['prod1']
        with patch('tg_bot.handlers.catalog.sync_to_async', side_effect=fake_sync_to_async):
            with patch('bot_admin_panel.models.Product') as mock_Product:
                mock_Product.objects.filter.return_value = dummy_products
                with patch('tg_bot.utils.cart_utils.send_product_with_pagination', new=AsyncMock()) as mock_send_product:
                    cbq = create_callback_query("quantity_dec_0_1_3")
                    await quantity_handler(cbq)
                    cbq.answer.assert_awaited_once_with("Обновление количества...")
                    mock_send_product.assert_awaited_once_with(cbq.message, dummy_products, 0, 1, 2)

    async def test_quantity_handler_invalid_format(self):
        cbq = create_callback_query("quantity_invalid_format")
        await quantity_handler(cbq)
        cbq.message.answer.assert_awaited_once()
        args, _ = cbq.message.answer.call_args
        self.assertIn("Неверный формат callback_data", args[0])


if __name__ == "__main__":
    unittest.main()
