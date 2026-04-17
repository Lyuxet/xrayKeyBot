from dataclasses import dataclass, field
from datetime import time
from aiogram.fsm.state import State, StatesGroup

@dataclass
class AutoRotateState:
    enabled: bool = False
    target_time: time = field(default_factory=lambda: time(hour=0, minute=0))


class SettingsState(StatesGroup):                                                                                                                                                                                     
    waiting_auto_rotate_time = State() 