from aiogram import Router
from app.handlers import start, menu


def setup_routers() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(menu.router)
    return router