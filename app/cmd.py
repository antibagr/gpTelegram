import asyncio
import functools
import signal
import types
import typing

import click
from loguru import logger

try:
    import uvloop
except ImportError:
    uvloop: types.ModuleType = asyncio  # type: ignore[no-redef]

from app.service.service import application_dependencies, telegram_bot_service

T = typing.TypeVar("T", bound=typing.Any)
P = typing.ParamSpec("P")
Coro = typing.Callable[P, typing.Coroutine[T, typing.Any, typing.Never]]


def coro(f: typing.Callable[P, T]) -> typing.Callable[P, T]:
    @functools.wraps(f)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        logger.info("run_cmd", command=f.__name__)
        with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
            return typing.cast(T, runner.run(f(*args, **kwargs)))

    return wrapper


@click.group()
def cli() -> None: ...


@cli.command()
@coro
async def dispatch() -> None:
    async with application_dependencies():
        await telegram_bot_service.dispatch()


def handle_exit_signal(_sig: int, _frame: types.FrameType | None) -> typing.NoReturn:
    raise SystemExit


signal.signal(signal.SIGINT, handle_exit_signal)
signal.signal(signal.SIGTERM, handle_exit_signal)

if __name__ == "__main__":
    cli()
