import os

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from dotenv import load_dotenv

load_dotenv()
ADMIN_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]


class IsAdmin(BaseFilter):
    async def __call__(self, obj: TelegramObject) -> bool:
        return obj.from_user.id in ADMIN_IDS
