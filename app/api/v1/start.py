import aiogram
import aiogram.filters
from aiogram.utils.i18n import gettext as _

from app.api.keyboards.inline.menu import main_keyboard

router = aiogram.Router(name="start")


@router.message(aiogram.filters.CommandStart())
async def start_handler(message: aiogram.types.Message) -> None:
    """Welcome message."""
    await message.answer(text=_("first message"), reply_markup=main_keyboard())
