"Запуск бота"
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher

import bot_common


logging.basicConfig(level=logging.INFO)


async def main():
    """Запуск бота"""
    bot = Bot(token=os.environ['BOT_TOKEN'])
    dp = Dispatcher()

    dp.include_routers(bot_common.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
