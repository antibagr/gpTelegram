import typing

import aiogram

Handler = typing.Callable[[aiogram.types.TelegramObject, dict[str, typing.Any]], typing.Awaitable[typing.Any]]
Json = dict[str, typing.Any]
