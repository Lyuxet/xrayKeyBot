from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, time


def seconds_until_next_msk(target_time: time) -> float:
    msk = ZoneInfo("Europe/Moscow")
    now = datetime.now(msk)

    next_run = now.replace(
        hour=target_time.hour,
        minute=target_time.minute,
        second=target_time.second,
        microsecond=0
    )
    if now >= next_run:
        next_run += timedelta(days=1)

    return (next_run - now).total_seconds()
