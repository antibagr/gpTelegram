import contextlib
import typing

import aiogram
import aiogram.client.default
import aiogram.client.session.aiohttp
import aiogram.fsm.storage.redis
import aiogram.utils.i18n.core
import redis.asyncio.client
from loguru import logger

import prisma
from app import logs
from app.api import routers
from app.api.middlewares.middlewares import register_middlewares
from app.service.bot import TelegramBotService
from app.settings import settings
from app.utils import serialization_kwargs

# Dependency level

db = prisma.Prisma(
    use_dotenv=True,
    log_queries=True,
    connect_timeout=settings.DB_TIMEOUT_SECONDS,
)

i18n = aiogram.utils.i18n.core.I18n(
    path=settings.LOCALES_DIR,
    default_locale="en",
    domain=settings.I18N_DOMAIN,
)

redis_client = redis.asyncio.client.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD.get_secret_value(),
    health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
)
redis_storage = aiogram.fsm.storage.redis.RedisStorage(
    redis=redis_client,
    key_builder=aiogram.fsm.storage.redis.DefaultKeyBuilder(
        with_bot_id=True,
    ),
    state_ttl=settings.REDIS_STATE_TTL,
    data_ttl=settings.REDIS_DATA_TTL,
    **serialization_kwargs,
)
event_isolation = aiogram.fsm.storage.redis.RedisEventIsolation(
    redis=redis_client,
)

telegram_bot_session = aiogram.client.session.aiohttp.AiohttpSession(
    **serialization_kwargs,
)
telegram_bot_default = aiogram.client.default.DefaultBotProperties(
    parse_mode=aiogram.enums.ParseMode.HTML,
)

dispatcher = aiogram.Dispatcher(
    storage=redis_storage,
    events_isolation=event_isolation,
    name=settings.TELEGRAM_BOT_NAME,
)
dispatcher.include_routers(*routers.routers)

bot = aiogram.Bot(
    token=settings.TELEGRAM_BOT_TOKEN.get_secret_value(),
    session=telegram_bot_session,
    default=telegram_bot_default,
)

# Service level

telegram_bot_service = TelegramBotService(
    bot=bot,
    dp=dispatcher,
)


async def startup() -> None:
    logs.setup_logging(debug=settings.DEBUG)
    logger.info("Starting up the application")
    if not await redis_client.ping():
        raise ConnectionError("Redis is not available")
    await db.connect(timeout=settings.DB_TIMEOUT_SECONDS)
    dispatcher["db"] = db
    register_middlewares(
        dp=dispatcher,
        db=db,
        i18n_instance=i18n,
        rate_limit=settings.RATE_LIMIT,
    )


async def shutdown() -> None:
    logger.info("Shutting down the application")
    await bot.session.close()
    await redis_client.close()
    await dispatcher.storage.close()
    await dispatcher.fsm.storage.close()
    await bot.session.close()
    await db.disconnect(timeout=settings.DB_TIMEOUT_SECONDS)
    logger.info("bot stopped")


@contextlib.asynccontextmanager
async def application_dependencies() -> typing.AsyncGenerator[None, None]:
    await startup()
    try:
        yield
    finally:
        await shutdown()
