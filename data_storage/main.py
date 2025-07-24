import asyncio
from aiogram import Bot, Dispatcher

import logging

from aiogram.client.default import DefaultBotProperties

from handlers.admin_handlers.admin_message_handlers import register_admin_message_handler
from handlers.user_handlers.callback_handlers import register_user_callback_handler
from handlers.user_handlers.message_handlers import register_user_message_handler

from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)

load_dotenv()


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    )
    logger.error("Starting bot")

    BOT_TOKEN = os.getenv("TOKEN")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()

    register_user_message_handler(dp)
    register_user_callback_handler(dp)
    register_admin_message_handler(dp)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
