from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


def get_user_main_buttons(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    buttons = {
        "Товары 📔": "catalogue",
        "Корзина 🛒": "cart",
        "О нас 🔎": "about",
        "Оплата 💸": "payment",
        "Доставка 🚀": "shipping",
    }
    for text, menu_name in buttons.items():
        if menu_name == "catalogue":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(
                        level=level + 1, menu_name=menu_name
                    ).pack(),
                )
            )
        elif menu_name == "cart":
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(level=3, menu_name=menu_name).pack(),
                )
            )
        else:
            keyboard.add(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(level=level, menu_name=menu_name).pack(),
                )
            )

    return keyboard.adjust(*sizes).as_markup()


def get_callback_buttons(
    *,
    buttons: dict[str, str],
    sizes: tuple[int] = (2,),
):
    keyboard = InlineKeyboardBuilder()
    for text, data in buttons.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()
