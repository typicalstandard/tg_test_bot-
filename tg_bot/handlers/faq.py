from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Создаем Router
router = Router()

def register_handlers(router: Router):
    @router.callback_query(lambda c: c.data == 'faq')
    async def faq_handler(callback_query: types.CallbackQuery):
        """
        Вывод FAQ с инлайн-кнопками для вопросов.
        """
        await callback_query.answer()
        faq_list = {
            "Как сделать заказ?": "Чтобы сделать заказ, выберите товар и добавьте его в корзину.",
            "Как оплатить заказ?": "Оплата производится через ЮKassa с последующим подтверждением об оплате.",
            "Как связаться с поддержкой?": "Свяжитесь с нами через наш официальный сайт или Telegram."
        }

        # Создаем клавиатуру с кнопками
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=question, callback_data=f"faq_{idx}")]
                for idx, question in enumerate(faq_list.keys())
            ]
        )
        await callback_query.message.answer("FAQ:", reply_markup=markup)

    @router.callback_query(lambda c: c.data.startswith('faq_'))
    async def faq_answer_handler(callback_query: types.CallbackQuery):
        """
        Ответ на выбранный вопрос из FAQ.
        """
        faq_answers = [
            "Чтобы сделать заказ, выберите товар и добавьте его в корзину.",
            "Оплата производится через ЮKassa с последующим подтверждением об оплате.",
            "Свяжитесь с нами через наш официальный сайт или Telegram."
        ]
        index = int(callback_query.data.split("_")[1])
        if 0 <= index < len(faq_answers):
            await callback_query.message.answer(faq_answers[index])
        else:
            await callback_query.message.answer("Вопрос не найден.")
