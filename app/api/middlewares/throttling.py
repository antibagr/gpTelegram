import typing

import aiogram
import cachetools

from app.api.middlewares.base import middleware, SkipMiddleware
from app.dto.types import Handler, Json


class ThrottlingMiddleware(aiogram.BaseMiddleware):
    def __init__(self, rate_limit: float) -> None:
        self.cache: cachetools.TTLCache[int, None] = cachetools.TTLCache(maxsize=10_000, ttl=rate_limit)

    @middleware
    async def __call__(
        self,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        if not isinstance(event, aiogram.types.Message):
            raise SkipMiddleware

        if event.chat.id in self.cache:
            return None
        self.cache[event.chat.id] = None
        return await handler(event, data)
