from aiogram.types import InputMediaPhoto
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_get_banner,
    orm_get_categories,
    orm_get_products,
    orm_delete_from_cart,
    orm_reduce_product_in_cart,
    orm_add_to_cart,
    orm_get_user_carts,
)
from database.paginator import Paginator
from keyboards.inline import (
    get_user_main_buttons,
    get_user_catalogue_buttons,
    get_products_buttons,
    get_user_cart,
)


async def main_menu(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    keyboards = get_user_main_buttons(level=level)

    return image, keyboards


async def catalogue(session, level, menu_name):
    banner = await orm_get_banner(session, menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)
    categories = await orm_get_categories(session)
    keyboards = get_user_catalogue_buttons(level=level, categories=categories)

    return image, keyboards


def pages(paginator: Paginator):
    buttons = dict()
    if paginator.has_previous():
        buttons["⬅️ Пред."] = "previous"

    if paginator.has_next():
        buttons["След. ➡️"] = "next"

    return buttons


async def products(session, level, category, page):
    products = await orm_get_products(session, category_id=category)
    paginator = Paginator(products, page=page)
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.image,
        caption=f"<strong>{product.name}</strong>\n"
        f"{product.description}\n"
        f"Стоимость: {round(product.price, 2)}\n"
        f"<strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )

    pagination_buttons = pages(paginator)

    keyboards = get_products_buttons(
        level=level,
        category=category,
        page=page,
        pagination_buttons=pagination_buttons,
        product_id=product.id,
    )

    return image, keyboards


async def carts(session, level, menu_name, page, user_id, product_id):
    if menu_name == "delete":
        await orm_delete_from_cart(session, user_id, product_id)
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await orm_reduce_product_in_cart(session, user_id, product_id)
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await orm_add_to_cart(session, user_id, product_id)

    carts = await orm_get_user_carts(session, user_id)

    if not carts:
        banner = await orm_get_banner(session, "cart")
        image = InputMediaPhoto(
            media=banner.image, caption=f"<strong>{banner.description}</strong>"
        )

        keyboards = get_user_cart(
            level=level,
            page=None,
            pagination_buttons=None,
            product_id=None,
        )

    else:
        paginator = Paginator(carts, page)
        cart = paginator.get_page()[0]
        cart_price = round(cart.quantity * cart.product.price, 2)
        totel_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.namr}</strong>\n"
            f"{cart.product.price}BYN x {cart.quantity} = {cart_price}BYN\n"
            f"Товар {paginator.page} из {paginator.pages} в корзине\n"
            f"Общая стоимость товаров в корзине {totel_price}BYN",
        )

        pagination_buttons = pages(paginator)

        keyboards = get_user_cart(
            level=level,
            page=page,
            pagination_buttons=pagination_buttons,
            product_id=cart.product.id,
        )

        return image, keyboards


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    category: int | None = None,
    page: int | None = None,
    user_id: int | None = None,
):
    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalogue(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category, page)
    elif level == 3:
        return ...
