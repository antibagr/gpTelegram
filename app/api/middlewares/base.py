__all__ = ["SkipMiddleware", "middleware"]

import functools
import typing

import aiogram

from app.dto.types import Handler, Json


class SkipMiddleware(Exception):  # noqa: N818
    """Middleware is skipped because it's not applicable to the current event."""


T = typing.TypeVar("T", bound=typing.Callable[..., typing.Awaitable[typing.Any]])


def middleware(func: T, /) -> T:
    """Decorate a middleware method to handle `SkipMiddleware` exception.
    The decorated middleware can raise `SkipMiddleware` to skip the middleware and
    proceed to the next one.

    Args:
    ----
        func (T): The middleware method to decorate.

    Returns:
    -------
        T: The decorated middleware method.

    """

    @functools.wraps(func)
    async def wrapper(
        self: aiogram.BaseMiddleware,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        try:
            return await func(self, handler, event, data)
        except SkipMiddleware:
            return await handler(event, data)

    return typing.cast(T, wrapper)
