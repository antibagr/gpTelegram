import aiogram

users_commands: dict[str, dict[str, str]] = {
    "en": {
        "help": "help",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "supports": "support contacts",
    },
    "uk": {
        "help": "help",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "supports": "support contacts",
    },
    "ru": {
        "help": "help",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "settings": "setting information about you",
        "supports": "support contacts",
    },
}

admins_commands: dict[str, dict[str, str]] = {
    **users_commands,
    "en": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
    "uk": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
    "ru": {
        "ping": "Check bot ping",
        "stats": "Show bot stats",
    },
}


async def set_default_commands(bot: aiogram.Bot) -> None:
    await remove_default_commands(bot)

    for language_code in users_commands:
        await bot.set_my_commands(
            [
                aiogram.types.BotCommand(command=command, description=description)
                for command, description in users_commands[language_code].items()
            ],
            scope=aiogram.types.BotCommandScopeDefault(),
        )


async def remove_default_commands(bot: aiogram.Bot) -> None:
    await bot.delete_my_commands(scope=aiogram.types.BotCommandScopeDefault())
