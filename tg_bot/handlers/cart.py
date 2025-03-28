from aiogram import types, Router
from asgiref.sync import sync_to_async

from bot_admin_panel.models import Cart, Client, Product
from tg_bot.keyboards.cart_keyboard import build_confirmation_keyboard, generate_cart_buttons
from tg_bot.utils.cart_utils import return_to_products_list

router = Router()

def register_handlers(router: Router):
    router.callback_query.register(
        confirm_yes_handler,
        lambda c: c.data.startswith('confirm_yes_')
    )

    router.callback_query.register(
        confirm_no_handler,
        lambda c: c.data.startswith('confirm_no_')
    )


    router.callback_query.register(
        confirm_add_to_cart_handler,
        lambda c: c.data.startswith('confirm_')
    )

    router.callback_query.register(
        cart_button_handler,
        lambda c: c.data == "cart"
    )

    router.callback_query.register(
        cart_pagination_handler,
        lambda c: c.data.startswith('cart_')
    )

    router.callback_query.register(
        delete_item_handler,
        lambda c: c.data.startswith('delete_')
    )


@router.callback_query(lambda c: c.data.startswith('confirm_'))
async def confirm_add_to_cart_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()

    data_parts = callback_query.data.split('_')
    product_id = int(data_parts[1])
    subcategory_id = int(data_parts[2])
    current_index = int(data_parts[3])
    quantity = int(data_parts[4])

    confirmation_keyboard = build_confirmation_keyboard(product_id, subcategory_id, current_index, quantity)

    if callback_query.message.caption:
        await callback_query.message.edit_caption(reply_markup=confirmation_keyboard)
    else:
        await callback_query.answer("Ошибка: сообщение нельзя редактировать.")


@router.callback_query(lambda c: c.data.startswith('confirm_yes_'))
async def confirm_yes_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Добавление товара в корзину...")

    data_parts = callback_query.data.split('_')
    product_id = int(data_parts[2])
    subcategory_id = int(data_parts[3])
    current_index = int(data_parts[4])
    quantity = int(data_parts[5])

    client_instance = await Client.objects.aget(telegram_id=callback_query.from_user.id)
    product_instance = await Product.objects.aget(id=product_id)

    await Cart.objects.aget_or_create(
        client=client_instance,
        product=product_instance,
        quantity=quantity,
    )

    await return_to_products_list(callback_query, subcategory_id, current_index, quantity)



@router.callback_query(lambda c: c.data.startswith('confirm_no_'))
async def confirm_no_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Действие отменено.")

    data_parts = callback_query.data.split('_')
    subcategory_id = int(data_parts[3])
    current_index = int(data_parts[4])
    quantity = int(data_parts[5])

    await return_to_products_list(callback_query, subcategory_id, current_index, quantity)



@router.callback_query(lambda c: c.data == "cart")
async def cart_button_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Обновление корзины...")

    try:
        client = await sync_to_async(Client.objects.get)(telegram_id=callback_query.from_user.id)

        cart_items = await sync_to_async(list)(
            Cart.objects.filter(client=client).select_related("product")
        )

        if not cart_items:
            await callback_query.message.edit_text("Ваша корзина пуста.")
            return

        total = sum(item.quantity * item.product.price for item in cart_items)

        text_lines = [" Ваша корзина:"]
        for item in cart_items:
            text_lines.append(f"{item.product.name} — {item.quantity} шт. = {item.quantity * item.product.price} руб.")
        text_lines.append(f"\n Общая сумма: {total} руб.")

        items_per_page = 2
        current_page = int(callback_query.data.split("_")[1]) if "_" in callback_query.data else 0
        keyboard = generate_cart_buttons(cart_items, current_page, items_per_page)

        await callback_query.message.edit_text("\n".join(text_lines), reply_markup=keyboard)
    except Client.DoesNotExist:
        await callback_query.answer("Клиент не найден.", show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при обновлении корзины.", show_alert=True)


@router.callback_query(lambda c: c.data.startswith("cart_"))
async def cart_pagination_handler(callback_query: types.CallbackQuery):
    await cart_button_handler(callback_query)


@router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_item_handler(callback_query: types.CallbackQuery):
    await callback_query.answer("Удаление товара...")

    try:
        item_id = int(callback_query.data.split("_")[1])
        await sync_to_async(Cart.objects.filter(id=item_id).delete)()
        client = await sync_to_async(Client.objects.get)(telegram_id=callback_query.from_user.id)

        cart_items = await sync_to_async(list)(
            Cart.objects.filter(client=client).select_related("product")
        )

        if cart_items:
            await cart_button_handler(callback_query)
        else:
            await callback_query.message.edit_text("🛒 Ваша корзина пуста.")
    except ValueError:
        await callback_query.answer("Ошибка: неверный идентификатор товара.", show_alert=True)
    except Client.DoesNotExist:
        await callback_query.answer("Клиент не найден.", show_alert=True)
    except Exception as e:
        await callback_query.answer("Ошибка при удалении товара.", show_alert=True)


