"""
Модуль для запуска бота.
"""

import subprocess
import os

# Выполняем git pull
try:
    print("[INFO] Updating code from git...")
    subprocess.run(["git", "pull"], check=True)
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Failed to update code from git: {e}")

from bot_init import bot
from commands import general_commands, voice_commands
from config import DISCORD_TOKEN
from events import on_ready, on_voice, on_slash_command
from tasks import shutdown_timer

if __name__ == "__main__":
    if DISCORD_TOKEN == "NULL":
        print("[ERROR] Not DISCORD_KEY. Programm Dev-bot shutdown!!")
    else:
        bot.run(DISCORD_TOKEN)
