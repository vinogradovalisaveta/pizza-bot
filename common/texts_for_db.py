from aiogram.utils.formatting import as_marked_section, Bold, as_list

categories = ["Еда", "Напитки"]

description_for_info_pages = {
    "main": "Добро пожаловать!",
    "about": "Пиццерия\nРежим работы: круглосуточно",
    "payment": as_marked_section(
        Bold("Варианты оплаты:"),
        "Картой в боте",
        "При получении картой или наличными",
        "В заведении",
        marker="💸",
    ).as_html(),
    "shipping": as_list(
        as_marked_section(
            Bold("Варианты доставки:"),
            "Курьер",
            "Самовывоз",
            "Покушаю у вас",
            marker="🤝",
        ),
        as_marked_section(Bold("Нельзя"), "Почта", "Голуби", marker="⛔"),
        sep="\n---------------\n",
    ).as_html(),
    "catalog": "Категории",
    "cart": "В корзине пока ничего нет",
}
