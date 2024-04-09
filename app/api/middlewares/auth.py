import typing

import aiogram
from loguru import logger

import prisma
from app.api.middlewares.base import middleware, SkipMiddleware
from app.dto.types import Handler, Json


class AuthMiddleware(aiogram.BaseMiddleware):
    @middleware
    async def __call__(
        self,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        if not isinstance(event, aiogram.types.Message):
            raise SkipMiddleware

        message: aiogram.types.Message = event
        user = message.from_user

        if not user:
            raise SkipMiddleware

        logger.info(f"new user registration | user_id: {user.id} | message: {message.text}")
        return await handler(event, data)


class CurrentUserMiddleware(aiogram.BaseMiddleware):
    """Middleware to fetch or create the current user from the database."""

    def __init__(self, db: prisma.Prisma) -> None:
        self._db = db

    @middleware
    async def __call__(
        self,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        if not isinstance(event, aiogram.types.Message | aiogram.types.CallbackQuery):
            raise SkipMiddleware

        if event.from_user is None:
            raise SkipMiddleware

        try:
            user = await self._db.user.find_first_or_raise(
                where={
                    "id": event.from_user.id,
                }
            )

        except prisma.errors.RecordNotFoundError:
            user = await self._db.user.create(
                data={
                    "id": event.from_user.id,
                    "name": event.from_user.full_name,
                }
            )
        data["user"] = user
        logger.warning(f"User {user=}")
        return await handler(event, data)
