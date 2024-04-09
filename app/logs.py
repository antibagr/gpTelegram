import contextlib
import contextvars
import datetime as dt
import decimal
import inspect
import json
import logging
import random
import sys
import typing
import uuid

from loguru import logger

if typing.TYPE_CHECKING:
    import loguru

    Message = loguru.Message
    LevelConfig = loguru.LevelConfig
else:
    Message = typing.Any
    LevelConfig = typing.Any

__all__ = ["set_new_operation_id", "setup_logging"]


class _InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # noqa: PLR6301
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def custom_serializer(obj: uuid.UUID | decimal.Decimal | typing.AnyStr) -> str:
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, decimal.Decimal):
        return f"{obj:f}"
    return str(obj)


operation_id: contextvars.ContextVar[int] = contextvars.ContextVar("operation_id")
_user_id: contextvars.ContextVar[uuid.UUID] = contextvars.ContextVar("user_id")


@contextlib.contextmanager
def user_id(value: uuid.UUID) -> typing.Generator[None, None, None]:
    token = _user_id.set(value)
    try:
        yield
    finally:
        _user_id.reset(token)


def set_new_operation_id() -> int:
    op_id = random.getrandbits(128)
    operation_id.set(op_id)
    return op_id


def _get_operation_id() -> int:
    op_id: int
    try:
        op_id = operation_id.get()
    except LookupError:
        op_id = set_new_operation_id()
    return op_id


def _serialize(record: dict[str, str | dt.datetime | int | LevelConfig]) -> tuple[str, bool]:
    err = False
    subset = {
        "timestamp": record["time"].isoformat(),  # type: ignore[union-attr]
        "level": record["level"].name,  # type: ignore[union-attr]
        "message": record["message"],
        "operation_id": str(_get_operation_id()),
        "extra": record["extra"],
    }

    if exc := record["exception"]:
        err = True
        subset["exception"] = exc

    if acc_id := _user_id.get(None):
        record["extra"]["user_id"] = acc_id  # type: ignore[index, typeddict-unknown-key]

    return f"{json.dumps(subset, default=custom_serializer)}\n", err


def _sink(message: Message) -> None:
    serialized, err = _serialize(message.record)  # type: ignore[arg-type]
    output = sys.stderr if err else sys.stdout
    output.write(serialized)


def setup_logging(*, debug: bool) -> None:  # noqa: ARG001
    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    _prisma = logging.getLogger("prisma")
    _prisma.addHandler(_InterceptHandler())
    _prisma.setLevel(logging.DEBUG)
