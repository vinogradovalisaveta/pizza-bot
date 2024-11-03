from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from aiogram.utils.keyboard import InlineKeyboardBuilder


class MenuCallback(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None


def get_products_buttons(
    *,
    level: int,
    category: int,
    page: int,
    pagination_buttons: dict,
    product_id: int,
    sizes: tuple[int] = (2, 1),
):
    keyboard = InlineKeyboardBuilder()

    keyboard.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data=MenuCallback(level=level - 1, menu_name="catalog").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Корзина 🛒",
            callback_data=MenuCallback(level=3, menu_name="cart").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Купить 💵",
            callback_data=MenuCallback(
                level=level, menu_name="add_to_cart", product_id=product_id
            ).pack(),
        )
    )

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_buttons.items():
        if menu_name == "next":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page + 1,
                    ).pack(),
                )
            )

        elif menu_name == "previous":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallback(
                        level=level,
                        menu_name=menu_name,
                        category=category,
                        page=page - 1,
                    ).pack(),
                )
            )

    return keyboard.row(*row).as_markup()


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


def get_user_cart(
    *,
    level: int,
    page: int | None = None,
    pagination_buttons: dict | None,
    product_id: int | None,
    sizes: tuple[int] = (3,),
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.add(
            InlineKeyboardButton(
                text="Удалить",
                callback_data=MenuCallback(
                    level=level, menu_name="delete", product_id=product_id, page=page
                ).pack(),
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="-1",
                callback_data=MenuCallback(
                    level=level, menu_name="decrement", product_id=product_id, page=page
                ).pack(),
            )
        )
        keyboard.add(
            InlineKeyboardButton(
                text="+1",
                callback_data=MenuCallback(
                    level=level, menu_name="increment", product_id=product_id, page=page
                ).pack(),
            )
        )

        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_buttons.items():
            if menu_name == "next":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallback(
                            level=level, menu_name=menu_name, page=page + 1
                        ).pack(),
                    )
                )
            elif menu_name == "previous":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallback(
                            level=level, menu_name=menu_name, page=page - 1
                        ).pack(),
                    )
                )

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(
                text="На главную",
                callback_data=MenuCallback(level=0, menu_name="main").pack(),
            ),
            InlineKeyboardButton(
                text="Заказать",
                callback_data=MenuCallback(level=0, menu_name="order").pack(),
            ),
        ]
        return keyboard.row(*row2).as_markup()

    else:
        keyboard.add(
            InlineKeyboardButton(
                text="На главную",
                callback_data=MenuCallback(level=0, menu_name="main").pack(),
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


def get_user_catalogue_buttons(
    *, level: int, categories: list, sizes: tuple[int] = (2,)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(
            text="Назад",
            callback_data=MenuCallback(level=level - 1, menu_name="main").pack(),
        )
    )
    keyboard.add(
        InlineKeyboardButton(
            text="Корзина 🛒",
            callback_data=MenuCallback(level=3, menu_name="cart").pack(),
        )
    )

    for category in categories:
        keyboard.add(
            InlineKeyboardButton(
                text=category.name,
                callback_data=MenuCallback(
                    level=level + 1, menu_name=category.name, category=category.id
                ).pack(),
            )
        )

    return keyboard.adjust(*sizes).as_markup()
