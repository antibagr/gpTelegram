import aiogram
import aiogram.utils.keyboard
from aiogram.utils.i18n import gettext as _


def contacts_keyboard() -> aiogram.types.InlineKeyboardMarkup:
    """Use when call contacts command."""
    buttons = [
        [aiogram.types.InlineKeyboardButton(text=_("support button"), url="www.google.com")],
    ]

    keyboard = aiogram.utils.keyboard.InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()


def support_keyboard() -> aiogram.types.InlineKeyboardMarkup:
    """Use when call support query."""
    buttons = [
        [aiogram.types.InlineKeyboardButton(text=_("support button"), url="www.google.com")],
        [aiogram.types.InlineKeyboardButton(text=_("back button"), callback_data="menu")],
    ]

    keyboard = aiogram.utils.keyboard.InlineKeyboardBuilder(markup=buttons)

    return keyboard.as_markup()
