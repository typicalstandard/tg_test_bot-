from aiogram.types import CallbackQuery

from aiogram import types, Router
from asgiref.sync import sync_to_async

from bot_admin_panel.models import Category, SubCategory, Product
from tg_bot.keyboards.catalog_keyboard import handle_page_switch
from tg_bot.utils.catalog_utils import  extract_pagination_data, send_product_with_pagination

router = Router()
def register_handlers(router: Router):
    router.callback_query.register(
        catalog_handler,
        lambda c: c.data == 'catalog'
    )

    router.callback_query.register(
        category_pagination_handler,
        lambda c: c.data.startswith('cat_page_')
    )

    router.callback_query.register(
        subcategory_pagination_handler,
        lambda c: c.data.startswith('subcat_page_')
    )


    router.callback_query.register(
        category_handler,
        lambda c: c.data.startswith('cat_') and not c.data.startswith('cat_page_')
    )
    router.callback_query.register(
        subcategory_handler,
        lambda c: c.data.startswith('subcat_') and not c.data.startswith('subcat_page_')
    )

    router.callback_query.register(
        product_pagination_handler,
        lambda c: c.data.startswith('prod_page_')
    )

    router.callback_query.register(
        quantity_handler,
        lambda c: c.data.startswith('quantity_')
    )


@router.callback_query(lambda c: c.data == 'catalog')
async def catalog_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    categories = await sync_to_async(list)(Category.objects.all())
    markup = await handle_page_switch(
        items=categories,
        current_page=0,
        callback_prefix="cat_",
    )
    await callback_query.message.answer("Выберите категорию:", reply_markup=markup)

@router.callback_query(lambda c: c.data.startswith('cat_'))
async def category_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    category_id = int(callback_query.data.split('_')[1])
    subcategories = await sync_to_async(list)(SubCategory.objects.filter(category_id=category_id))
    markup = await handle_page_switch(
        items=subcategories,
        current_page=0,
        callback_prefix="subcat_",
        extra_param=str(category_id)
    )
    await callback_query.message.answer("Выберите подкатегорию:", reply_markup=markup)

@router.callback_query(lambda c: c.data.startswith('cat_page_'))
async def category_pagination_handler(callback_query: types.CallbackQuery):

    await callback_query.answer()
    current_page = int(callback_query.data.split('_')[2])
    categories = await sync_to_async(list)(Category.objects.all())
    markup = await handle_page_switch(
        items=categories,
        current_page=current_page,
        callback_prefix="cat_"
    )
    await callback_query.message.edit_text("Выберите категорию:", reply_markup=markup)

@router.callback_query(lambda c: c.data.startswith('subcat_'))
async def subcategory_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    try:
        subcategory_id = int(callback_query.data.split('_')[2])
        products = await sync_to_async(list)(Product.objects.filter(subcategory_id=subcategory_id))
        if not products:
            await callback_query.message.answer("В данной подкатегории нет товаров.")
            return
        await send_product_with_pagination(callback_query.message, products, 0, subcategory_id)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка: {e}")

@router.callback_query(lambda c: c.data.startswith('subcat_page_'))
async def subcategory_pagination_handler(callback_query: CallbackQuery):
    await callback_query.answer()
    data_parts = callback_query.data.split('_')
    page_id = int(data_parts[2])
    category_id = int(data_parts[3])

    # Загружаем подкатегории
    subcategories = await sync_to_async(list)(SubCategory.objects.filter(category_id=category_id))
    markup = await handle_page_switch(
        items=subcategories,
        current_page=page_id,
        callback_prefix="subcat_",
        extra_param=category_id,
    )
    await callback_query.message.edit_text("Выберите подкатегорию:", reply_markup=markup)



@router.callback_query(lambda c: c.data.startswith('prod_page_'))
async def product_pagination_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Обновление товара...")
    try:
        current_index, subcategory_id, quantity = extract_pagination_data(callback_query.data)
        products = await sync_to_async(list)(Product.objects.filter(subcategory_id=subcategory_id))
        if not products or current_index < 0 or current_index >= len(products):
            await callback_query.message.answer("Неверный индекс товара.")
            return
        await send_product_with_pagination(callback_query.message, products, current_index, subcategory_id, quantity)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка: {e}")

@router.callback_query(lambda c: c.data.startswith('quantity_'))
async def quantity_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Обновление количества...")
    try:
        parts = callback_query.data.split('_')
        if len(parts) != 5:
            raise ValueError("Неверный формат callback_data для изменения количества.")
        action = parts[1]
        current_index = int(parts[2])
        subcategory_id = int(parts[3])
        quantity = int(parts[4])
        if action == "inc":
            quantity += 1
        elif action == "dec" and quantity > 1:
            quantity -= 1
        products = await sync_to_async(list)(Product.objects.filter(subcategory_id=subcategory_id))
        if not products:
            await callback_query.message.answer("В данной подкатегории нет товаров.")
            return
        await send_product_with_pagination(callback_query.message, products, current_index, subcategory_id, quantity)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка: {e}")
