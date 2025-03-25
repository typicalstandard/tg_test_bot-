from asgiref.sync import sync_to_async
from bot_admin_panel.models import Product
from tg_bot.utils.catalog_utils import send_product_with_pagination
from bot_admin_panel.models import Cart, Client

async def return_to_products_list(callback_query, subcategory_id: int, current_index: int, quantity: int):
    try:
        products = await sync_to_async(list)(Product.objects.filter(subcategory_id=subcategory_id))
        if not products:
            await callback_query.message.answer("В данной подкатегории нет товаров.")
            return
        await send_product_with_pagination(callback_query.message, products, current_index, subcategory_id, quantity)
    except Exception as e:
        await callback_query.message.answer(f"Ошибка: {e}")


async def get_cart_items(client):
    client = await Client.objects.aget(telegram_id=client.telegram_id)
    return await sync_to_async(list)(Cart.objects.filter(client=client).select_related("product"))

async def calculate_cart_total(cart_items):
    total = sum(item.product.price * item.quantity for item in cart_items)
    return total


async def delete_item_from_cart(item_id):
    try:
        await Cart.filter(id=item_id).delete()
        return True
    except Exception as e:
        print(f"Ошибка удаления товара: {e}")
        return False
