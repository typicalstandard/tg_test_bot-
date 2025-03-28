from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def build_confirmation_keyboard(product_id: int, subcategory_id: int, current_index: int, quantity: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data=f"confirm_yes_{product_id}_{subcategory_id}_{current_index}_{quantity}"
            ),
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data=f"confirm_no_{product_id}_{subcategory_id}_{current_index}_{quantity}"
            )
        ]
    ])
    return keyboard

def generate_cart_buttons(cart_items, current_page, items_per_page):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    start_index = current_page * items_per_page
    end_index = min(start_index + items_per_page, len(cart_items))
    if start_index >= len(cart_items):
        start_index = max(0, len(cart_items) - items_per_page)
        end_index = len(cart_items)


    for item in cart_items[start_index:end_index]:
        button_text = f"Удалить {item.product.name}"
        callback_data = f"delete_{item.id}"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text=button_text, callback_data=callback_data)
        ])

    if start_index > 0:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="⬅️ Предыдущая страница", callback_data=f"cart_{current_page - 1}")
        ])
    if end_index < len(cart_items):
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="➡️ Следующая страница", callback_data=f"cart_{current_page + 1}")
        ])

    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="Доставка", callback_data="start_user_info_input"),
    ])

    return keyboard
