import os

from yookassa import Configuration

from tg_bot.utils.cart_utils import get_cart_items, calculate_cart_total
from tg_bot.utils.excel import save_payment_to_excel

Configuration.account_id = os.getenv("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.getenv("YOOKASSA_SECRET_KEY")


async def create_yookassa_payment(client, amount, description, return_url):

    from yookassa import Payment as YooPayment
    try:
        payment = YooPayment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
        })

        await save_payment_to_excel(client, payment.id, amount, "pending", description)

        return payment
    except Exception as e:
        raise Exception(f"Ошибка создания платежа: {str(e)}")


async def start_payment_step(message, client, state):
    try:
        cart_items = await get_cart_items(client)
        total_amount = await calculate_cart_total(cart_items)

        payment = await create_yookassa_payment(
            amount=total_amount,
            client=client,
            description="Оплата товаров в корзине",
            return_url="https://example.com/success"
        )
        confirmation_url = payment.confirmation.confirmation_url

        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оплатить", url=confirmation_url)]
        ])
        await message.reply(f"Сумма вашей корзины: {total_amount:.2f} руб.", reply_markup=keyboard)
    except Exception as e:
        await message.reply(f"Произошла ошибка при создании платежа: {str(e)}")
    finally:
        await state.clear()


