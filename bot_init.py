"""
Этот модуль инициализирует бота для работы с Discord.
Настроены необходимые параметры для запуска и обработки команд.
"""

import disnake
from disnake.ext import commands

from config import GUILD_ID

intents = disnake.Intents.all()
intents.message_content = True
intents.members = True
intents.voice_states = True
intents.guilds = True


bot = commands.Bot(
    command_prefix="!",
    help_command=None,
    intents=intents,
    sync_commands=True,
    test_guilds=[GUILD_ID]
)
