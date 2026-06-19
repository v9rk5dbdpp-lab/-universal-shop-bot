from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards.user import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(
        "Привет! Это универсальный магазин-бот. Выбери действие в меню.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "🛍 Каталог")
async def catalog_handler(message: Message) -> None:
    await message.answer("Каталог пока пуст. Скоро здесь появятся товары.")


@router.message(F.text == "📦 Мои заказы")
async def my_orders_handler(message: Message) -> None:
    await message.answer("Раздел заказов пока в разработке.")


@router.message(F.text == "ℹ️ Помощь")
async def help_handler(message: Message) -> None:
    await message.answer("Здесь будет помощь по магазину, оплате и доставке.")
