import typing

import aiogram
import attrs


@typing.final
@attrs.define(slots=True, frozen=True, kw_only=True)
class TelegramBotService:
    _bot: aiogram.Bot
    _dp: aiogram.Dispatcher

    async def dispatch(self) -> None:
        await self._dp.start_polling(self._bot)
