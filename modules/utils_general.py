from datetime import datetime

from disnake import TextChannel, VoiceChannel

import data
from bot_init import bot
from modules.send_log_to_channel import log_to_channel
from modules.utils_data import save_data


async def send_console_style_log(channel: TextChannel):
    """Отправляет стилизованное сообщение о запуске в лог-канал"""
    current_time = datetime.now().strftime("%d/%m/%Y %H:%M")

    ascii_art = f"""
```diff
+-----------------------------------------------------+
| SCPINET BOTT {current_time}                       |
|                                                     |
-->> SYSTEM BOOT SEQUENCE INITIATED                   |
-->> BOT CORE ONLINE                                  |
|                                                     |
{await get_guild_status()}           |
|                                                     |
-->> ALL SYSTEMS NOMINAL                              |
-->> AWAITING USER COMMANDS                           |
+-----------------------------------------------------+

test
```
"""
    await channel.send(ascii_art)


async def get_guild_status() -> str:
    """Форматирует информацию о серверах"""
    guilds = bot.guilds
    status = []
    for i, guild in enumerate(guilds[:3], 1):
        status.append(f"|  {i}. {guild.name:<25} [{len(guild.members):>3} users]")

    if len(guilds) > 3:
        status.append(f"|  ...and {len(guilds)-3} more servers")

    return "\n".join(status)

async def cleanup_empty_voice_channels(bot, guild_id: int):
    guild = bot.get_guild(guild_id)
    if not guild:
        print(f"❌ Guild с ID {guild_id} не найден")
        return

    print(f"🔍 Проверяем сервер: {guild.name} (ID: {guild.id})")

    checked_categories = set()
    for trigger_id in data.trigger_channels:
        trigger_id = int(trigger_id)  # ключи могут быть строками
        trigger_channel = guild.get_channel(trigger_id)
        if not isinstance(trigger_channel, VoiceChannel):
            print(f"⚠️ Триггер ID {trigger_id} не голосовой канал.")
            continue

        category = trigger_channel.category
        if not category or category.id in checked_categories:
            print(f"⚠️ Категория не найдена или уже проверялась: {category}")
            continue

        checked_categories.add(category.id)
        print(f"📂 Проверка категории: {category.name} (ID: {category.id})")

        for channel in category.voice_channels:
            print(f"🔍 Канал: {channel.name} (ID: {channel.id}), пользователей: {len(channel.members)}")

            if channel.id == trigger_channel.id:
                print(f"⛔ Пропущен триггер: {channel.name}")
                continue

            # Проверка только для приватных каналов
            if channel.id in data.private_channels.values():
                if len(channel.members) == 0:
                    message = f"[🧹] Удаляю ПУСТОЙ приватный канал: {channel.name} (ID {channel.id})"
                    print(message)
                    await log_to_channel(bot=bot, message=message, codeblock=False)
                    await channel.delete()

                    # Удаляем из словаря
                    for user_id, ch_id in list(data.private_channels.items()):
                        if ch_id == channel.id:
                            del data.private_channels[user_id]
                            break

                    await save_data()
                else:
                    print(f"⛔ Пропущен активный приватный: {channel.name}")
            else:
                print(f"✅ Пропущен вручную созданный или системный канал: {channel.name}")
