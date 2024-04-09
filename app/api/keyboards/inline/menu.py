import aiogram
import aiogram.utils.keyboard
from aiogram.utils.i18n import gettext as _


def main_keyboard() -> aiogram.types.InlineKeyboardMarkup:
    """Use in main menu."""
    buttons = [
        [aiogram.types.InlineKeyboardButton(text=_("wallet button"), callback_data="wallet")],
        [aiogram.types.InlineKeyboardButton(text=_("premium button"), callback_data="premium")],
        [aiogram.types.InlineKeyboardButton(text=_("info button"), callback_data="info")],
        [aiogram.types.InlineKeyboardButton(text=_("support button"), callback_data="support")],
    ]

    keyboard = aiogram.utils.keyboard.InlineKeyboardBuilder(markup=buttons)

    keyboard.adjust(1, 1, 2)

    return keyboard.as_markup()
