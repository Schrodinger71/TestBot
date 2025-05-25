from disnake import (MessageInteraction, ModalInteraction, SelectOption,
                     TextInputStyle)
from disnake.ui import Modal, Select, TextInput, UserSelect, View

from commands.utils import get_user_private_channel


class ChannelOptionsView(View):
    def __init__(self, bot, user):
        super().__init__(timeout=180)
        self.bot = bot
        self.user = user
        self.add_item(ChannelSettingsSelect(bot, user))

class ChannelSettingsSelect(Select):
    def __init__(self, bot, user):
        self.bot = bot
        self.user = user

        options = [
            SelectOption(label="🔒 Закрыть канал", value="lock", description="Запретить вход другим участникам"),
            SelectOption(label="🔓 Открыть канал", value="unlock", description="Разрешить вход другим участникам"),
            SelectOption(label="📝 Изменить имя", value="name", description="Задать новое имя канала"),
            SelectOption(label="👥 Изменить лимит", value="limit", description="Установить лимит участников"),
            SelectOption(label="🎚 Изменить битрейт", value="bitrate", description="Установить битрейт канала"),
            SelectOption(label="✅ Разрешить участнику", value="permit", description="Разрешить доступ пользователю"),
            SelectOption(label="⛔ Удалить участника", value="reject", description="Закрыть доступ пользователю и кикнуть"),
        ]

        super().__init__(
            placeholder="Выберите настройку...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="channel_settings_menu"
        )

    async def callback(self, interaction: MessageInteraction):
        channel = get_user_private_channel(interaction.author)
        if not channel:
            await interaction.response.send_message("❌ Вы не в своем приватном канале.", ephemeral=True)
            return

        value = self.values[0]

        if value == "lock":
            await interaction.response.defer(ephemeral=True)
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.followup.send("🔒 Канал закрыт для других.", ephemeral=True)

        elif value == "unlock":
            await interaction.response.defer(ephemeral=True)
            await channel.set_permissions(interaction.guild.default_role, connect=True)
            await interaction.followup.send("🔓 Канал открыт для других.", ephemeral=True)

        elif value == "name":
            await interaction.response.send_modal(NameChangeModal(channel.id))

        elif value == "limit":
            await interaction.response.send_modal(LimitChangeModal(channel.id))

        elif value == "bitrate":
            await interaction.response.send_modal(BitrateChangeModal(channel.id))

        elif value == "permit":
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Выберите пользователя для доступа:", ephemeral=True, view=PermitUserView(channel))

        elif value == "reject":
            await interaction.response.defer(ephemeral=True)
            await interaction.followup.send("Выберите пользователя для удаления:", ephemeral=True, view=RejectUserView(channel))

class PermitUserView(View):
    def __init__(self, channel):
        super().__init__(timeout=60)
        self.add_item(PermitUserSelect(channel))


class PermitUserSelect(UserSelect):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(placeholder="Выберите пользователя...", custom_id="permit_user_select")

    async def callback(self, interaction: MessageInteraction):
        member = self.values[0]
        await self.channel.set_permissions(member, connect=True)
        await interaction.response.send_message(f"✅ {member.mention} получил доступ к каналу.", ephemeral=True)


class RejectUserView(View):
    def __init__(self, channel):
        super().__init__(timeout=60)
        self.add_item(RejectUserSelect(channel))


class RejectUserSelect(UserSelect):
    def __init__(self, channel):
        self.channel = channel
        super().__init__(placeholder="Выберите пользователя...", custom_id="reject_user_select")

    async def callback(self, interaction: MessageInteraction):
        member = self.values[0]
        await self.channel.set_permissions(member, overwrite=None)
        if member.voice and member.voice.channel == self.channel:
            await member.move_to(None)
        await interaction.response.send_message(f"⛔ {member.mention} удалён из канала и доступ закрыт.", ephemeral=True)


class NameChangeModal(Modal):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        components = [
            TextInput(label="Новое имя канала", custom_id="name", style=TextInputStyle.short)
        ]
        super().__init__(title="Изменить имя канала", components=components)

    async def callback(self, interaction: ModalInteraction):
        channel = interaction.guild.get_channel(self.channel_id)
        name = interaction.text_values["name"].strip()
        await channel.edit(name=name)
        await interaction.response.send_message(f"📝 Имя канала изменено на: `{name}`", ephemeral=True)

class LimitChangeModal(Modal):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        components = [
            TextInput(label="Лимит участников (0 — без лимита)", custom_id="limit", style=TextInputStyle.short)
        ]
        super().__init__(title="Изменить лимит", components=components)

    async def callback(self, interaction: ModalInteraction):
        limit_str = interaction.text_values["limit"].strip()
        if not limit_str.isdigit():
            await interaction.response.send_message("❌ Лимит должен быть числом.", ephemeral=True)
            return
        limit = int(limit_str)
        if limit > 99:
            await interaction.response.send_message("❌ Лимит не может быть больше 99.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(self.channel_id)
        await channel.edit(user_limit=limit)
        await interaction.response.send_message(f"👥 Лимит установлен: {limit}", ephemeral=True)

class BitrateChangeModal(Modal):
    def __init__(self, channel_id):
        self.channel_id = channel_id
        components = [
            TextInput(label="Битрейт (8000–96000)", custom_id="bitrate", style=TextInputStyle.short)
        ]
        super().__init__(title="Изменить битрейт", components=components)

    async def callback(self, interaction: ModalInteraction):
        bitrate_str = interaction.text_values["bitrate"].strip()
        if not bitrate_str.isdigit():
            await interaction.response.send_message("❌ Битрейт должен быть числом.", ephemeral=True)
            return
        bitrate = int(bitrate_str)
        if not (8000 <= bitrate <= 96000):
            await interaction.response.send_message("❌ Битрейт должен быть от 8000 до 96000.", ephemeral=True)
            return
        channel = interaction.guild.get_channel(self.channel_id)
        await channel.edit(bitrate=bitrate)
        await interaction.response.send_message("🎚️ Битрейт обновлён.", ephemeral=True)
