from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
async def handle_page_switch(items, current_page: int, callback_prefix: str, extra_param: str = None):
    ITEMS_PER_PAGE = 3
    start_idx = current_page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = items[start_idx:end_idx]

    keyboard = [
        [InlineKeyboardButton(text=item.name,
                              callback_data=f"{callback_prefix}{extra_param}_{item.id}" if extra_param else f"{callback_prefix}{item.id}")]
        for item in page_items
    ]

    navigation_buttons = []
    if current_page > 0:
        prev_data = f"{callback_prefix}page_{current_page - 1}_{extra_param}" if extra_param else f"{callback_prefix}page_{current_page - 1}"
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущая", callback_data=prev_data))
    if end_idx < len(items):
        next_data = f"{callback_prefix}page_{current_page + 1}_{extra_param}" if extra_param else f"{callback_prefix}page_{current_page + 1}"
        navigation_buttons.append(InlineKeyboardButton(text="Следующая ➡️", callback_data=next_data))

    if navigation_buttons:
        keyboard.append(navigation_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)




def build_product_keyboard(current_index: int, subcategory_id: int, quantity: int, products_count: int,
                           product_id: int) -> InlineKeyboardMarkup:
    """
    Формирует клавиатуру с кнопками изменения количества, пагинации и добавления в корзину.
    """
    kb = InlineKeyboardMarkup(inline_keyboard=[])

    # Кнопки изменения количества
    kb.inline_keyboard.append([
        InlineKeyboardButton(text="➖", callback_data=f"quantity_dec_{current_index}_{subcategory_id}_{quantity}"),
        InlineKeyboardButton(text="➕", callback_data=f"quantity_inc_{current_index}_{subcategory_id}_{quantity}")
    ])

    # Кнопки пагинации
    if current_index > 0:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="⬅️ Назад",
                                 callback_data=f"prod_page_{current_index - 1}_{subcategory_id}_{quantity}")
        ])
    if current_index < products_count - 1:
        kb.inline_keyboard.append([
            InlineKeyboardButton(text="Вперед ➡️",
                                 callback_data=f"prod_page_{current_index + 1}_{subcategory_id}_{quantity}")
        ])

    kb.inline_keyboard.append([
        InlineKeyboardButton(text="Добавить в корзину", callback_data=f"confirm_{product_id}_{subcategory_id}_{current_index}_{quantity}")
    ])

    return kb
