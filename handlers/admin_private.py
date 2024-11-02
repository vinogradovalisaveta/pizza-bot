from aiogram import Router, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_query import (
    orm_add_product,
    orm_get_products,
    orm_delete_product,
    orm_update_product,
    orm_get_product,
    orm_get_categories,
    orm_get_info_pages,
    orm_change_banner_image,
)
from keyboards.inline import get_callback_buttons
from keyboards.reply import get_keyboard

router = Router()

ADMIN_KB = get_keyboard(
    "Добавить товар",
    "Ассортимент",
    "Добавить/изменить баннер",
    placeholder="Выберите действие",
    sizes=(2,),
)


@router.message(Command("admin"))
async def admin_features(message: Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)


@router.message(F.text == "Ассортимент")
async def admin_features(message: Message, session: AsyncSession):
    categories = await orm_get_categories(session)
    buttons = {category.name: f"category_{category.id}" for category in categories}
    await message.answer(
        "Выберите категорию", reply_markup=get_callback_buttons(buttons=buttons)
    )


@router.callback_query(F.data.startswith("category_"))
async def starring_at_product(callback: CallbackQuery, session: AsyncSession):
    category_id = callback.data.split("_")[-1]
    for product in await orm_get_products(session, category_id):
        await callback.message.answer_photo(
            product.image,
            caption=f"<strong>{product.name}"
            f"</strong>\n{product.description}\nСтоимость: {round(product.price, 2)}",
            reply_markup=get_callback_buttons(
                buttons={
                    "Удалить товар": f"delete_{product.id}",
                    "Изменить товар": f"update_{product.id}",
                }
            ),
        )
    await callback.answer()
    await callback.message.answer("ОК, вот список товаров")


@router.callback_query(F.data.startswith("delete_"))
async def delete_product_callback(callback: CallbackQuery, session: AsyncSession):
    product_id = callback.data.split("_")[-1]
    await orm_delete_product(session, int(product_id))

    # эта строка отключает "подсветку" кнопки, сообщение передавать не обязательно
    await callback.answer("Товар удален")

    # эта строка отправляет сообщеие в чат
    await callback.message.answer("Товар удален")


class AddBanner(StatesGroup):
    image = State()


@router.message(StateFilter(None), F.text == "Добавить/изменить баннер")
async def add_image2(message: Message, state: FSMContext, session: AsyncSession):
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    await message.answer(
        f"Отправьте фото баннера\nВ описании укажите для какой страницы:\n{', '.join(pages_names)}"
    )
    await state.set_state(AddBanner.image)


@router.message(AddBanner.image, F.photo)
async def add_banner(message: Message, state: FSMContext, session: AsyncSession):
    image_id = message.photo[-1].file_id
    for_page = message.caption.strip()
    pages_names = [page.name for page in await orm_get_info_pages(session)]
    if for_page not in pages_names:
        await message.answer(
            f"Введите корректное название страницы из списка ниже:\n{', '.join(pages_names)}"
        )

    await orm_change_banner_image(session, for_page, image_id)
    await message.answer("Баннер добавлен/изменен")
    await state.clear()


@router.message(AddBanner.image)
async def add_banner2(message: Message, state: FSMContext):
    await message.answer("Отправьте фото баннера или отмена")


class AddProduct(StatesGroup):
    name = State()
    description = State()
    category = State()
    price = State()
    image = State()

    product_to_update = None

    texts = {
        "AddProduct:name": "Введите название заново",
        "AddProduct:description": "введите описание заново",
        "AddProduct:category": "Выберите категорию заново",
        "AddProduct:price": "введите стоиомть заново",
        "AddProduct:image": "это последний шаг",
    }


