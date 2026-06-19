from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def admin_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить товар")],
            [KeyboardButton(text="📋 Список товаров"), KeyboardButton(text="📦 Заказы")],
            [KeyboardButton(text="⬅️ В меню")],
        ],
        resize_keyboard=True,
    )
