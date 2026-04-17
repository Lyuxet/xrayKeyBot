from aiogram import Router, F
from aiogram.types import CallbackQuery
import logging


from app.keyboards.inline import menu_kb, back_to_menu_kb, generate_profiles_button
from app.keyboards.inline import buttons_profiles, confirm_change_keys
from app.keyboards.inline import settings_func, settings_autoUpdateKeys
from app.services.remna_client import RemnaClient
from app.services.remna_client import RemnaApiError
from app.storage.profiles_store import set_keys, clear_keys
from app.storage.profiles_store import clear_profile_keys, set_profile_keys, get_profile_keys, set_profile
from app.storage.profiles_store import clear_store_config
from app.callbacks.profiles import ProfileCallback, UpdateKeysCallback, ConfirmUpdateKeys
from app.domain.xray import get_public_xray_key
from app.profiles.config import rotate_profile_keys



router = Router()
logger = logging.getLogger(__name__)



@router.callback_query(F.data == "menu")
async def cb_menu(call: CallbackQuery):
    await call.message.edit_text("Выбери:", reply_markup=menu_kb())
    await call.answer()

@router.callback_query(F.data == "show_profiles")
async def cb_show_profiles(call: CallbackQuery, remna: RemnaClient):
    await call.answer("Загружаю...")

    try:
        profiles = await remna.list_profiles()
    except RemnaApiError as e:
        await call.message.edit_text(f"Ошибка:\n{e}", reply_markup=back_to_menu_kb())
        await call.answer()
        return

    if not profiles:
        await call.message.edit_text("Профилей нет.", reply_markup=back_to_menu_kb())
        await call.answer()
        return
    
    profiles_data = []
    
    clear_profile_keys()
    clear_keys()
    clear_store_config()

    for p in profiles:
        name = p.get('name')
        uuid = p.get('uuid')
        profiles_data.append({"name": name, "uuid": uuid})

        config = p.get('config')
        set_profile(uuid, config)
        inbounds = config.get("inbounds", [])

        for inbound in inbounds:
            stream = inbound.get("streamSettings", {})
            if stream.get("security") == "reality":
                reality = stream.setdefault("realitySettings", {})
                private_key = reality["privateKey"]
                public_key = get_public_xray_key(private_key)

                set_keys(public_key, private_key)
                set_profile_keys(uuid, {public_key: private_key})

    text = "Доступные профили:\n\n" + "\n".join(
        f"🖥 {p['name']}"
        for p in profiles_data
    )

    await call.message.edit_text(text, reply_markup=generate_profiles_button(profiles_data))
    await call.answer()


@router.callback_query(ConfirmUpdateKeys.filter())
async def confirm_update_keys(call: CallbackQuery, callback_data: ConfirmUpdateKeys):
    name = callback_data.name
    uuid = callback_data.uuid
    
    text = (
        f"⚠️ **Внимание!**\n\n"
        f"Вы действительно хотите обновить Reality-ключи для профиля **{name}**?\n\n"
        f"Старые ключи будут заменены новыми."
    )
    
    await call.message.edit_text(text, reply_markup=confirm_change_keys(name, uuid), parse_mode="Markdown")
    await call.answer()




@router.callback_query(UpdateKeysCallback.filter())
async def cb_update_profile_keys(
    call: CallbackQuery,
    callback_data: UpdateKeysCallback,
    remna: RemnaClient
):
    name = callback_data.name
    uuid = callback_data.uuid

    await call.answer("Генерирую новые ключи...")

    try:
        new_public_key, new_private_key = await rotate_profile_keys(uuid, remna)
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка обновления:\n{e}")
        logger.exception(f"❌ Ошибка обновления:\n{e}")
        return

    text = (
        f"{name}\n\n"
        f"🔑PublicKey: {new_public_key}\n\n"
        f"🔑PrivateKey: {new_private_key}\n\n"
        f"✅ Ключи успешно обновлены на сервере!"
    )
    await call.message.edit_text(text, reply_markup=buttons_profiles(name, uuid))


@router.callback_query(F.data == "show_settings")
async def show_settings(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(text="Настройки:",reply_markup=settings_func())


@router.callback_query(F.data == "autoUpdateKeys")
async def show_settings_auto_update_keys(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text(text="Настройки автообновления ключей:", reply_markup=settings_autoUpdateKeys())


@router.callback_query(ProfileCallback.filter())
async def profile_actions(
    call: CallbackQuery, callback_data: ProfileCallback):
    name = callback_data.name
    uuid = callback_data.uuid

    keys = get_profile_keys(uuid)
    if not keys:
        await call.message.edit_text(f"{name}\n ❌Ключи не найдены", reply_markup=buttons_profiles(name, uuid, False))
        return

    public_key, private_key = next(iter(keys.items()))

    text = (
        f"{name}\n\n"
        f"🔑PublicKey: {public_key}\n\n"
        f"🔑PrivateKey: {private_key}"
    )
    await call.message.edit_text(f"{text}", reply_markup=buttons_profiles(name, uuid))
    