import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

from database.db import add_product, init_db, get_all_products, delete_product


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
]

dp = Dispatcher()
add_product_states = {}


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 VPN"), KeyboardButton(text="🎁 Gift Cards")],
        [KeyboardButton(text="💳 Prepaid Cards"), KeyboardButton(text="📦 Товары")],
        [KeyboardButton(text="🛠 Услуги"), KeyboardButton(text="ℹ️ Помощь")],
    ],
    resize_keyboard=True,
)

services_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗑 Вынос мусора"), KeyboardButton(text="🚚 Доставка")],
        [KeyboardButton(text="🪟 Мытье окон"), KeyboardButton(text="🐕 Выгул собак")],
        [KeyboardButton(text="🔧 Сантехника"), KeyboardButton(text="⚡ Электрика")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)

gift_cards_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🍎 iTunes"), KeyboardButton(text="🎮 PlayStation")],
        [KeyboardButton(text="🎯 Xbox"), KeyboardButton(text="🕹 Steam")],
        [KeyboardButton(text="💳 Visa Prepaid"), KeyboardButton(text="💳 Mastercard Prepaid")],
        [KeyboardButton(text="⬅️ Назад")],
    ],
    resize_keyboard=True,
)

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить товар")],
        [KeyboardButton(text="📦 Все товары"), KeyboardButton(text="🧾 Заказы")],
        [KeyboardButton(text="🏪 Главное меню")],
    ],
    resize_keyboard=True,
)

category_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔐 VPN"), KeyboardButton(text="🎁 Gift Cards")],
        [KeyboardButton(text="💳 Prepaid Cards"), KeyboardButton(text="📦 Товары")],
        [KeyboardButton(text="🛠 Услуги")],
        [KeyboardButton(text="❌ Отмена")],
    ],
    resize_keyboard=True,
)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def cancel_add_product(user_id: int):
    if user_id in add_product_states:
        del add_product_states[user_id]


@dp.message(CommandStart())
async def start(message: types.Message):
    if is_admin(message.from_user.id):
        await message.answer(
            "👑 Админ-панель\n\n"
            "Команды:\n"
            "/id — узнать свой Telegram ID\n"
            "/catalog — каталог\n"
            "/admin — меню администратора",
            reply_markup=main_menu,
        )
    else:
        await message.answer(
            "🛍 Добро пожаловать в магазин!\n\n"
            "Команды:\n"
            "/catalog — каталог\n"
            "/id — узнать свой Telegram ID",
            reply_markup=main_menu,
        )


@dp.message(Command("id"))
async def get_id(message: types.Message):
    await message.answer(
        f"Твой Telegram ID:\n`{message.from_user.id}`",
        parse_mode="Markdown",
    )


@dp.message(Command("catalog"))
async def catalog(message: types.Message):
    products = get_all_products()

    if not products:
        await message.answer(
            "📦 Сейчас товаров в наличии нет.",
            reply_markup=main_menu,
        )
        return

    catalog_text = "📦 Товары в наличии:\n\n"

    for product in products:
        product_id, name, category, description, price = product

        catalog_text += (
            f"🆔 {product_id}\n"
            f"📌 {name}\n"
            f"📂 {category}\n"
            f"💰 {price} ₽\n"
            f"📝 {description or '-'}\n\n"
        )

    await message.answer(catalog_text, reply_markup=main_menu)


@dp.message(Command("admin"))
async def admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У тебя нет доступа к админ-панели.")
        return

    await message.answer(
        "👑 Админ-панель\n\n"
        "Выбери действие:",
        reply_markup=admin_menu,
    )


