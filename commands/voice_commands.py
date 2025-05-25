from disnake import Member, VoiceChannel
from disnake.ext import commands

import data
from bot_init import bot
from commands.utils import get_user_private_channel, has_any_role_by_keys
from modules.modal_window_voice import ChannelOptionsView
from modules.utils_data import save_data


@bot.slash_command(name="lock", description="Закрыть канал для других")
async def lock_channel(interaction):
    if interaction.author.voice and interaction.author.voice.channel.id in data.private_channels.values():
        channel = interaction.author.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=False)
        await interaction.send("🔒 Канал заблокирован!", ephemeral=True)
    else:
        await interaction.send("Вы не в своем приватном канале!", ephemeral=True)

@bot.slash_command(name="unlock", description="Открыть канал для других")
async def unlock_channel(interaction):
    if interaction.author.voice and interaction.author.voice.channel.id in data.private_channels.values():
        channel = interaction.author.voice.channel
        await channel.set_permissions(interaction.guild.default_role, connect=True)
        await interaction.send("🔓 Канал разблокирован!", ephemeral=True)
    else:
        await interaction.send("Вы не в своем приватном канале!", ephemeral=True)


# Слэш-команда для добавления триггер-канала
@bot.slash_command(description="Добавить триггер-канал для создания приватных каналов")
@has_any_role_by_keys("head_project")
async def add_trigger_channel(interaction, channel: VoiceChannel, tag: str):
    data.trigger_channels[channel.id] = tag
    await save_data() # Синхронизация при изменении data
    await interaction.response.send_message(f"Добавлен триггер-канал {channel.mention} с тегом '{tag}'")


# Слэш-команда для удаления триггер-канала
@bot.slash_command(description="Удалить триггер-канал")
@has_any_role_by_keys("head_project")
async def remove_trigger_channel(interaction, channel: VoiceChannel):
    if channel.id in data.trigger_channels:
        del data.trigger_channels[channel.id]
        await save_data() # Синхронизация при изменении data
        await interaction.response.send_message(f"Удалён триггер-канал {channel.mention}")
    else:
        await interaction.response.send_message(f"Канал {channel.mention} не является триггер-каналом")


# Можно командой вывести список триггер-каналов
@bot.slash_command(description="Показать список триггер-каналов")
async def list_trigger_channels(interaction):
    if not data.trigger_channels:
        await interaction.response.send_message("Триггер-каналы не настроены.")
        return
    msg = "Триггер-каналы:\n"
    for ch_id, tag in data.trigger_channels.items():
        msg += f"- <#{ch_id}> с тегом '{tag}'\n"
    await interaction.response.send_message(msg)


@bot.slash_command(name="name", description="Изменить имя голосового канала.")
async def change_name(interaction, name: str):
    await interaction.response.defer(ephemeral=True)  # говорим, что ответ будет позже
    channel = get_user_private_channel(interaction.author)
    if channel:
        try:
            await channel.edit(name=name)
            await interaction.followup.send(f"✅ Название канала изменено на: `{name}`", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Ошибка при изменении имени: {e}", ephemeral=True)
    else:
        await interaction.followup.send("❌ Вы не в своем приватном канале.", ephemeral=True)


@bot.slash_command(name="limit", description="Изменить лимит участников.")
async def change_limit(
    interaction,
    limit: int = commands.Param(default=0, description="0 — без лимита")
):
    if limit > 99:
        await interaction.response.send_message("❌ Лимит не может быть больше 99.", ephemeral=True)
        return

    channel = interaction.author.voice.channel if interaction.author.voice else None
    if channel and channel.id in data.private_channels.values():
        await channel.edit(user_limit=limit)
        await interaction.response.send_message(f"✅ Лимит участников установлен на: {limit}", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Вы не в своём приватном канале.", ephemeral=True)


@bot.slash_command(name="bitrate", description="Изменить битрейт канала.")
async def change_bitrate(
    interaction,
    bitrate: int = commands.Param(default=64000, description="Введите битрейт (минимум 8000, максимум зависит от буста сервера)")
):
    if bitrate < 8000:
        await interaction.response.send_message("❌ Минимальный битрейт — 8000.", ephemeral=True)
        return

    channel = get_user_private_channel(interaction.author)
    if channel:
        await channel.edit(bitrate=bitrate)
        await interaction.response.send_message("✅ Битрейт обновлён.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Вы не в своём приватном канале.", ephemeral=True)


# @bot.slash_command(name="claim", description="Стать владельцем текущего канала.")
# 
# async def claim_channel(interaction):
#     vc = interaction.author.voice.channel if interaction.author.voice else None
#     if vc and vc.id not in data.private_channels.values():
#         data.private_channels[interaction.author.id] = vc.id
#         await save_data()
#         await interaction.response.send_message("✅ Вы теперь владелец этого канала.", ephemeral=True)
#     else:
#         await interaction.response.send_message("❌ Невозможно стать владельцем: канал уже приватный или вы не в голосовом канале.", ephemeral=True)


@bot.slash_command(name="permit", description="Разрешить пользователю доступ к каналу.")
async def permit_user(interaction, member: Member):
    channel = get_user_private_channel(interaction.author)
    if channel:
        await channel.set_permissions(member, connect=True)
        await interaction.response.send_message(f"✅ {member.mention} получил доступ к каналу.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Вы не в своем приватном канале.", ephemeral=True)


@bot.slash_command(name="reject", description="Отклонить доступ пользователя (кик).")
async def reject_user(interaction, member: Member):
    channel = get_user_private_channel(interaction.author)
    if channel:
        await channel.set_permissions(member, overwrite=None)
        if member.voice and member.voice.channel == channel:
            await member.move_to(None)
        await interaction.response.send_message(f"⛔ {member.mention} удалён из канала и доступ закрыт.", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Вы не в своем приватном канале.", ephemeral=True)


@bot.slash_command(name="settings", description="Меню управления приватным каналом")
async def open_settings_menu(interaction):
    await interaction.response.send_message(
        "⚙️ Меню управления каналом:",
        view=ChannelOptionsView(bot, interaction.author),
        ephemeral=True
    )
