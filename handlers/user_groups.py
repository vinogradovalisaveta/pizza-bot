from string import punctuation

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from filters.chat_types import ChatTypeFilter

router = Router()
router.message.filter(ChatTypeFilter(["group", "supergroup"]))
restricted_words = {"кабан", "хомяк", "выхухоль", "хуй"}


@router.message(Command("admin"))
async def get_admins(message: Message, bot: Bot):
    chat_id = message.chat.id
    admins_list = await bot.get_chat_administrators(chat_id)
    admins_list = [
        member.user.id
        for member in admins_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admins_list
    if message.from_user.id in admins_list:
        await message.delete()


def clean_text(text: str):
    return text.translate(str.maketrans("", "", punctuation))


@router.edited_message()
@router.message()
async def cleaner(message: Message):
    """
    функция для модерации сообщений
    сообщение переводится в нижний регистр, разбивается на слова и каждое
    слово проверяется на наличие его в множестве запрещенных слов
    если в сообщении есть запрещеннын слова - сообщение удаляется, пользователь
    банится
    """
    if restricted_words.intersection(message.text.lower().split()):

        # предупреждение
        await message.answer(f"@{message.from_user.username}, следи за базаром")

        # удаление сообщения
        await message.delete()

        # бан пользователя
        await message.chat.ban(message.from_user.id)
