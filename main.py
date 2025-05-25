"""
Модуль для запуска бота.
"""

from bot_init import bot
from commands import general_commands, voice_commands
from config import DISCORD_TOKEN
from events import on_ready, on_voice
from tasks import shutdown_timer

if __name__ == "__main__":
    if DISCORD_TOKEN == "NULL":
        print("[ERROR] Not DISCORD_KEY. Programm Dev-bot shutdown!!")
    else:
        bot.run(DISCORD_TOKEN)
