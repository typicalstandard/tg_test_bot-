from aiogram import types, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async
from bot_admin_panel.models import FAQ

router = Router()

def register_handlers(router: Router):
    router.callback_query.register(faq_handler, lambda c: c.data == "faq")
    router.callback_query.register(faq_answer_handler, lambda c: c.data.startswith("faq_"))
    router.message.register(add_faq_handler, lambda message: message.text.startswith("/addfaq"))


async def faq_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    try:
        faqs = await sync_to_async(list)(FAQ.objects.all().order_by("created_at"))
        if not faqs:
            await callback_query.message.answer("FAQ пуст. Пока вопросов нет.")
            return
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=faq.question, callback_data=f"faq_{faq.id}")]
                for faq in faqs
            ]
        )
        await callback_query.message.answer("FAQ:", reply_markup=markup)
    except Exception as e:
        await callback_query.message.answer("Произошла ошибка при загрузке FAQ.")
        print(f"Ошибка в faq_handler: {e}")

async def faq_answer_handler(callback_query: types.CallbackQuery):
    await callback_query.answer()
    try:
        faq_id = int(callback_query.data.split("_")[1])
        faq = await sync_to_async(FAQ.objects.get)(id=faq_id)
        await callback_query.message.answer(f"Ответ:\n{faq.answer}")
    except FAQ.DoesNotExist:
        await callback_query.message.answer("Данный вопрос не найден.")
    except Exception as e:
        await callback_query.message.answer("Произошла ошибка при получении ответа.")
        print(f"Ошибка в faq_answer_handler: {e}")

async def add_faq_handler(message: types.Message):
    try:
        _, data = message.text.split(maxsplit=1)
        question, answer = data.split("|", maxsplit=1)
        faq_obj = await sync_to_async(FAQ.objects.create)(
            question=question.strip(),
            answer=answer.strip()
        )
        await message.reply(f"Новый FAQ добавлен:\nВопрос: {faq_obj.question}\nОтвет: {faq_obj.answer}")
    except ValueError:
        await message.reply("Неверный формат. Используйте:\n/addfaq Вопрос | Ответ")
    except Exception as e:
        await message.reply("Произошла ошибка при добавлении FAQ.")
        print(f"Ошибка в add_faq_handler: {e}")

