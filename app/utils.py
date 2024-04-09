import typing

import orjson


class _Kwargs(typing.TypedDict):
    json_loads: typing.Callable[[str], typing.Any]
    json_dumps: typing.Callable[[object], str]


class Json:
    """Json class to handle json serialization and deserialization.

    This class is a wrapper around orjson library to provide a consistent
    interface for json serialization and deserialization.
    """

    @staticmethod
    def dumps(
        __obj: object,
        default: typing.Callable[[typing.Any], typing.Any] | None = None,
        option: int | None = None,
    ) -> str:
        return orjson.dumps(__obj, default=default, option=option).decode("utf-8", errors="replace")

    loads: typing.Callable[[str], typing.Any] = orjson.loads


serialization_kwargs: typing.Final[_Kwargs] = {
    "json_loads": Json.loads,
    "json_dumps": Json.dumps,
}
