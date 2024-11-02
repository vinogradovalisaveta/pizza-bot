import math

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Product


# paginator


class Paginator:
    """
    класс для разбиения списка объектов на страницы

    атрибуты:
    array (list | tuple): список или кортеж объектов, которые нужно разбить
    на страницы
    page (int, optional): номер текущей страницы, по умолчанию = 1
    per_page (int, optional): количество объектов на странице, по умолчанию = 1
    """

    def __init__(self, array: list | tuple, page: int = 1, per_page: int = 1):
        self.array = array
        self.per_page = per_page
        self.page = page
        self.len = len(self.array)
        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        """
        вычисляет начальный и конечный индексы среза на основе номера
        текущей страницы (self.page) и количества объеков на странице
        (self.per_page)
        :return: list: срез списка объектов для запрашиваемой страницы
        """

        # рассчитывает смещение от начала списка до первого объекта на
        # текущей странице
        start = (self.page - 1) * self.per_page

        # вычисляет конечный индекс среза
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        """
        :return: срез списка объектов для конкретной страницы
        """
        page_items = self.__get_slice()
        return page_items

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError(f"next page does not exist. use has_next() to check before")

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self.__get_slice()
        raise IndexError(
            f"previous page does not exist. use has_previous() to check before"
        )


async def orm_add_product(session: AsyncSession, data: dict):
    obj = Product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],
    )
    session.add(obj)
    await session.commit()


async def orm_get_products(session: AsyncSession):
    query = select(Product)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_product(session: AsyncSession, product_id: int):
    query = select(Product).where(Product.id == product_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_product(session: AsyncSession, product_id: int, data):
    query = (
        update(Product)
        .where(Product.id == product_id)
        .values(
            name=data["name"],
            description=data["description"],
            price=float(data["price"]),
            image=data["image"],
        )
    )
    await session.execute(query)
    await session.commit()


async def orm_delete_product(session: AsyncSession, product_id: int):
    query = delete(Product).where(Product.id == product_id)
    await session.execute(query)
    await session.commit()
