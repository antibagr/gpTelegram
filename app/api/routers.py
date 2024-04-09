import aiogram

from .v1 import admin, navigation, start

routers: list[aiogram.Router] = [
    admin.router,
    start.router,
    navigation.router,
]
