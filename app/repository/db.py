import contextlib
import datetime as dt
import typing

import prisma


@contextlib.asynccontextmanager
async def get_db(timeout: int) -> typing.AsyncGenerator[prisma.Prisma, None]:
    db = prisma.Prisma(
        use_dotenv=True,
        log_queries=True,
        connect_timeout=timeout,
    )
    try:
        await db.connect(timeout=dt.timedelta(seconds=timeout))
        yield db
    finally:
        await db.disconnect(timeout=dt.timedelta(seconds=timeout))
