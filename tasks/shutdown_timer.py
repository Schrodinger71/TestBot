import asyncio
import sys
from datetime import datetime

from disnake.ext import tasks

from bot_init import bot
from config import LOG_TECH_CHANNEL, SHUTDOWN_TIMER
from modules.utils_data import save_data
from modules.utils_general import get_guild_status


async def shutdown_procces():
    await save_data()
    # Получаем канал для логов
    log_channel = bot.get_channel(LOG_TECH_CHANNEL)
    if log_channel:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = await get_guild_status()
        
        ascii_art = f"""
```diff
+-----------------------------------------------------+
| SCPINET BOTT {current_time}                    |
|                                                     |
-->> SYSTEM ⚠ WARNING                                 |
-->> RESTART IN 10 MINUTES                            |
|                                                     |
{status}           |
|                                                     |
-->> BOT SHUTDOWN COMPLETE                            |
-->> GOODBYE.                                         |
+-----------------------------------------------------+
```
"""
        await log_channel.send(ascii_art)

    await bot.close()
    sys.exit(0)
    

@tasks.loop(count=1)
async def shutdown_timer():
    await asyncio.sleep(SHUTDOWN_TIMER)
    await shutdown_procces()
