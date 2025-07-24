from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    document = State()
    photo = State()
    audio = State()
    get_doc = State()
    get_photo = State()
    get_audio = State()