@router.callback_query(StateFilter(None), F.data.startswith("update_"))
async def update_product_callback(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    product_id = callback.data.split("_")[-1]
    product_to_update = await orm_get_product(session, int(product_id))

    AddProduct.product_to_update = product_to_update
    await callback.answer()
    await callback.message.answer(
        "Введите название товара", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@router.message(StateFilter(None), F.text == "Добавить товар")
async def add_product(message: Message, state: FSMContext):
    await message.answer("Введите название товара", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AddProduct.name)


@router.message(StateFilter("*"), Command("отмена"))
@router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    if AddProduct.product_to_update:
        AddProduct.product_to_update = None

    await state.clear()
    await message.answer("Действия отменеы", reply_markup=ADMIN_KB)


@router.message(StateFilter("*"), Command("назад"))
@router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_step_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer("Предыдущего шага нет")
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"ок, вы вернулись к предыдущему шагу\n{AddProduct.texts[previous.state]}"
            )
            return
        previous = step


@router.message(AddProduct.name, or_f(F.text, F.text))
async def add_name(message: Message, state: FSMContext):
    if message.text == "." and AddProduct.product_to_update:
        await state.update_data(name=AddProduct.product_to_update.name)
    else:
        if 4 >= len(message.text) > 75:
            await message.answer(
                "название товара не должно превышать 75 символов\nвведите заново"
            )
            return

        await state.update_data(name=message.text)
    await message.answer("Введите описание товара")
    await state.set_state(AddProduct.description)


@router.message(AddProduct.name)
async def add_name2(message: Message):
    await message.answer("вы вввели недопустимые данныеб введите название товара")


@router.message(AddProduct.description, F.text)
async def add_description(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "." and AddProduct.product_to_update:
        await state.update_data(description=AddProduct.product_to_update.description)
    else:
        await state.update_data(description=message.text)

    categories = await orm_get_categories(session)
    print(categories)
    buttons = {category.name: str(category.id) for category in categories}
    await message.answer(
        "Выберите категорию", reply_markup=get_callback_buttons(buttons=buttons)
    )
    await state.set_state(AddProduct.category)


@router.message(AddProduct.description)
async def add_description2(message: Message):
    await message.answer("вы ввели недопустимые данные, введите текст описания товара")


@router.callback_query(AddProduct.category)
async def category_choice(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    if int(callback.data) in [
        category.id for category in await orm_get_categories(session)
    ]:
        await callback.answer()
        await state.update_data(category=callback.data)
        await callback.message.answer("Введите цену товара")
        await state.set_state(AddProduct.price)
    else:
        await callback.message.answer("Выберите корректную категорию")
        await callback.answer()


@router.message(AddProduct.category)
async def category_choice2(message: Message):
    await message.answer("Выберите корректную категорию")


@router.message(AddProduct.price, or_f(F.text, F.text))
async def add_price(message: Message, state: FSMContext):
    if message.text == "." and AddProduct.product_to_update:
        await state.update_data(price=AddProduct.product_to_update.price)
    else:
        try:
            float(message.text)
        except ValueError:
            await message.answer("введите корректное значение цены")
            return

    await state.update_data(price=message.text)
    await message.answer("Загрузите изображение товара")
    await state.set_state(AddProduct.image)


@router.message(AddProduct.price)
async def add_price2(message: Message):
    await message.answer("вы ввели недопустимые данные, введите стоимость товара")


@router.message(AddProduct.image, or_f(F.photo, F.text))
async def add_image(message: Message, state: FSMContext, session: AsyncSession):
    if message.text and F.text == "." and AddProduct.product_to_update:
        await state.update_data(image=AddProduct.product_to_update.image)

    else:
        await state.update_data(image=message.photo[-1].file_id)

    data = await state.get_data()
    try:
        if AddProduct.product_to_update:
            await orm_update_product(session, AddProduct.product_to_update.id, data)
        else:
            await orm_add_product(session, data)

        await message.answer("Товар добавлен", reply_markup=ADMIN_KB)
        await state.clear()

    except Exception as e:
        await message.answer(f"Ошибка: \n{str(e)}", reply_markup=ADMIN_KB)
        await state.clear()

    AddProduct.product_to_update = None


@router.message(AddProduct.image)
async def add_image2(message: Message):
    await message.answer("отправьте изображение")
