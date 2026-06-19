from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config.settings import settings
from keyboards.admin import admin_menu_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("admin"))
async def admin_handler(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        await message.answer("У тебя нет доступа к админ-панели.")
        return

    await message.answer("Админ-панель открыта.", reply_markup=admin_menu_keyboard())


@router.message(F.text == "➕ Добавить товар")
async def add_product_handler(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    await message.answer("Добавление товара будет реализовано следующим шагом.")


@router.message(F.text == "📋 Список товаров")
async def product_list_handler(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    await message.answer("Список товаров пока пуст.")


@router.message(F.text == "📦 Заказы")
async def orders_handler(message: Message) -> None:
    if not message.from_user or not is_admin(message.from_user.id):
        return

    await message.answer("Заказов пока нет.")
