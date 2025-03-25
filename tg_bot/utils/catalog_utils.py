import os
from aiogram.types import InputMediaPhoto, FSInputFile

from admin_panel import settings
from tg_bot.keyboards.catalog_keyboard import build_product_keyboard


def get_photo_path(product) -> str:
    return os.path.join(settings.MEDIA_ROOT, product.photo.name) if product.photo else None

async def update_product_message(message, product, keyboard, text: str):
    photo_path = get_photo_path(product)
    if photo_path and os.path.exists(photo_path):
        photo = FSInputFile(photo_path)
        try:
            if message.caption != text:
                await message.edit_media(
                    media=InputMediaPhoto(media=photo, caption=text),
                    reply_markup=keyboard
                )
        except Exception:
            await message.edit_text(text=f"{text}\n(Ошибка загрузки фото)", reply_markup=keyboard)
        else:
            try:
                if message.text != text:
                    await message.edit_text(text=text, reply_markup=keyboard)
            except Exception:
                pass
    else:
        await message.edit_text(text=text, reply_markup=keyboard)


async def send_product_with_pagination(message, products, current_index, subcategory_id, quantity=1):
    product = products[current_index]
    text = format_product_text(product, quantity)
    keyboard = build_product_keyboard(current_index, subcategory_id, quantity, len(products), product.id)
    await update_product_message(message, product, keyboard, text)


def format_product_text(product, quantity: int) -> str:
    total_price = product.price * quantity
    return (
        f"**{product.name}**\n\n{product.description}\n"
        f"Цена за единицу: {product.price} руб.\n"
        f"Количество: {quantity}\n"
        f"Общая цена: {total_price} руб."
    )



def extract_pagination_data(callback_data: str) -> (int, int, int):
    parts = callback_data.split('_')
    if len(parts) != 5:
        raise ValueError("Неверный формат callback_data.")
    return int(parts[2]), int(parts[3]), int(parts[4])
