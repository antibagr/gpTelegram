import aiogram
import aiogram.filters

import prisma


class AdminFilter(aiogram.filters.BaseFilter):
    """Allows only administrators (whose database column is_admin=True)."""

    async def __call__(
        self,
        message: aiogram.types.Message,
        db: prisma.Prisma,
    ) -> bool:
        if not message.from_user:
            return False
        return bool(await db.user.find_first(where={"id": message.from_user.id}))
