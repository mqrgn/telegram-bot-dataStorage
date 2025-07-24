from aiogram import Dispatcher, types
from aiogram.filters import Command

from states.admin import IsAdmin


async def admin_command(message: types.Message) -> None:
    await message.answer("Привет, ты админ")


def register_admin_message_handler(dp: Dispatcher):
    dp.message.register(admin_command, Command('admin'), IsAdmin())
