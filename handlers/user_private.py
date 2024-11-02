from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from filters.chat_types import ChatTypeFilter
from handlers.menu_processing import get_menu_content
from keyboards.inline import MenuCallback


router = Router()
router.message.filter(ChatTypeFilter(["private"]))


@router.message(CommandStart())
async def start_command(message: Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")
    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


@router.callback_query(MenuCallback.filter())
async def user_menu(
    callback: CallbackQuery, callback_data: MenuCallback, session: AsyncSession
):
    media, reply_markup = await get_menu_content(
        session, level=callback_data.level, menu_name=callback_data.menu_name
    )
    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()
