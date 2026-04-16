STORE_CONFIG: dict[str, dict] = {}


def set_profile(uuid: str, config: dict) -> None:
    STORE_CONFIG[uuid] = config

def get_profile(uuid: str) -> dict | None:
    return STORE_CONFIG.get(uuid)

def delete_profile(uuid: str) -> bool:
    return STORE_CONFIG.pop(uuid, None) is not None

def list_uuid() -> list[str]:
    return list(STORE_CONFIG.keys())

def list_config() -> list[dict]:
    return list(STORE_CONFIG.values())

def get_store_config() -> dict[str, dict]:   # нижний регистр + snake_case
    return STORE_CONFIG.copy()

def clear_store_config():
    for key in list(STORE_CONFIG.keys()):
        del STORE_CONFIG[key]



STORE_KEYS: dict[str, str] = {}

def set_keys(public: str, private: str):
    STORE_KEYS[private] = public

def get_keys(private: str) -> str | None:
    return STORE_KEYS.get(private)

def delete_keys(private: str) -> bool:
    return STORE_KEYS.pop(private, None) is not None

def clear_keys():
    for key in list(STORE_KEYS.keys()):
        del STORE_KEYS[key]


STORE_PROFILE_KEYS: dict[str, dict[str, str]] = {}

def set_profile_keys(profile_name: str, keys: dict[str, str]):
    STORE_PROFILE_KEYS[profile_name] = keys

def get_profile_keys(profile_name: str) -> dict[str, str] | None:
    return STORE_PROFILE_KEYS.get(profile_name)

def delete_profile_keys(profile_name: str) -> bool:
    return STORE_PROFILE_KEYS.pop(profile_name, None) is not None

def clear_profile_keys():
    for key in list(STORE_PROFILE_KEYS.keys()):
        del STORE_PROFILE_KEYS[key]


 
