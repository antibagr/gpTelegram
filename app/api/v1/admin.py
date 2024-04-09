import aiogram
import aiogram.filters

from app.api.filters.admin import AdminFilter

router = aiogram.Router(name="admin")


@router.message(aiogram.filters.Command(commands="export_users"), AdminFilter())
async def _test_admin(
    message: aiogram.types.Message,
) -> aiogram.types.Message:
    return await message.answer("Exporting users is not implemented yet.")
