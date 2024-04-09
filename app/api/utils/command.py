def is_command(message: str | None) -> bool:
    return bool(message and message.startswith("/"))


def find_command_argument(message: str | None) -> str | None:
    """Find command argument in message.

    Example:
    -------
        >>> find_command_argument("/start referrer")
        "referrer"
        >>> find_command_argument("/start")
        None
        >>> find_command_argument("hi! it's me")
        None

    """
    if not message or not is_command(message):
        return None

    return message.split()[1] if " " in message else None
