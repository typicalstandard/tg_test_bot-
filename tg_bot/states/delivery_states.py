from aiogram.fsm.state import State, StatesGroup

class UserInfo(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()
    waiting_for_email = State()