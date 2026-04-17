from app.services.remna_client import RemnaClient, RemnaApiError
from app.storage.profiles_store import (get_profile,
                                        delete_profile_keys,
                                        set_profile_keys,
                                        get_profile_keys,
                                        get_store_config,
                                        set_profile)
from app.domain.xray import generate_xray_keys
from app.domain.time import seconds_until_next_msk
from app.settings.flags import AutoRotateState



import logging
import asyncio
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

def update_config_inbounds(config: dict, private_key: str) -> bool:
    for inbound in config.get("inbounds", []):
        stream = inbound.get("streamSettings", {})
        if stream.get("security") == "reality":
            reality = stream.setdefault("realitySettings", {})
            if reality.get("privateKey"):
                reality["privateKey"] = private_key
                return True
    return False

def update_config_outbounds(config: dict, new_public_key: str, old_public_key: str) -> bool:
    for outbound in config.get("outbounds", []):
        stream = outbound.get("streamSettings", {})
        if stream.get("security") == "reality":
            reality = stream.setdefault("realitySettings", {})
            if reality.get("publicKey") == old_public_key:
                reality["publicKey"] = new_public_key
                return True
    return False

async def restore_configs(configs: dict, remna: RemnaClient):
    for sub_uuid, conf in configs.items():
        payload = {
            "config": conf,
            "uuid": sub_uuid
        }
        try:
            await remna.update_xray_keys_in_profile(payload)
        except RemnaApiError as e:
            logger.exception("Ошибка возврата профиля %s: %s", sub_uuid, e)



async def rotate_profile_keys(uuid: str, remna: RemnaClient) -> tuple[str, str]:
    config = get_profile(uuid)
    if not config:
        raise ValueError(f"Профиль {uuid} не найден в локальном хранилище")

    old_keys = get_profile_keys(uuid)
    if not old_keys:
        raise ValueError(f"Для профиля {uuid} не найдены текущие ключи")

    old_public_key, _ = next(iter(old_keys.items()))

    new_keys = generate_xray_keys()
    new_public_key, new_private_key = next(iter(new_keys.items()))

    configs = get_store_config()

    updated = update_config_inbounds(config, new_private_key)
    if not updated:
        raise ValueError(f"Reality inbound не найден в профиле {uuid}")

    try:
        for sub_uuid, conf in configs.items():
            sub_updated = update_config_outbounds(conf, new_public_key, old_public_key)
            if sub_updated:
                payload = {
                    "config": conf,
                    "uuid": sub_uuid
                }
                await remna.update_xray_keys_in_profile(payload)

        payload = {
            "config": config,
            "uuid": uuid
        }
        await remna.update_xray_keys_in_profile(payload)

    except RemnaApiError:
        await restore_configs(configs, remna)
        raise

    delete_profile_keys(uuid)
    set_profile_keys(uuid, new_keys)

    return new_public_key, new_private_key

async def auto_rotate_keys_task(remna: RemnaClient, state:AutoRotateState):
    while True:
        try:

            if not state.enabled:
                await asyncio.sleep(30)
                continue

            run_time = state.target_time
            sleep_seconds = seconds_until_next_msk(run_time)
    
            while sleep_seconds > 0:
                if not state.enabled:                                                                                                                                                                                                         
                    break  
                
                step = min(30, sleep_seconds)
                await asyncio.sleep(step)                                                                                                                                                                                                     
                sleep_seconds -= step    

            if not state.enabled:                                                                                                                                                                                                             
                  continue  

            logger.info("Запуск автоматического обновления ключей")

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
    