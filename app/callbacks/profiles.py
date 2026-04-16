from aiogram.filters.callback_data import CallbackData


class ProfileCallback(CallbackData, prefix="profile"):
    name: str
    uuid: str = ""

class UpdateKeysCallback(CallbackData, prefix="update_keys"):
    name: str
    uuid: str= ""
    

class ConfirmUpdateKeys(CallbackData, prefix="confirm_upd"):
    name: str
    uuid: str