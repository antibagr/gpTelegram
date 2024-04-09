import aiogram
import aiogram.utils.callback_answer
import aiogram.utils.i18n.core

import prisma
from app.api.middlewares import (
    auth,
    logging,
    throttling,
)


def register_middlewares(
    dp: aiogram.Dispatcher,
    db: prisma.Prisma,
    i18n_instance: aiogram.utils.i18n.core.I18n,
    rate_limit: float,
) -> None:
    dp.update.outer_middleware(logging.LoggingMiddleware())
    dp.message.outer_middleware(throttling.ThrottlingMiddleware(rate_limit=rate_limit))
    dp.message.middleware(auth.CurrentUserMiddleware(db=db))

    dp.message.middleware(aiogram.utils.i18n.FSMI18nMiddleware(i18n=i18n_instance))

    dp.callback_query.middleware(aiogram.utils.i18n.FSMI18nMiddleware(i18n=i18n_instance))
    dp.inline_query.middleware(aiogram.utils.i18n.FSMI18nMiddleware(i18n=i18n_instance))

    dp.callback_query.middleware(aiogram.utils.callback_answer.CallbackAnswerMiddleware())
