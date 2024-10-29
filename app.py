import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeAllPrivateChats
from dotenv import load_dotenv

# from common.bot_command_list import private
from middleware.db import DataBaseSession

load_dotenv()
from database.engine import create_db, session_maker, drop_db
from handlers.user_private import router as user_router
from handlers.user_groups import router as group_router
from handlers.admin_private import router as admin_router

# ALLOWED_UPDATES = ["message", "edited_message", 'callback_query']

TOKEN = os.getenv("TOKEN")

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = []
dp = Dispatcher()

dp.include_router(user_router)
dp.include_router(group_router)
dp.include_router(admin_router)
"""
диспетчер здесь выполняет функцию маршрутизатора
то есть получает сообщение от пользователя, анализирует его и вызывает
функцию
"""

"""
* message.answer() автоматически добавляет reply_markup из предыдущего
сообщения пользователя, если он был. Это удобно для создания интерактивных
меню.
* message.answer() - Отправляет сообщение в ответ на последнее сообщение
пользователя (в том же чате).
* message.answer() чаще используется для ответа на сообщения пользователя
в контексте диалога.
* message.send_message() не добавляет reply_markup автоматически. Его
нужно указать явно в параметрах функции.
* message.send_message() - Отправляет сообщение в указанный чат
(не обязательно в ответ на последнее сообщение).
* message.send_message() чаще используется для отправки сообщений в
другие чаты (например, в группы) или для отправки сообщений без связи
с последним сообщением пользователя.
"""


# async def main() -> None:
#
#     logging.basicConfig(level=logging.INFO)
#
#     await create_db()
#
#     dp.update.middleware(DataBaseSession(session_pool=session_maker))
#
#     # для того, чтобы бот не отвечал на сообщения, которые он пропустил
#     # пока был офлайн
#     await bot.delete_webhook(drop_pending_updates=True)
#
#     """
#     commands - это список объектов BotCommand, которые определяют команды
#     в меню. Каждая команда имеет два атрибута:
#     * command — имя команды (например, /start, /help).
#     * description — краткое описание команды.
#
#     scope определяет, для каких чатов будут доступны указанные команды.
#     BotCommandScopeAllPrivateChats() означает, что команды будут доступны во
#     всех личных чатах с ботом.
#
#     bot.set_my_commands() используется только один раз при запуске бота,
#     чтобы обновить главное меню.
#     """
#     await bot.set_my_commands(commands=private, scope=BotCommandScopeAllPrivateChats())
#
#     # allowed_updates определяет какие типы событий бот будет получать
#     # указание конкретных событий позволяет снизить нагрузку на сервер,
#     # улучшить производительность (бот будет быстрее реагировать), упростить
#     # обработку событий
#     await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def  on_startup(bot):
    # await drop_db()
    await create_db()


async def on_shutdown(bot):
    print('бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.delete_my_commands(scope=BotCommandScopeAllPrivateChats())
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


asyncio.run(main())