@dp.message(Command("delete"))
async def delete_product_command(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У тебя нет доступа к этой функции.")
        return

    parts = message.text.split()

    if len(parts) != 2:
        await message.answer(
            "🗑 Укажи ID товара для удаления.\n\n"
            "Пример:\n"
            "/delete 2",
            reply_markup=admin_menu,
        )
        return

    try:
        product_id = int(parts[1])
    except ValueError:
        await message.answer(
            "⚠️ ID товара должен быть числом.\n\n"
            "Пример:\n"
            "/delete 2",
            reply_markup=admin_menu,
        )
        return

    delete_product(product_id)

    await message.answer(
        f"✅ Товар с ID {product_id} удалён.",
        reply_markup=admin_menu,
    )


@dp.message(lambda message: message.text == "➕ Добавить товар")
async def add_product_button(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У тебя нет доступа к этой функции.")
        return

    add_product_states[message.from_user.id] = {"step": "name"}

    await message.answer(
        "➕ Добавление товара\n\n"
        "Введите название товара:",
        reply_markup=admin_menu,
    )


@dp.message(lambda message: message.text == "📦 Все товары")
async def all_products_button(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У тебя нет доступа к этой функции.")
        return

    products = get_all_products()

    if not products:
        await message.answer(
            "📦 В базе пока нет товаров.",
            reply_markup=admin_menu,
        )
        return

    text = "📦 Список товаров:\n\n"

    for product in products:
        product_id, name, category, description, price = product

        text += (
            f"🆔 {product_id}\n"
            f"📌 {name}\n"
            f"📂 {category}\n"
            f"💰 {price} ₽\n"
            f"📝 {description or '-'}\n\n"
        )

    await message.answer(
        text,
        reply_markup=admin_menu,
    )


@dp.message(lambda message: message.text == "🧾 Заказы")
async def orders_button(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У тебя нет доступа к этой функции.")
        return

    await message.answer(
        "🧾 Заказов пока нет.",
        reply_markup=admin_menu,
    )


@dp.message(lambda message: message.text == "🏪 Главное меню")
async def back_to_main_from_admin(message: types.Message):
    cancel_add_product(message.from_user.id)
    await message.answer("🏪 Главное меню:", reply_markup=main_menu)


@dp.message()
async def handle_menu(message: types.Message):
    text = message.text
    user_id = message.from_user.id

    if text == "❌ Отмена":
        cancel_add_product(user_id)
        await message.answer(
            "❌ Добавление товара отменено.",
            reply_markup=admin_menu if is_admin(user_id) else main_menu,
        )
        return

    if user_id in add_product_states:
        state = add_product_states[user_id]
        step = state.get("step")

        if step == "name":
            state["name"] = text
            state["step"] = "category"

            await message.answer(
                "Выберите категорию товара:",
                reply_markup=category_menu,
            )
            return

        if step == "category":
            state["category"] = text
            state["step"] = "price"

            await message.answer(
                "Введите цену товара числом.\n\n"
                "Например: 1000",
                reply_markup=admin_menu,
            )
            return

        if step == "price":
            try:
                price = int(text.strip())
            except ValueError:
                await message.answer(
                    "⚠️ Цена должна быть числом.\n\n"
                    "Например: 1000"
                )
                return

            state["price"] = price
            state["step"] = "description"

            await message.answer(
                "Введите описание товара.\n\n"
                "Если описание не нужно, напишите: -"
            )
            return

        if step == "description":
            description = "" if text.strip() == "-" else text

            add_product(
                name=state["name"],
                category=state["category"],
                price=state["price"],
                description=description,
            )

            product_name = state["name"]
            product_category = state["category"]
            product_price = state["price"]
            cancel_add_product(user_id)

            await message.answer(
                "✅ Товар добавлен в базу данных.\n\n"
                f"Название: {product_name}\n"
                f"Категория: {product_category}\n"
                f"Цена: {product_price}",
                reply_markup=admin_menu,
            )
            return

    if text == "🛠 Услуги":
        await message.answer("🛠 Выберите услугу:", reply_markup=services_menu)

    elif text == "🎁 Gift Cards":
        await message.answer("🎁 Выберите тип карты:", reply_markup=gift_cards_menu)

    elif text == "⬅️ Назад":
        await message.answer("🏪 Главное меню:", reply_markup=main_menu)

    elif text == "🔐 VPN":
        await message.answer(
            "🔐 VPN-подписки пока в разработке.",
            reply_markup=main_menu,
        )

    elif text == "💳 Prepaid Cards":
        await message.answer(
            "💳 Предоплаченные карты пока в разработке.",
            reply_markup=main_menu,
        )

    elif text == "📦 Товары":
        products = get_all_products()

        if not products:
            await message.answer(
                "📦 Сейчас товаров в наличии нет.",
                reply_markup=main_menu,
            )
            return

        catalog_text = "📦 Товары в наличии:\n\n"

        for product in products:
            product_id, name, category, description, price = product

            catalog_text += (
                f"🆔 {product_id}\n"
                f"📌 {name}\n"
                f"📂 {category}\n"
                f"💰 {price} ₽\n"
                f"📝 {description or '-'}\n\n"
            )

        await message.answer(
            catalog_text,
            reply_markup=main_menu,
        )

    elif text == "ℹ️ Помощь":
        await message.answer(
            "ℹ️ Здесь будет информация о магазине, оплате и поддержке.",
            reply_markup=main_menu,
        )

    elif text in {
        "🗑 Вынос мусора",
        "🚚 Доставка",
        "🪟 Мытье окон",
        "🐕 Выгул собак",
        "🔧 Сантехника",
        "⚡ Электрика",
    }:
        await message.answer(
            f"{text}\n\nУслуга пока в разработке. Скоро здесь можно будет оформить заявку.",
            reply_markup=services_menu,
        )

    elif text in {
        "🍎 iTunes",
        "🎮 PlayStation",
        "🎯 Xbox",
        "🕹 Steam",
        "💳 Visa Prepaid",
        "💳 Mastercard Prepaid",
    }:
        await message.answer(
            f"{text}\n\nРаздел пока в разработке. Скоро здесь появятся цифровые товары.",
            reply_markup=gift_cards_menu,
        )

    else:
        await message.answer(
            "Я пока понимаю только команды и кнопки меню.",
            reply_markup=main_menu,
        )


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN не указан в .env")

    init_db()

    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())