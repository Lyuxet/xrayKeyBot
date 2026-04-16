from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.callbacks.profiles import ProfileCallback, UpdateKeysCallback, ConfirmUpdateKeys

def menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Показать все доступные профили", callback_data="show_profiles")],
        [InlineKeyboardButton(text="Пинг", callback_data="ping")]
    ])

def back_to_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="В меню", callback_data="menu")]
    ])


def buttons_profiles(name: str, uuid: str, has_keys: bool = True) -> InlineKeyboardMarkup:
    buttons = []
    if has_keys and uuid:
        buttons.append([
            InlineKeyboardButton(
                text="🔄 Обновить ключи",
                callback_data=ConfirmUpdateKeys(name=name, uuid=uuid).pack()   # ← теперь подтверждение
            )
        ])
    buttons.append([InlineKeyboardButton(text="← К профилям", callback_data="show_profiles")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def change_keys() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Обновить ключи", callback_data=UpdateKeysCallback())]
    ])


def confirm_change_keys(name: str, uuid: str) -> InlineKeyboardMarkup:
     return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Да, обновить",
                callback_data=UpdateKeysCallback(name=name, uuid=uuid).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data=ProfileCallback(name=name, uuid=uuid).pack()
            )
        ]
    ])
     
     

def generate_profiles_button(profiles_data: list[dict]) -> InlineKeyboardMarkup:
    rows = []

    for i in range(0, len(profiles_data), 2):
        row = []

        name1 = profiles_data[i]['name']
        uuid1 = profiles_data[i]['uuid']
        row.append(
            InlineKeyboardButton(
                text=name1,
                callback_data=ProfileCallback(name=name1, uuid=uuid1).pack()
            )
        )

        if i + 1 < len(profiles_data):
            name2 = profiles_data[i + 1]['name']
            uuid2 = profiles_data[i + 1]['uuid']

            row.append(
                InlineKeyboardButton(
                    text=name2,
                    callback_data=ProfileCallback(name=name2, uuid=uuid2).pack()
                )
            )

        rows.append(row)

    rows.append([InlineKeyboardButton(text="Меню", callback_data="menu")])

    return InlineKeyboardMarkup(inline_keyboard=rows)
