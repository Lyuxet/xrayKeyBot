import asyncio
import logging
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv


from app.routers import setup_routers
from app.services.remna_client import RemnaClient
from app.config import loadConfig
from app.storage.profiles_store import get_profile_keys
from app.storage.profiles_store import set_profile
from app.domain.time import seconds_until_next_msk
from app.profiles.config import auto_rotate_keys_task
from app.security import OwnerOnlyMiddleware
from app.settings.flags import AutoRotateState

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logging.getLogger("aiogram.event").disabled = True
logging.getLogger("aiogram.events").disabled = True

logger = logging.getLogger(__name__)

load_dotenv()
async def main():
    logger.info("Приложение запущено, читаем конфиг")
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

    auto_rotate_state = AutoRotateState(enabled=True)

    dp.workflow_data["remna"] = client
    dp.workflow_data["auto_rotate_state"] = auto_rotate_state

    dp.include_router(setup_routers())

    logger.info("Запускаем авто обновление ключей")
    auto_task = asyncio.create_task(auto_rotate_keys_task(client, auto_rotate_state))


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