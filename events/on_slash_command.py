import asyncio
import functools

from disnake import AppCommandInteraction, Embed

from bot_init import bot
from modules.send_log_to_channel import log_to_channel


def log_slash_command(func):
    @functools.wraps(func)
    async def wrapper(interaction: AppCommandInteraction, *args, **kwargs):
        result = await func(interaction, *args, **kwargs)

        try:
            message = await interaction.original_message()
            message_url = f"https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{message.id}"
        except Exception:
            message_url = f"https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}"

        user = interaction.user
        guild = interaction.guild
        command_name = interaction.application_command.name
        options = interaction.data.get("options", [])

        args_str = ", ".join(f"{opt['name']}={opt['value']}" for opt in options) or "без аргументов"

        embed = Embed(
            title=f"Команда: /{command_name}",
            color=0x2f3136,
            timestamp=interaction.created_at,
        )
        embed.description = (
            f"👤 {user} (`{user.id}`)\n"
            f"📁 {guild.name if guild else 'DM'} / {interaction.channel.name if interaction.channel else 'N/A'}\n"
            f"📝 Аргументы: {args_str}\n"
            f"[Перейти к сообщению]({message_url})"
        )

        # Просто вызываем логирование — message передаём пустую строку, embed_obj — наш эмбед
        asyncio.create_task(log_to_channel(bot=bot, message="", embed_obj=embed, title="slash_command"))

        return result
    return wrapper
