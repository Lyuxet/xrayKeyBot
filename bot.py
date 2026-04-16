import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from dotenv import load_dotenv
from typing import List
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import logging

from aiogram.types import CallbackQuery


from app.routers import setup_routers
from app.services.remna_client import RemnaClient
from app.config import loadConfig
from app.storage.profiles_store import get_profile_keys
from app.handlers.menu import rotate_profile_keys
from app.storage.profiles_store import set_profile

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OwnerOnlyMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: List[int]):
        self.allowed_user_ids = allowed_user_ids

    async def __call__(self, handler, event, data):
        bot: Bot = data["bot"]                   
        user = getattr(event, "from_user", None)

        if user is None:
            return
        
        if user.id not in self.allowed_user_ids:
            try:
                if isinstance(event, CallbackQuery):
                   
                    await event.answer("⛔ У вас нет доступа к этому боту.", show_alert=True)
                else:
                   
                    await bot.send_message(
                        chat_id=user.id,
                        text="⛔ У вас нет доступа к этому боту."
                    )
            except:
                pass  
            return  

        
        return await handler(event, data)
    
def seconds_until_next_msk_3am() -> float:
    msk = ZoneInfo("Europe/Moscow")
    now = datetime.now(msk)

    next_run = now.replace(hour=3, minute=0, second=0, microsecond=0)
    if now >= next_run:
        next_run += timedelta(days=1)

    return (next_run - now).total_seconds()



async def auto_rotate_keys_task(remna: RemnaClient):
    while True:
        try:
            sleep_seconds = seconds_until_next_msk_3am()
            next_run_at = datetime.now(ZoneInfo("Europe/Moscow")) + timedelta(seconds=sleep_seconds)

            logger.info(
                "Следующее автообновление ключей запланировано на %s MSK",
                next_run_at.strftime("%Y-%m-%d %H:%M:%S")
            )

            await asyncio.sleep(sleep_seconds)

            logger.info("Запуск автоматического обновления ключей в 03:00 MSK")

            profiles = await remna.list_profiles()
            if not profiles:
                logger.info("Профили не найдены")
                continue

            for p in profiles:
                uuid = p.get("uuid")
                name = p.get("name")
                config = p.get("config")

                if not uuid or not config:
                    logger.warning("Пропускаю профиль без uuid/config: %s", p)
                    continue

                set_profile(uuid, config)

                if not get_profile_keys(uuid):
                    logger.info("Пропускаю профиль %s: ключи не найдены в store", name)
                    continue

                try:
                    new_public_key, _ = await rotate_profile_keys(uuid, remna)
                    logger.info(
                        "Профиль %s успешно обновлён. Новый public key: %s",
                        name,
                        new_public_key
                    )
                except Exception as e:
                    logger.exception("Ошибка автообновления профиля %s: %s", name, e)

        except asyncio.CancelledError:
            logger.info("Фоновая задача автообновления остановлена")
            raise
        except Exception as e:
            logger.exception("Ошибка в фоновой задаче: %s", e)
            await asyncio.sleep(60)
    
async def main():
    config = loadConfig()
    bot = Bot(token=config.bot_token)
    dp = Dispatcher()

   
    mw = OwnerOnlyMiddleware(config.allowed_user_ids)

    dp.message.middleware(mw)
    dp.edited_message.middleware(mw)
    dp.callback_query.middleware(mw)
    dp.inline_query.middleware(mw)

    client = RemnaClient(base_url=config.remna_base_url, token=config.remna_token)
    await client.start()
    dp.workflow_data["remna"] = client

    dp.include_router(setup_routers())
    auto_task = asyncio.create_task(auto_rotate_keys_task(client))


    try:
        await dp.start_polling(bot)
    finally:
        auto_task.cancel()
        try:
            await auto_task
        except asyncio.CancelledError:
            pass
        await client.close()
       

if __name__ == "__main__":
    asyncio.run(main())