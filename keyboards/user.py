from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Каталог")],
            [KeyboardButton(text="📦 Мои заказы"), KeyboardButton(text="ℹ️ Помощь")],
        ],
        resize_keyboard=True,
    )
