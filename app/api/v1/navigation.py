import aiogram

import prisma

router: aiogram.Router = aiogram.Router(name="navigation")


@router.message()
async def message_handler(message: aiogram.types.Message, db: prisma.Prisma) -> None:
    await db.user.find_many()
    await message.answer("Hello from my router!")
