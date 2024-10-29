from aiogram import Router, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import as_marked_section, Bold, as_list
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import orm_get_products
from filters.chat_types import ChatTypeFilter
from keyboards.inline import get_callback_buttons
from keyboards.reply import (
    start_kb,
    remove_keyboard,
    start_kb2,
    start_kb3,
    test_kb,
    get_keyboard,
)

router = Router()
router.message.filter(ChatTypeFilter(["private"]))


@router.message(CommandStart())
async def start_command(message: Message):
    await message.answer('привет, я виртуальный помощник',
                         reply_markup=get_callback_buttons(buttons={
                             'нажми меня': 'some_1',
                         }))


@router.callback_query(F.data.startswith('some_'))
async def counter(callback: CallbackQuery):
    number = int(callback.data.split('_')[-1])
    await callback.message.edit_text(
        text=f'нажатий - {number}',
        reply_markup=get_callback_buttons(buttons={
            'нажми еще раз': f'some_{number+1}'
        })
    )


# @router.message(CommandStart())
# async def start(message: Message):
#     await message.answer(
#         "Привет, я виртуальный помощник",
#         reply_markup=get_keyboard(
#             "Меню",
#             "О магазине",
#             "Варианты оплаты",
#             "Варианты доставки",
#             placeholder="Что вас интересует?",
#             sizes=(2, 2),
#         ),
#     )


# @router.message(CommandStart())
# async def start_cmd(message: Message):
#     await message.answer('it was command start',
#                          reply_markup=start_kb3.as_markup())


"""
эта запись совмещает два декоратора, @router.message(Command('menu'))
и @router.message(F.text.lower().contains('menu')) с помощью оператора or_f
"""


# @router.message(or_f(Command("Меню"), (F.text.lower().contains("меню"))))
# async def menu(message: Message, session: AsyncSession):
#     for product in await orm_get_products(session):
#         await message.answer_photo(
#             product.image,
#             caption=f"<strong>{product.name}"
#             f"</strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
#         )
#     await message.answer("the menu:", reply_markup=remove_keyboard)
#
#
# @router.message(or_f(Command("О магазине"), (F.text.lower().contains("о магазине"))))
# async def about(message: Message):
#     await message.answer("about", reply_markup=test_kb)
#
#
# @router.message(or_f(Command("Payment"), (F.text.lower().contains("payment"))))
# async def payment(message: Message):
#     text = as_marked_section(Bold("Payment:"), "by card", "cash", marker="- ")
#     await message.answer(text.as_html())
#
#
# @router.message(or_f(Command("Shipping"), (F.text.lower().contains("shipping"))))
# async def shipping(message: Message):
#     text = as_list(
#         as_marked_section(Bold("Shipping:"), "courier", "pickup", marker="💁 "),
#         as_marked_section(Bold("нельзя:"), "почта", "голуби", marker="🤡 "),
#         sep="\n-------------\n",
#     )
#     await message.answer(text.as_html())
#
#
# @router.message(F.contact)
# async def get_contact(message: Message):
#     await message.answer(f"got number")
#     await message.answer(str(message.contact))
#
#
# @router.message(F.location)
# async def get_location(message: Message):
#     await message.answer(f"got location")
#     await message.answer(str(message.location))
