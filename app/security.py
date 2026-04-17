from aiogram.types import CallbackQuery
from aiogram import Bot
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from typing import List


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
    
    