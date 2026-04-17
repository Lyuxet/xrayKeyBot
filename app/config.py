import os
from dataclasses import dataclass, field
from typing import List

@dataclass(frozen=True)
class Config:
    bot_token: str
    remna_base_url: str
    remna_token: str
    remna_timeout: int = 10
    allowed_user_ids: List[int] = field(default_factory=list)   # ← теперь список!


def loadConfig() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("Нет BOT_TOKEN в .env")

    remna_url = os.getenv("UTL_PANEL", "").strip().rstrip("/")
    remna_port = os.getenv("PORT_PANEL", "").strip()
    remna_token = os.getenv("API_TOKEN", "").strip()
    timeout = int(os.getenv("REMNA_TIMEOUT", "10"))

    if not remna_url or not remna_port or not remna_token:
        raise RuntimeError("Нет UTL_PANEL / PORT_PANEL / API_TOKEN в .env")

    allowed_str = os.getenv("ALLOWED_USER_IDS", "").strip()
    allowed_user_ids: List[int] = []
    
    if allowed_str:
        try:
            allowed_user_ids = [
                int(x.strip()) for x in allowed_str.split(",") if x.strip()
            ]
        except ValueError:
            raise RuntimeError("ALLOWED_USER_IDS должен содержать только числа через запятую")

    base_url = f"{remna_url}:{remna_port}"

    return Config(
        bot_token=bot_token,
        remna_base_url=base_url,
        remna_token=remna_token,
        remna_timeout=timeout,
        allowed_user_ids=allowed_user_ids,
    )