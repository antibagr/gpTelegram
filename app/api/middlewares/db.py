import typing

import aiogram

from app.api.middlewares.base import middleware
from app.dto.types import Handler, Json
from app.repository.db import get_db


class DatabaseMiddleware(aiogram.BaseMiddleware):
    def __init__(self, timeout: int) -> None:
        self._timeout = timeout

    @middleware
    async def __call__(
        self,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        if "db" in data:
            return await handler(event, data)
        async with get_db(timeout=self._timeout) as db:
            data["db"] = db
            return await handler(event, data)
