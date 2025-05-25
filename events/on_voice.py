import random

import disnake

import data
from bot_init import bot
from modules.modal_window_voice import ChannelOptionsView
from modules.utils_data import save_data


@bot.event
async def on_voice_state_update(member, before, after):
    print(f"VOICE EVENT | {member} | {before.channel} → {after.channel}")
    if before.channel == after.channel:
        return

    guild = member.guild

    # === Удаление пустого старого канала, если это приватный ===
    if before.channel and before.channel.id in data.private_channels.values():
        if len(before.channel.members) == 0:
            print(f"Удаляю канал {before.channel.name} (ID {before.channel.id}) — пустой")
            await before.channel.delete()
            data.private_channels = {
                k: v for k, v in data.private_channels.items()
                if v != before.channel.id
            }
            await save_data()
            print("Канал удалён, словарь обновлён")

    # === Создание нового приватного канала, если вошёл в триггерный ===
    if after.channel and after.channel.id in data.trigger_channels:
        category = after.channel.category

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(view_channel=True, connect=True),
            member: disnake.PermissionOverwrite(view_channel=True, connect=True, manage_channels=True),
            guild.me: disnake.PermissionOverwrite(view_channel=True)
        }

        freq = f"{random.randint(60, 110)}.{random.randint(0, 9)}"
        tag = data.trigger_channels[after.channel.id]
        channel = await guild.create_voice_channel(
            name=f"Частота {tag}-{freq}: {member.display_name}",
            category=category,
            overwrites=overwrites,
            user_limit=5
        )

        data.private_channels[str(member.id)] = channel.id
        await member.move_to(channel)
        await save_data()

        # Находим текстовый канал для инструкции
        text_channel = guild.get_channel(after.channel.id)
        if not text_channel and category:
            for ch in category.channels:
                if isinstance(ch, disnake.TextChannel):
                    text_channel = ch
                    break

        if text_channel:
            embed = disnake.Embed(
                title="🎙 Управление приватным голосовым каналом",
                description=(
                    f"Привет, {member.mention}! Это твой приватный голосовой канал.\n\n"
                    "🔹 **Как управлять каналом:**\n"
                    "• Используй меню ниже для управления доступом и параметрами.\n"
                    "• Вы также можете использовать команду `/setting` для вызова такого же окна опций.\n"
                    "• Канал удалится автоматически, когда все покинут его.\n\n"
                    "Если нужна помощь — обратись к администрации."
                ),
                color=0x2f3136,
                timestamp=disnake.utils.utcnow()
            )
            embed.set_footer(text="Автоматически созданный канал")

            view = ChannelOptionsView(bot, member)
            await text_channel.send(embed=embed, view=view)
